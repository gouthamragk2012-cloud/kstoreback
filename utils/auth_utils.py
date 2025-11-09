import bcrypt
from functools import wraps
from flask import jsonify
from flask_jwt_extended import verify_jwt_in_request, get_jwt_identity
from db_connection import db

def hash_password(password):
    """Hash a password using bcrypt"""
    return bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')

def verify_password(password, hashed):
    """Verify a password against its hash"""
    return bcrypt.checkpw(password.encode('utf-8'), hashed.encode('utf-8'))

def admin_required():
    """Decorator to require admin role"""
    def wrapper(fn):
        @wraps(fn)
        def decorator(*args, **kwargs):
            verify_jwt_in_request()
            user_id = get_jwt_identity()
            
            conn = db.get_connection()
            cursor = conn.cursor()
            cursor.execute("SELECT role FROM users WHERE user_id = %s", (user_id,))
            result = cursor.fetchone()
            cursor.close()
            db.return_connection(conn)
            
            if not result or result[0] != 'admin':
                return jsonify({'error': 'Admin access required'}), 403
            
            return fn(*args, **kwargs)
        return decorator
    return wrapper
