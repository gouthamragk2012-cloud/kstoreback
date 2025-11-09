from flask import Blueprint, request
from flask_jwt_extended import jwt_required, get_jwt_identity
from db_connection import db
from utils.response_utils import success_response, error_response
from utils.auth_utils import admin_required

user_bp = Blueprint('users', __name__)

@user_bp.route('/profile', methods=['PUT'])
@jwt_required()
def update_profile():
    user_id = get_jwt_identity()
    data = request.get_json()
    
    conn = db.get_connection()
    cursor = conn.cursor()
    
    try:
        cursor.execute("""
            UPDATE users 
            SET first_name = COALESCE(%s, first_name),
                last_name = COALESCE(%s, last_name),
                phone = COALESCE(%s, phone),
                updated_at = CURRENT_TIMESTAMP
            WHERE user_id = %s
            RETURNING user_id, email, first_name, last_name, phone
        """, (data.get('first_name'), data.get('last_name'), data.get('phone'), user_id))
        
        user = cursor.fetchone()
        conn.commit()
        
        return success_response({
            'user_id': user[0],
            'email': user[1],
            'first_name': user[2],
            'last_name': user[3],
            'phone': user[4]
        }, 'Profile updated')
        
    except Exception as e:
        conn.rollback()
        return error_response(str(e), 500)
    finally:
        cursor.close()
        db.return_connection(conn)

@user_bp.route('/addresses', methods=['GET'])
@jwt_required()
def get_addresses():
    user_id = get_jwt_identity()
    
    conn = db.get_connection()
    cursor = conn.cursor()
    
    try:
        cursor.execute("""
            SELECT address_id, address_type, full_name, phone, address_line1, address_line2,
                   city, state, postal_code, country, is_default
            FROM addresses WHERE user_id = %s ORDER BY is_default DESC, created_at DESC
        """, (user_id,))
        
        addresses = []
        for row in cursor.fetchall():
            addresses.append({
                'address_id': row[0],
                'address_type': row[1],
                'full_name': row[2],
                'phone': row[3],
                'address_line1': row[4],
                'address_line2': row[5],
                'city': row[6],
                'state': row[7],
                'postal_code': row[8],
                'country': row[9],
                'is_default': row[10]
            })
        
        return success_response(addresses)
        
    finally:
        cursor.close()
        db.return_connection(conn)

@user_bp.route('/addresses', methods=['POST'])
@jwt_required()
def add_address():
    user_id = get_jwt_identity()
    data = request.get_json()
    
    required = ['address_line1', 'city', 'postal_code', 'country']
    if not all(field in data for field in required):
        return error_response('Missing required fields')
    
    conn = db.get_connection()
    cursor = conn.cursor()
    
    try:
        # If this is default, unset other defaults
        if data.get('is_default'):
            cursor.execute("UPDATE addresses SET is_default = FALSE WHERE user_id = %s", (user_id,))
        
        cursor.execute("""
            INSERT INTO addresses (user_id, address_type, full_name, phone, address_line1, 
                                 address_line2, city, state, postal_code, country, is_default)
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
            RETURNING address_id
        """, (user_id, data.get('address_type', 'shipping'), data.get('full_name'),
              data.get('phone'), data['address_line1'], data.get('address_line2'),
              data['city'], data.get('state'), data['postal_code'], data['country'],
              data.get('is_default', False)))
        
        address_id = cursor.fetchone()[0]
        conn.commit()
        
        return success_response({'address_id': address_id}, 'Address added', 201)
        
    except Exception as e:
        conn.rollback()
        return error_response(str(e), 500)
    finally:
        cursor.close()
        db.return_connection(conn)
