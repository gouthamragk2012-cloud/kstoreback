"""
Customer Support Routes - Telegram Integration
"""
from flask import Blueprint, request
from flask_jwt_extended import jwt_required, get_jwt_identity
from db_connection import db
from utils.response_utils import success_response, error_response
from utils.telegram_service import telegram_service

support_bp = Blueprint('support', __name__)

@support_bp.route('/messages', methods=['POST'])
@jwt_required()
def send_support_message():
    """Customer sends a support message"""
    user_id = get_jwt_identity()
    
    # Convert to int if string
    if isinstance(user_id, str):
        user_id = int(user_id)
    
    data = request.get_json()
    message_text = data.get('message')
    order_id = data.get('order_id')
    
    if not message_text or not message_text.strip():
        return error_response('Message cannot be empty', 400)
    
    conn = db.get_connection()
    cursor = conn.cursor()
    
    try:
        # Get user details
        cursor.execute("""
            SELECT first_name, last_name, email, is_verified
            FROM users WHERE user_id = %s
        """, (user_id,))
        
        user = cursor.fetchone()
        if not user:
            return error_response('User not found', 404)
        
        first_name, last_name, email, is_verified = user
        
        # Check if user is verified
        if not is_verified:
            return error_response('Only verified users can send support messages', 403)
        
        # Save message to database
        cursor.execute("""
            INSERT INTO support_messages 
            (user_id, order_id, message_text, sender, status)
            VALUES (%s, %s, %s, 'customer', 'pending')
            RETURNING message_id, created_at
        """, (user_id, order_id, message_text))
        
        message_id, created_at = cursor.fetchone()
        conn.commit()
        
        # Send Telegram notification to admin
        customer_name = f"{first_name} {last_name}"
        telegram_message_id = None
        
        if telegram_service:
            telegram_message_id = telegram_service.send_support_notification(
                customer_name=customer_name,
                customer_email=email,
                message=message_text,
                order_id=order_id
            )
            
            # Update with telegram_message_id
            if telegram_message_id:
                cursor.execute("""
                    UPDATE support_messages 
                    SET telegram_message_id = %s 
                    WHERE message_id = %s
                """, (telegram_message_id, message_id))
                conn.commit()
        
        return success_response({
            'message_id': message_id,
            'created_at': created_at.isoformat(),
            'status': 'pending'
        }, 'Message sent successfully! We will reply soon.', 201)
        
    except Exception as e:
        conn.rollback()
        print(f"Error sending support message: {e}")
        return error_response(str(e), 500)
    finally:
        cursor.close()
        db.return_connection(conn)

@support_bp.route('/messages', methods=['GET'])
@jwt_required()
def get_support_messages():
    """Get all support messages for current user"""
    user_id = get_jwt_identity()
    
    # Convert to int if string
    if isinstance(user_id, str):
        user_id = int(user_id)
    
    conn = db.get_connection()
    cursor = conn.cursor()
    
    try:
        cursor.execute("""
            SELECT 
                message_id, order_id, message_text, sender, 
                status, created_at
            FROM support_messages
            WHERE user_id = %s
            ORDER BY created_at ASC
        """, (user_id,))
        
        messages = []
        for row in cursor.fetchall():
            messages.append({
                'message_id': row[0],
                'order_id': row[1],
                'message_text': row[2],
                'sender': row[3],
                'status': row[4],
                'created_at': row[5].isoformat()
            })
        
        return success_response(messages)
        
    except Exception as e:
        print(f"Error fetching support messages: {e}")
        return error_response(str(e), 500)
    finally:
        cursor.close()
        db.return_connection(conn)

@support_bp.route('/webhook', methods=['POST'])
def telegram_webhook():
    """
    Webhook endpoint for Telegram bot to receive admin replies
    This will be called when admin replies in Telegram
    """
    try:
        data = request.get_json()
        
        # Check if this is a reply to a message
        if 'message' not in data:
            return success_response({'ok': True})
        
        message = data['message']
        
        # Check if it's a reply
        if 'reply_to_message' not in message:
            return success_response({'ok': True})
        
        reply_to_message_id = message['reply_to_message']['message_id']
        reply_text = message.get('text', '')
        
        if not reply_text:
            return success_response({'ok': True})
        
        conn = db.get_connection()
        cursor = conn.cursor()
        
        try:
            # Find the original message
            cursor.execute("""
                SELECT user_id, message_id
                FROM support_messages
                WHERE telegram_message_id = %s AND sender = 'customer'
            """, (reply_to_message_id,))
            
            result = cursor.fetchone()
            if not result:
                return success_response({'ok': True})
            
            user_id, original_message_id = result
            
            # Save admin reply
            cursor.execute("""
                INSERT INTO support_messages 
                (user_id, message_text, sender, status)
                VALUES (%s, %s, 'admin', 'replied')
                RETURNING message_id
            """, (user_id, reply_text))
            
            admin_message_id = cursor.fetchone()[0]
            
            # Update original message status
            cursor.execute("""
                UPDATE support_messages 
                SET status = 'replied', updated_at = CURRENT_TIMESTAMP
                WHERE message_id = %s
            """, (original_message_id,))
            
            conn.commit()
            
            # Get customer name for confirmation
            cursor.execute("""
                SELECT first_name, last_name FROM users WHERE user_id = %s
            """, (user_id,))
            
            user_data = cursor.fetchone()
            if user_data and telegram_service:
                customer_name = f"{user_data[0]} {user_data[1]}"
                telegram_service.send_reply_confirmation(customer_name, reply_text)
            
            return success_response({'ok': True, 'message_id': admin_message_id})
            
        except Exception as e:
            conn.rollback()
            print(f"Error processing webhook: {e}")
            return success_response({'ok': True})
        finally:
            cursor.close()
            db.return_connection(conn)
        
    except Exception as e:
        print(f"Webhook error: {e}")
        return success_response({'ok': True})

@support_bp.route('/messages/<int:message_id>/close', methods=['PUT'])
@jwt_required()
def close_support_message(message_id):
    """Mark a support conversation as closed"""
    user_id = get_jwt_identity()
    
    # Convert to int if string
    if isinstance(user_id, str):
        user_id = int(user_id)
    
    conn = db.get_connection()
    cursor = conn.cursor()
    
    try:
        cursor.execute("""
            UPDATE support_messages 
            SET status = 'closed', updated_at = CURRENT_TIMESTAMP
            WHERE message_id = %s AND user_id = %s
            RETURNING message_id
        """, (message_id, user_id))
        
        result = cursor.fetchone()
        if not result:
            return error_response('Message not found', 404)
        
        conn.commit()
        return success_response({'message_id': result[0]}, 'Conversation closed')
        
    except Exception as e:
        conn.rollback()
        return error_response(str(e), 500)
    finally:
        cursor.close()
        db.return_connection(conn)
