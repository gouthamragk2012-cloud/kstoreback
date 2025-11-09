from flask import Blueprint, request
from flask_jwt_extended import jwt_required, get_jwt_identity
from db_connection import db
from utils.response_utils import success_response, error_response
from utils.email_service import generate_verification_code, send_verification_email, send_welcome_email
from datetime import datetime, timedelta

verification_bp = Blueprint('verification', __name__)

@verification_bp.route('/send-code', methods=['POST'])
@jwt_required()
def send_verification_code():
    """Send or resend verification code to user's email"""
    user_id = get_jwt_identity()
    
    conn = db.get_connection()
    cursor = conn.cursor()
    
    try:
        # Get user details
        cursor.execute("""
            SELECT email, first_name, is_verified 
            FROM users 
            WHERE user_id = %s
        """, (user_id,))
        
        user = cursor.fetchone()
        if not user:
            return error_response('User not found', 404)
        
        email, first_name, is_verified = user
        
        if is_verified:
            return error_response('Email already verified', 400)
        
        # Generate new verification code
        verification_code = generate_verification_code()
        expires_at = datetime.now() + timedelta(minutes=15)
        
        # Update user with new code
        cursor.execute("""
            UPDATE users 
            SET verification_token = %s,
                verification_token_expires = %s
            WHERE user_id = %s
        """, (verification_code, expires_at, user_id))
        
        conn.commit()
        
        # Send email
        if send_verification_email(email, first_name, verification_code):
            return success_response({
                'message': 'Verification code sent to your email',
                'expires_in_minutes': 15
            })
        else:
            return error_response('Failed to send email. Please try again.', 500)
        
    except Exception as e:
        conn.rollback()
        print(f"Error sending verification code: {e}")
        return error_response(str(e), 500)
    finally:
        cursor.close()
        db.return_connection(conn)

@verification_bp.route('/verify-code', methods=['POST'])
@jwt_required()
def verify_code():
    """Verify the code entered by user"""
    user_id = get_jwt_identity()
    data = request.get_json()
    
    if not data or 'code' not in data:
        return error_response('Verification code is required', 400)
    
    code = data['code'].strip()
    
    if len(code) != 6 or not code.isdigit():
        return error_response('Invalid code format. Code must be 6 digits.', 400)
    
    conn = db.get_connection()
    cursor = conn.cursor()
    
    try:
        # Get user verification details
        cursor.execute("""
            SELECT email, first_name, verification_token, 
                   verification_token_expires, is_verified
            FROM users 
            WHERE user_id = %s
        """, (user_id,))
        
        user = cursor.fetchone()
        if not user:
            return error_response('User not found', 404)
        
        email, first_name, stored_token, expires_at, is_verified = user
        
        if is_verified:
            return error_response('Email already verified', 400)
        
        if not stored_token:
            return error_response('No verification code found. Please request a new code.', 400)
        
        # Check if code expired
        if datetime.now() > expires_at:
            return error_response('Verification code has expired. Please request a new code.', 400)
        
        # Verify code
        if stored_token != code:
            return error_response('Invalid verification code', 400)
        
        # Mark user as verified
        cursor.execute("""
            UPDATE users 
            SET is_verified = TRUE,
                verification_token = NULL,
                verification_token_expires = NULL
            WHERE user_id = %s
        """, (user_id,))
        
        conn.commit()
        
        # Send welcome email
        send_welcome_email(email, first_name)
        
        return success_response({
            'message': 'Email verified successfully!',
            'is_verified': True
        })
        
    except Exception as e:
        conn.rollback()
        print(f"Error verifying code: {e}")
        return error_response(str(e), 500)
    finally:
        cursor.close()
        db.return_connection(conn)

@verification_bp.route('/status', methods=['GET'])
@jwt_required()
def verification_status():
    """Check if user is verified"""
    user_id = get_jwt_identity()
    
    conn = db.get_connection()
    cursor = conn.cursor()
    
    try:
        cursor.execute("""
            SELECT is_verified, email 
            FROM users 
            WHERE user_id = %s
        """, (user_id,))
        
        user = cursor.fetchone()
        if not user:
            return error_response('User not found', 404)
        
        is_verified, email = user
        
        return success_response({
            'is_verified': is_verified,
            'email': email
        })
        
    finally:
        cursor.close()
        db.return_connection(conn)
