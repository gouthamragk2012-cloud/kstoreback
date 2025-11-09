from flask import Blueprint, request
from flask_jwt_extended import jwt_required, get_jwt_identity
from db_connection import db
from utils.response_utils import success_response, error_response, paginated_response
from utils.auth_utils import admin_required
import secrets

order_bp = Blueprint('orders', __name__)

def generate_order_number():
    return f"ORD-{secrets.token_hex(6).upper()}"

@order_bp.route('', methods=['POST'])
@jwt_required()
def create_order():
    user_id = get_jwt_identity()
    data = request.get_json()
    
    if not data.get('shipping_address_id'):
        return error_response('Shipping address required')
    
    conn = db.get_connection()
    cursor = conn.cursor()
    
    try:
        # Get cart items
        cursor.execute("""
            SELECT c.product_id, c.variant_id, c.quantity, p.name, p.sku, p.price, p.stock_quantity,
                   pv.price as variant_price, pv.sku as variant_sku
            FROM cart c
            JOIN products p ON c.product_id = p.product_id
            LEFT JOIN product_variants pv ON c.variant_id = pv.variant_id
            WHERE c.user_id = %s
        """, (user_id,))
        
        cart_items = cursor.fetchall()
        
        if not cart_items:
            return error_response('Cart is empty')
        
        # Calculate totals
        subtotal = 0
        for item in cart_items:
            price = float(item[7]) if item[7] else float(item[5])
            subtotal += price * item[2]
        
        shipping_cost = data.get('shipping_cost', 0)
        tax_amount = data.get('tax_amount', 0)
        discount_amount = data.get('discount_amount', 0)
        total_amount = subtotal + shipping_cost + tax_amount - discount_amount
        
        # Create order
        order_number = generate_order_number()
        cursor.execute("""
            INSERT INTO orders (order_number, user_id, subtotal, tax_amount, shipping_cost,
                              discount_amount, total_amount, shipping_address_id, 
                              billing_address_id, payment_method, shipping_method)
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
            RETURNING order_id
        """, (order_number, user_id, subtotal, tax_amount, shipping_cost, discount_amount,
              total_amount, data['shipping_address_id'], data.get('billing_address_id'),
              data.get('payment_method'), data.get('shipping_method')))
        
        order_id = cursor.fetchone()[0]
        
        # Create order items
        for item in cart_items:
            price = float(item[7]) if item[7] else float(item[5])
            sku = item[8] if item[8] else item[4]
            
            cursor.execute("""
                INSERT INTO order_items (order_id, product_id, variant_id, product_name, 
                                       sku, quantity, unit_price, total_price)
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
            """, (order_id, item[0], item[1], item[3], sku, item[2], price, price * item[2]))
            
            # Update stock
            if item[1]:  # Has variant
                cursor.execute("""
                    UPDATE product_variants SET stock_quantity = stock_quantity - %s
                    WHERE variant_id = %s
                """, (item[2], item[1]))
            else:
                cursor.execute("""
                    UPDATE products SET stock_quantity = stock_quantity - %s
                    WHERE product_id = %s
                """, (item[2], item[0]))
        
        # Clear cart
        cursor.execute("DELETE FROM cart WHERE user_id = %s", (user_id,))
        
        # Add status history
        cursor.execute("""
            INSERT INTO order_status_history (order_id, status, notes, created_by)
            VALUES (%s, %s, %s, %s)
        """, (order_id, 'pending', 'Order created', user_id))
        
        conn.commit()
        
        return success_response({
            'order_id': order_id,
            'order_number': order_number,
            'total_amount': float(total_amount)
        }, 'Order created successfully', 201)
        
    except Exception as e:
        conn.rollback()
        return error_response(str(e), 500)
    finally:
        cursor.close()
        db.return_connection(conn)

@order_bp.route('', methods=['GET'])
@jwt_required()
def get_orders():
    user_id = get_jwt_identity()
    page = int(request.args.get('page', 1))
    per_page = int(request.args.get('per_page', 10))
    offset = (page - 1) * per_page
    
    conn = db.get_connection()
    cursor = conn.cursor()
    
    try:
        cursor.execute("SELECT COUNT(*) FROM orders WHERE user_id = %s", (user_id,))
        total = cursor.fetchone()[0]
        
        cursor.execute("""
            SELECT order_id, order_number, total_amount, status, payment_status, created_at
            FROM orders WHERE user_id = %s
            ORDER BY created_at DESC
            LIMIT %s OFFSET %s
        """, (user_id, per_page, offset))
        
        orders = []
        for row in cursor.fetchall():
            orders.append({
                'order_id': row[0],
                'order_number': row[1],
                'total_amount': float(row[2]),
                'status': row[3],
                'payment_status': row[4],
                'created_at': row[5].isoformat()
            })
        
        return paginated_response(orders, page, per_page, total)
        
    finally:
        cursor.close()
        db.return_connection(conn)

@order_bp.route('/<int:order_id>', methods=['GET'])
@jwt_required()
def get_order(order_id):
    user_id = get_jwt_identity()
    
    conn = db.get_connection()
    cursor = conn.cursor()
    
    try:
        cursor.execute("""
            SELECT o.order_id, o.order_number, o.subtotal, o.tax_amount, o.shipping_cost,
                   o.discount_amount, o.total_amount, o.status, o.payment_status, 
                   o.payment_method, o.tracking_number, o.created_at,
                   a.full_name, a.address_line1, a.address_line2, a.city, a.state, 
                   a.postal_code, a.country, a.phone
            FROM orders o
            LEFT JOIN addresses a ON o.shipping_address_id = a.address_id
            WHERE o.order_id = %s AND o.user_id = %s
        """, (order_id, user_id))
        
        order = cursor.fetchone()
        if not order:
            return error_response('Order not found', 404)
        
        # Get order items
        cursor.execute("""
            SELECT product_name, sku, quantity, unit_price, total_price
            FROM order_items WHERE order_id = %s
        """, (order_id,))
        
        items = [{'product_name': r[0], 'sku': r[1], 'quantity': r[2],
                  'unit_price': float(r[3]), 'total_price': float(r[4])} 
                 for r in cursor.fetchall()]
        
        order_data = {
            'order_id': order[0],
            'order_number': order[1],
            'subtotal': float(order[2]),
            'tax_amount': float(order[3]),
            'shipping_cost': float(order[4]),
            'discount_amount': float(order[5]),
            'total_amount': float(order[6]),
            'status': order[7],
            'payment_status': order[8],
            'payment_method': order[9],
            'tracking_number': order[10],
            'created_at': order[11].isoformat(),
            'shipping_address': {
                'full_name': order[12],
                'address_line1': order[13],
                'address_line2': order[14],
                'city': order[15],
                'state': order[16],
                'postal_code': order[17],
                'country': order[18],
                'phone': order[19]
            } if order[12] else None,
            'items': items
        }
        
        return success_response(order_data)
        
    finally:
        cursor.close()
        db.return_connection(conn)

# Admin routes
@order_bp.route('/admin/all', methods=['GET'])
@admin_required()
def get_all_orders():
    page = int(request.args.get('page', 1))
    per_page = int(request.args.get('per_page', 20))
    offset = (page - 1) * per_page
    status_filter = request.args.get('status')
    
    conn = db.get_connection()
    cursor = conn.cursor()
    
    try:
        # Build query with optional status filter
        where_clause = ""
        params = []
        if status_filter:
            where_clause = "WHERE o.status = %s"
            params.append(status_filter)
        
        # Get total count
        cursor.execute(f"SELECT COUNT(*) FROM orders o {where_clause}", params)
        total = cursor.fetchone()[0]
        
        # Get orders with user info
        query = f"""
            SELECT o.order_id, o.order_number, o.total_amount, o.status, o.payment_status,
                   o.tracking_number, o.created_at, u.first_name, u.last_name, u.email,
                   a.full_name, a.city, a.state, a.country, a.phone
            FROM orders o
            JOIN users u ON o.user_id = u.user_id
            LEFT JOIN addresses a ON o.shipping_address_id = a.address_id
            {where_clause}
            ORDER BY o.created_at DESC
            LIMIT %s OFFSET %s
        """
        params.extend([per_page, offset])
        cursor.execute(query, params)
        
        orders = []
        for row in cursor.fetchall():
            orders.append({
                'order_id': row[0],
                'order_number': row[1],
                'total_amount': float(row[2]),
                'status': row[3],
                'payment_status': row[4],
                'tracking_number': row[5],
                'created_at': row[6].isoformat(),
                'customer': {
                    'first_name': row[7],
                    'last_name': row[8],
                    'email': row[9]
                },
                'shipping_address': {
                    'full_name': row[10],
                    'city': row[11],
                    'state': row[12],
                    'country': row[13],
                    'phone': row[14]
                } if row[10] else None
            })
        
        return paginated_response(orders, page, per_page, total)
        
    finally:
        cursor.close()
        db.return_connection(conn)

@order_bp.route('/admin/<int:order_id>', methods=['GET'])
@admin_required()
def get_order_admin(order_id):
    conn = db.get_connection()
    cursor = conn.cursor()
    
    try:
        cursor.execute("""
            SELECT o.order_id, o.order_number, o.subtotal, o.tax_amount, o.shipping_cost,
                   o.discount_amount, o.total_amount, o.status, o.payment_status, 
                   o.payment_method, o.tracking_number, o.shipping_method, o.created_at,
                   u.user_id, u.first_name, u.last_name, u.email, u.phone,
                   a.full_name, a.address_line1, a.address_line2, a.city, a.state, 
                   a.postal_code, a.country, a.phone as shipping_phone
            FROM orders o
            JOIN users u ON o.user_id = u.user_id
            LEFT JOIN addresses a ON o.shipping_address_id = a.address_id
            WHERE o.order_id = %s
        """, (order_id,))
        
        order = cursor.fetchone()
        if not order:
            return error_response('Order not found', 404)
        
        # Get order items
        cursor.execute("""
            SELECT product_id, product_name, sku, quantity, unit_price, total_price
            FROM order_items WHERE order_id = %s
        """, (order_id,))
        
        items = [{'product_id': r[0], 'product_name': r[1], 'sku': r[2], 'quantity': r[3],
                  'unit_price': float(r[4]), 'total_price': float(r[5])} 
                 for r in cursor.fetchall()]
        
        # Get status history
        cursor.execute("""
            SELECT status, notes, created_at, created_by
            FROM order_status_history
            WHERE order_id = %s
            ORDER BY created_at DESC
        """, (order_id,))
        
        status_history = [{'status': r[0], 'notes': r[1], 'created_at': r[2].isoformat(),
                          'created_by': r[3]} for r in cursor.fetchall()]
        
        order_data = {
            'order_id': order[0],
            'order_number': order[1],
            'subtotal': float(order[2]),
            'tax_amount': float(order[3]),
            'shipping_cost': float(order[4]),
            'discount_amount': float(order[5]),
            'total_amount': float(order[6]),
            'status': order[7],
            'payment_status': order[8],
            'payment_method': order[9],
            'tracking_number': order[10],
            'shipping_method': order[11],
            'created_at': order[12].isoformat(),
            'customer': {
                'user_id': order[13],
                'first_name': order[14],
                'last_name': order[15],
                'email': order[16],
                'phone': order[17]
            },
            'shipping_address': {
                'full_name': order[18],
                'address_line1': order[19],
                'address_line2': order[20],
                'city': order[21],
                'state': order[22],
                'postal_code': order[23],
                'country': order[24],
                'phone': order[25]
            } if order[18] else None,
            'items': items,
            'status_history': status_history
        }
        
        return success_response(order_data)
        
    finally:
        cursor.close()
        db.return_connection(conn)

@order_bp.route('/admin/<int:order_id>/status', methods=['PUT'])
@admin_required()
def update_order_status(order_id):
    admin_id = get_jwt_identity()
    data = request.get_json()
    
    if not data.get('status'):
        return error_response('Status is required')
    
    valid_statuses = ['pending', 'processing', 'shipped', 'delivered', 'cancelled']
    if data['status'] not in valid_statuses:
        return error_response(f'Invalid status. Must be one of: {", ".join(valid_statuses)}')
    
    conn = db.get_connection()
    cursor = conn.cursor()
    
    try:
        # Check if order exists
        cursor.execute("SELECT order_id FROM orders WHERE order_id = %s", (order_id,))
        if not cursor.fetchone():
            return error_response('Order not found', 404)
        
        # Update order status
        cursor.execute("""
            UPDATE orders SET status = %s, updated_at = CURRENT_TIMESTAMP
            WHERE order_id = %s
        """, (data['status'], order_id))
        
        # Add to status history
        cursor.execute("""
            INSERT INTO order_status_history (order_id, status, notes, created_by)
            VALUES (%s, %s, %s, %s)
        """, (order_id, data['status'], data.get('notes', ''), admin_id))
        
        conn.commit()
        
        return success_response({'order_id': order_id, 'status': data['status']}, 
                              'Order status updated successfully')
        
    except Exception as e:
        conn.rollback()
        return error_response(str(e), 500)
    finally:
        cursor.close()
        db.return_connection(conn)

@order_bp.route('/admin/<int:order_id>/tracking', methods=['PUT'])
@admin_required()
def update_tracking_number(order_id):
    data = request.get_json()
    
    if not data.get('tracking_number'):
        return error_response('Tracking number is required')
    
    conn = db.get_connection()
    cursor = conn.cursor()
    
    try:
        # Check if order exists
        cursor.execute("SELECT order_id FROM orders WHERE order_id = %s", (order_id,))
        if not cursor.fetchone():
            return error_response('Order not found', 404)
        
        # Update tracking number
        cursor.execute("""
            UPDATE orders SET tracking_number = %s, updated_at = CURRENT_TIMESTAMP
            WHERE order_id = %s
        """, (data['tracking_number'], order_id))
        
        conn.commit()
        
        return success_response({'order_id': order_id, 'tracking_number': data['tracking_number']}, 
                              'Tracking number updated successfully')
        
    except Exception as e:
        conn.rollback()
        return error_response(str(e), 500)
    finally:
        cursor.close()
        db.return_connection(conn)
