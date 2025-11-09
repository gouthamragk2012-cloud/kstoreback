from flask import Blueprint, request
from flask_jwt_extended import jwt_required, get_jwt_identity
from db_connection import db
from utils.response_utils import success_response, error_response

cart_bp = Blueprint('cart', __name__)

@cart_bp.route('', methods=['GET'])
@jwt_required()
def get_cart():
    user_id = get_jwt_identity()
    
    conn = db.get_connection()
    cursor = conn.cursor()
    
    try:
        cursor.execute("""
            SELECT c.cart_id, c.product_id, c.variant_id, c.quantity,
                   p.name, p.price, p.stock_quantity, p.slug,
                   (SELECT image_url FROM product_images WHERE product_id = p.product_id 
                    AND is_primary = TRUE LIMIT 1) as image_url,
                   pv.name as variant_name, pv.price as variant_price
            FROM cart c
            JOIN products p ON c.product_id = p.product_id
            LEFT JOIN product_variants pv ON c.variant_id = pv.variant_id
            WHERE c.user_id = %s
        """, (user_id,))
        
        items = []
        total = 0
        
        for row in cursor.fetchall():
            price = float(row[10]) if row[10] else float(row[5])
            item_total = price * row[3]
            total += item_total
            
            items.append({
                'cart_id': row[0],
                'product_id': row[1],
                'variant_id': row[2],
                'quantity': row[3],
                'product_name': row[4],
                'price': price,
                'stock_quantity': row[6],
                'slug': row[7],
                'image_url': row[8],
                'variant_name': row[9],
                'item_total': item_total
            })
        
        return success_response({'items': items, 'total': total})
        
    finally:
        cursor.close()
        db.return_connection(conn)

@cart_bp.route('', methods=['POST'])
@jwt_required()
def add_to_cart():
    user_id = get_jwt_identity()
    data = request.get_json()
    
    if not data.get('product_id'):
        return error_response('Product ID required')
    
    conn = db.get_connection()
    cursor = conn.cursor()
    
    try:
        # Check if item exists
        cursor.execute("""
            SELECT cart_id, quantity FROM cart 
            WHERE user_id = %s AND product_id = %s AND 
                  (variant_id = %s OR (variant_id IS NULL AND %s IS NULL))
        """, (user_id, data['product_id'], data.get('variant_id'), data.get('variant_id')))
        
        existing = cursor.fetchone()
        
        if existing:
            # Update quantity
            new_quantity = existing[1] + data.get('quantity', 1)
            cursor.execute("""
                UPDATE cart SET quantity = %s, updated_at = CURRENT_TIMESTAMP
                WHERE cart_id = %s
            """, (new_quantity, existing[0]))
        else:
            # Insert new
            cursor.execute("""
                INSERT INTO cart (user_id, product_id, variant_id, quantity)
                VALUES (%s, %s, %s, %s)
            """, (user_id, data['product_id'], data.get('variant_id'), data.get('quantity', 1)))
        
        conn.commit()
        return success_response(message='Item added to cart')
        
    except Exception as e:
        conn.rollback()
        return error_response(str(e), 500)
    finally:
        cursor.close()
        db.return_connection(conn)

@cart_bp.route('/<int:cart_id>', methods=['PUT'])
@jwt_required()
def update_cart_item(cart_id):
    user_id = get_jwt_identity()
    data = request.get_json()
    
    if not data.get('quantity'):
        return error_response('Quantity required')
    
    conn = db.get_connection()
    cursor = conn.cursor()
    
    try:
        cursor.execute("""
            UPDATE cart SET quantity = %s, updated_at = CURRENT_TIMESTAMP
            WHERE cart_id = %s AND user_id = %s
        """, (data['quantity'], cart_id, user_id))
        
        conn.commit()
        return success_response(message='Cart updated')
        
    except Exception as e:
        conn.rollback()
        return error_response(str(e), 500)
    finally:
        cursor.close()
        db.return_connection(conn)

@cart_bp.route('/<int:cart_id>', methods=['DELETE'])
@jwt_required()
def remove_from_cart(cart_id):
    user_id = get_jwt_identity()
    
    conn = db.get_connection()
    cursor = conn.cursor()
    
    try:
        cursor.execute("DELETE FROM cart WHERE cart_id = %s AND user_id = %s", (cart_id, user_id))
        conn.commit()
        return success_response(message='Item removed from cart')
        
    finally:
        cursor.close()
        db.return_connection(conn)

@cart_bp.route('/clear', methods=['DELETE'])
@jwt_required()
def clear_cart():
    user_id = get_jwt_identity()
    
    conn = db.get_connection()
    cursor = conn.cursor()
    
    try:
        cursor.execute("DELETE FROM cart WHERE user_id = %s", (user_id,))
        conn.commit()
        return success_response(message='Cart cleared')
        
    finally:
        cursor.close()
        db.return_connection(conn)
