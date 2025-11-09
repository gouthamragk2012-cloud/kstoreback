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
