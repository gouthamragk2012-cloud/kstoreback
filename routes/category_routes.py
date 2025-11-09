from flask import Blueprint, request
from flask_jwt_extended import jwt_required
from db_connection import db
from utils.response_utils import success_response, error_response
from utils.auth_utils import admin_required

category_bp = Blueprint('categories', __name__)

@category_bp.route('', methods=['GET'])
def get_categories():
    conn = db.get_connection()
    cursor = conn.cursor()
    
    try:
        cursor.execute("""
            SELECT category_id, name, slug, description, parent_id, image_url, display_order
            FROM categories WHERE is_active = TRUE ORDER BY display_order, name
        """)
        
        categories = []
        for row in cursor.fetchall():
            categories.append({
                'category_id': row[0],
                'name': row[1],
                'slug': row[2],
                'description': row[3],
                'parent_id': row[4],
                'image_url': row[5],
                'display_order': row[6]
            })
        
        return success_response(categories)
        
    finally:
        cursor.close()
        db.return_connection(conn)

@category_bp.route('', methods=['POST'])
@jwt_required()
@admin_required()
def create_category():
    data = request.get_json()
    
    if not data.get('name') or not data.get('slug'):
        return error_response('Name and slug required')
    
    conn = db.get_connection()
    cursor = conn.cursor()
    
    try:
        cursor.execute("""
            INSERT INTO categories (name, slug, description, parent_id, image_url, display_order)
            VALUES (%s, %s, %s, %s, %s, %s)
            RETURNING category_id
        """, (data['name'], data['slug'], data.get('description'), 
              data.get('parent_id'), data.get('image_url'), data.get('display_order', 0)))
        
        category_id = cursor.fetchone()[0]
        conn.commit()
        
        return success_response({'category_id': category_id}, 'Category created', 201)
        
    except Exception as e:
        conn.rollback()
        return error_response(str(e), 500)
    finally:
        cursor.close()
        db.return_connection(conn)
