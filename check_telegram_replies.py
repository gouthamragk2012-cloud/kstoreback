"""Manually check for Telegram replies and save to database"""
import requests
import psycopg2
from config import Config

TELEGRAM_BOT_TOKEN = Config.TELEGRAM_BOT_TOKEN

def check_telegram_updates():
    """Check for new Telegram messages"""
    url = f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}/getUpdates"
    
    try:
        response = requests.get(url)
        data = response.json()
        
        if not data.get('ok'):
            print("❌ Failed to get updates from Telegram")
            return
        
        updates = data.get('result', [])
        print(f"📬 Found {len(updates)} updates")
        
        conn = psycopg2.connect(
            host=Config.DB_HOST,
            database=Config.DB_NAME,
            user=Config.DB_USER,
            password=Config.DB_PASSWORD,
            port=Config.DB_PORT
        )
        cursor = conn.cursor()
        
        for update in updates:
            if 'message' not in update:
                continue
            
            message = update['message']
            
            # Check if it's a reply
            if 'reply_to_message' not in message:
                continue
            
            reply_to_message_id = message['reply_to_message']['message_id']
            reply_text = message.get('text', '')
            
            if not reply_text:
                continue
            
            print(f"💬 Admin reply: {reply_text[:50]}...")
            
            try:
                # Find the original message
                cursor.execute("""
                    SELECT user_id, message_id
                    FROM support_messages
                    WHERE telegram_message_id = %s AND sender = 'customer'
                """, (reply_to_message_id,))
                
                result = cursor.fetchone()
                if not result:
                    print(f"   ⚠️  Original message not found")
                    continue
                
                user_id, original_message_id = result
                
                # Check if reply already exists
                cursor.execute("""
                    SELECT message_id FROM support_messages
                    WHERE user_id = %s AND message_text = %s AND sender = 'admin'
                """, (user_id, reply_text))
                
                if cursor.fetchone():
                    print(f"   ℹ️  Reply already saved")
                    continue
                
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
                print(f"   ✅ Reply saved (message_id: {admin_message_id})")
                
            except Exception as e:
                conn.rollback()
                print(f"   ❌ Error: {e}")
        
        cursor.close()
        conn.close()
        
        print("\n✅ Done checking Telegram updates")
        
    except Exception as e:
        print(f"❌ Error: {e}")

if __name__ == '__main__':
    print("🔍 Checking for Telegram replies...\n")
    check_telegram_updates()
