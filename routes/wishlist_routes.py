from flask import Blueprint
from flask_jwt_extended import jwt_required, get_jwt_identity
from db_connection import db
from utils.response_utils import success_response, error_response

wishlist_bp = Blueprint('wishlist', __name__)

@wishlist_bp.route('', methods=['GET'])
@jwt_required()
def get_wishlist():
    user_id = get_jwt_identity()
    
    conn = db.get_connection()
    cursor = conn.cursor()
    
    try:
        cursor.execute("""
            SELECT w.wishlist_id, w.product_id, p.name, p.slug, p.price, p.stock_quantity,
                   (SELECT image_url FROM product_images WHERE product_id = p.product_id 
                    AND is_primary = TRUE LIMIT 1) as image_url
            FROM wishlist w
            JOIN products p ON w.product_id = p.product_id
            WHERE w.user_id = %s AND p.is_active = TRUE
            ORDER BY w.created_at DESC
        """, (user_id,))
        
        items = []
        for row in cursor.fetchall():
            items.append({
                'wishlist_id': row[0],
                'product_id': row[1],
                'name': row[2],
                'slug': row[3],
                'price': float(row[4]),
                'stock_quantity': row[5],
                'image_url': row[6]
            })
        
        return success_response(items)
        
    finally:
        cursor.close()
        db.return_connection(conn)

@wishlist_bp.route('/<int:product_id>', methods=['POST'])
@jwt_required()
def add_to_wishlist(product_id):
    user_id = get_jwt_identity()
    
    conn = db.get_connection()
    cursor = conn.cursor()
    
    try:
        cursor.execute("""
            INSERT INTO wishlist (user_id, product_id)
            VALUES (%s, %s)
            ON CONFLICT (user_id, product_id) DO NOTHING
        """, (user_id, product_id))
        
        conn.commit()
        return success_response(message='Added to wishlist')
        
    except Exception as e:
        conn.rollback()
        return error_response(str(e), 500)
    finally:
        cursor.close()
        db.return_connection(conn)

@wishlist_bp.route('/<int:product_id>', methods=['DELETE'])
@jwt_required()
def remove_from_wishlist(product_id):
    user_id = get_jwt_identity()
    
    conn = db.get_connection()
    cursor = conn.cursor()
    
    try:
        cursor.execute("""
            DELETE FROM wishlist WHERE user_id = %s AND product_id = %s
        """, (user_id, product_id))
        
        conn.commit()
        return success_response(message='Removed from wishlist')
        
    finally:
        cursor.close()
        db.return_connection(conn)
