from flask import Blueprint, request
from flask_jwt_extended import jwt_required, get_jwt_identity
from db_connection import db
from utils.response_utils import success_response, error_response

review_bp = Blueprint('reviews', __name__)

@review_bp.route('/product/<int:product_id>', methods=['GET'])
def get_product_reviews(product_id):
    conn = db.get_connection()
    cursor = conn.cursor()
    
    try:
        cursor.execute("""
            SELECT r.review_id, r.rating, r.title, r.comment, r.is_verified_purchase,
                   r.helpful_count, r.created_at,
                   u.first_name, u.last_name
            FROM reviews r
            LEFT JOIN users u ON r.user_id = u.user_id
            WHERE r.product_id = %s AND r.is_approved = TRUE
            ORDER BY r.created_at DESC
        """, (product_id,))
        
        reviews = []
        for row in cursor.fetchall():
            reviews.append({
                'review_id': row[0],
                'rating': row[1],
                'title': row[2],
                'comment': row[3],
                'is_verified_purchase': row[4],
                'helpful_count': row[5],
                'created_at': row[6].isoformat(),
                'reviewer_name': f"{row[7]} {row[8][0]}." if row[7] else "Anonymous"
            })
        
        return success_response(reviews)
        
    finally:
        cursor.close()
        db.return_connection(conn)

@review_bp.route('', methods=['POST'])
@jwt_required()
def create_review():
    user_id = get_jwt_identity()
    data = request.get_json()
    
    required = ['product_id', 'rating']
    if not all(field in data for field in required):
        return error_response('Product ID and rating required')
    
    if not 1 <= data['rating'] <= 5:
        return error_response('Rating must be between 1 and 5')
    
    conn = db.get_connection()
    cursor = conn.cursor()
    
    try:
        # Check if user purchased the product
        cursor.execute("""
            SELECT 1 FROM order_items oi
            JOIN orders o ON oi.order_id = o.order_id
            WHERE o.user_id = %s AND oi.product_id = %s
        """, (user_id, data['product_id']))
        
        is_verified = cursor.fetchone() is not None
        
        cursor.execute("""
            INSERT INTO reviews (product_id, user_id, order_id, rating, title, comment, 
                               is_verified_purchase)
            VALUES (%s, %s, %s, %s, %s, %s, %s)
            RETURNING review_id
        """, (data['product_id'], user_id, data.get('order_id'), data['rating'],
              data.get('title'), data.get('comment'), is_verified))
        
        review_id = cursor.fetchone()[0]
        conn.commit()
        
        return success_response({'review_id': review_id}, 'Review submitted', 201)
        
    except Exception as e:
        conn.rollback()
        return error_response(str(e), 500)
    finally:
        cursor.close()
        db.return_connection(conn)
