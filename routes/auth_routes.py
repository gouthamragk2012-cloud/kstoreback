from flask import Blueprint, request
from flask_jwt_extended import create_access_token, create_refresh_token, jwt_required, get_jwt_identity
from db_connection import db
from utils.auth_utils import hash_password, verify_password
from utils.response_utils import success_response, error_response
from utils.email_service import generate_verification_code, send_verification_email
from datetime import datetime, timedelta

auth_bp = Blueprint('auth', __name__)

@auth_bp.route('/register', methods=['POST'])
def register():
    data = request.get_json()
    
    required_fields = ['email', 'password', 'first_name', 'last_name']
    if not all(field in data for field in required_fields):
        return error_response('Missing required fields')
    
    email = data['email'].lower().strip()
    password = data['password']
    
    if len(password) < 8:
        return error_response('Password must be at least 8 characters')
    
    conn = db.get_connection()
    cursor = conn.cursor()
    
    try:
        # Check if user exists
        cursor.execute("SELECT user_id FROM users WHERE email = %s", (email,))
        if cursor.fetchone():
            return error_response('Email already registered', 409)
        
        # Create user with verification code
        password_hash = hash_password(password)
        verification_code = generate_verification_code()
        verification_expires = datetime.now() + timedelta(minutes=15)
        
        cursor.execute("""
            INSERT INTO users (email, password_hash, first_name, last_name, phone, role, 
                             verification_token, verification_token_expires, is_verified)
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)
            RETURNING user_id, email, first_name, last_name, role, created_at, is_verified
        """, (email, password_hash, data['first_name'], data['last_name'], 
              data.get('phone'), data.get('role', 'customer'),
              verification_code, verification_expires, False))
        
        user = cursor.fetchone()
        conn.commit()
        
        # Send verification email
        send_verification_email(user[1], user[2], verification_code)
        
        user_data = {
            'user_id': user[0],
            'email': user[1],
            'first_name': user[2],
            'last_name': user[3],
            'role': user[4],
            'created_at': user[5].isoformat(),
            'is_verified': user[6]
        }
        
        access_token = create_access_token(identity=str(user[0]))
        refresh_token = create_refresh_token(identity=str(user[0]))
        
        return success_response({
            'user': user_data,
            'access_token': access_token,
            'refresh_token': refresh_token,
            'requires_verification': True
        }, 'Registration successful. Please check your email for verification code.', 201)
        
    except Exception as e:
        conn.rollback()
        return error_response(f'Registration failed: {str(e)}', 500)
    finally:
        cursor.close()
        db.return_connection(conn)

@auth_bp.route('/login', methods=['POST'])
def login():
    data = request.get_json()
    
    if not data.get('email') or not data.get('password'):
        return error_response('Email and password required')
    
    email = data['email'].lower().strip()
    password = data['password']
    
    conn = db.get_connection()
    cursor = conn.cursor()
    
    try:
        cursor.execute("""
            SELECT user_id, email, password_hash, first_name, last_name, role, is_active, is_verified, phone
            FROM users WHERE email = %s
        """, (email,))
        
        user = cursor.fetchone()
        
        if not user or not verify_password(password, user[2]):
            return error_response('Invalid credentials', 401)
        
        if not user[6]:
            return error_response('Account is inactive', 403)
        
        # Update last login
        cursor.execute("UPDATE users SET last_login = CURRENT_TIMESTAMP WHERE user_id = %s", (user[0],))
        conn.commit()
        
        user_data = {
            'user_id': user[0],
            'email': user[1],
            'first_name': user[3],
            'last_name': user[4],
            'role': user[5],
            'is_verified': user[7],
            'phone': user[8]
        }
        
        access_token = create_access_token(identity=str(user[0]))
        refresh_token = create_refresh_token(identity=str(user[0]))
        
        return success_response({
            'user': user_data,
            'access_token': access_token,
            'refresh_token': refresh_token
        }, 'Login successful')
        
    except Exception as e:
        return error_response(f'Login failed: {str(e)}', 500)
    finally:
        cursor.close()
        db.return_connection(conn)

@auth_bp.route('/refresh', methods=['POST'])
@jwt_required(refresh=True)
def refresh():
    user_id = get_jwt_identity()
    access_token = create_access_token(identity=user_id)
    return success_response({'access_token': access_token})

@auth_bp.route('/me', methods=['GET'])
@jwt_required()
def get_current_user():
    user_id = get_jwt_identity()
    
    conn = db.get_connection()
    cursor = conn.cursor()
    
    try:
        cursor.execute("""
            SELECT user_id, email, first_name, last_name, phone, role, is_verified, created_at
            FROM users WHERE user_id = %s
        """, (user_id,))
        
        user = cursor.fetchone()
        
        if not user:
            return error_response('User not found', 404)
        
        user_data = {
            'user_id': user[0],
            'email': user[1],
            'first_name': user[2],
            'last_name': user[3],
            'phone': user[4],
            'role': user[5],
            'is_verified': user[6],
            'created_at': user[7].isoformat()
        }
        
        return success_response(user_data)
        
    finally:
        cursor.close()
        db.return_connection(conn)
