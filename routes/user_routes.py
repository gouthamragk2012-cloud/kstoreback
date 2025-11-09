from flask import Blueprint, request
from flask_jwt_extended import jwt_required, get_jwt_identity
from db_connection import db
from utils.response_utils import success_response, error_response
from utils.auth_utils import admin_required

user_bp = Blueprint('users', __name__)

@user_bp.route('', methods=['GET'])
@jwt_required()
def get_all_users():
    """Admin endpoint to get all users"""
    user_id = get_jwt_identity()
    
    # Convert to int if string
    if isinstance(user_id, str):
        user_id = int(user_id)
    
    # Check if user is admin
    conn = db.get_connection()
    cursor = conn.cursor()
    
    try:
        # Verify admin role
        cursor.execute("SELECT role FROM users WHERE user_id = %s", (user_id,))
        result = cursor.fetchone()
        if not result or result[0] != 'admin':
            return error_response('Admin access required', 403)
        
        # Get all users
        cursor.execute("""
            SELECT user_id, email, first_name, last_name, phone, role, 
                   is_active, is_verified, created_at, last_login
            FROM users
            ORDER BY created_at DESC
        """)
        
        users = []
        for row in cursor.fetchall():
            users.append({
                'user_id': row[0],
                'email': row[1],
                'first_name': row[2],
                'last_name': row[3],
                'phone': row[4],
                'role': row[5],
                'is_active': row[6],
                'is_verified': row[7],
                'created_at': row[8].isoformat(),
                'last_login': row[9].isoformat() if row[9] else None
            })
        
        return success_response(users)
        
    finally:
        cursor.close()
        db.return_connection(conn)

@user_bp.route('/profile', methods=['GET'])
@jwt_required()
def get_profile():
    user_id = get_jwt_identity()
    
    conn = db.get_connection()
    cursor = conn.cursor()
    
    try:
        cursor.execute("""
            SELECT user_id, email, first_name, last_name, phone, gender, date_of_birth, 
                   role, is_verified, created_at
            FROM users 
            WHERE user_id = %s
        """, (user_id,))
        
        user = cursor.fetchone()
        
        if not user:
            return error_response('User not found', 404)
        
        return success_response({
            'user_id': user[0],
            'email': user[1],
            'first_name': user[2],
            'last_name': user[3],
            'phone': user[4],
            'gender': user[5],
            'date_of_birth': user[6].isoformat() if user[6] else None,
            'role': user[7],
            'is_verified': user[8],
            'created_at': user[9].isoformat()
        })
        
    finally:
        cursor.close()
        db.return_connection(conn)

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
                gender = COALESCE(%s, gender),
                date_of_birth = COALESCE(%s, date_of_birth),
                updated_at = CURRENT_TIMESTAMP
            WHERE user_id = %s
            RETURNING user_id, email, first_name, last_name, phone, gender, date_of_birth
        """, (data.get('first_name'), data.get('last_name'), data.get('phone'), 
              data.get('gender'), data.get('date_of_birth'), user_id))
        
        user = cursor.fetchone()
        conn.commit()
        
        return success_response({
            'user_id': user[0],
            'email': user[1],
            'first_name': user[2],
            'last_name': user[3],
            'phone': user[4],
            'gender': user[5],
            'date_of_birth': user[6].isoformat() if user[6] else None
        }, 'Profile updated successfully')
        
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

@user_bp.route('/addresses/<int:address_id>', methods=['PUT'])
@jwt_required()
def update_address(address_id):
    user_id = get_jwt_identity()
    data = request.get_json()
    
    # Convert to int if string
    if isinstance(user_id, str):
        user_id = int(user_id)
    
    conn = db.get_connection()
    cursor = conn.cursor()
    
    try:
        # Verify address belongs to user
        cursor.execute("SELECT user_id FROM addresses WHERE address_id = %s", (address_id,))
        result = cursor.fetchone()
        
        if not result:
            return error_response('Address not found', 404)
        
        if result[0] != user_id:
            return error_response('Unauthorized', 403)
        
        # If this is default, unset other defaults
        if data.get('is_default'):
            cursor.execute("UPDATE addresses SET is_default = FALSE WHERE user_id = %s AND address_id != %s", 
                         (user_id, address_id))
        
        cursor.execute("""
            UPDATE addresses 
            SET address_line1 = COALESCE(%s, address_line1),
                address_line2 = %s,
                city = COALESCE(%s, city),
                state = COALESCE(%s, state),
                postal_code = COALESCE(%s, postal_code),
                country = COALESCE(%s, country),
                is_default = COALESCE(%s, is_default),
                updated_at = CURRENT_TIMESTAMP
            WHERE address_id = %s AND user_id = %s
            RETURNING address_id
        """, (data.get('address_line1'), data.get('address_line2'), data.get('city'),
              data.get('state'), data.get('postal_code'), data.get('country'),
              data.get('is_default'), address_id, user_id))
        
        result = cursor.fetchone()
        conn.commit()
        
        if not result:
            return error_response('Failed to update address', 500)
        
        return success_response({'address_id': result[0]}, 'Address updated successfully')
        
    except Exception as e:
        conn.rollback()
        return error_response(str(e), 500)
    finally:
        cursor.close()
        db.return_connection(conn)
