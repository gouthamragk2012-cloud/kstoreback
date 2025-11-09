"""
Telegram Bot Service for Customer Support
"""
import requests
from typing import Optional

class TelegramService:
    def __init__(self, bot_token: str, admin_chat_id: str):
        self.bot_token = bot_token
        self.admin_chat_id = admin_chat_id
        self.base_url = f"https://api.telegram.org/bot{bot_token}"
    
    def send_message(self, text: str, parse_mode: str = "HTML") -> Optional[int]:
        """
        Send message to admin's Telegram
        Returns: telegram_message_id if successful, None otherwise
        """
        try:
            url = f"{self.base_url}/sendMessage"
            payload = {
                "chat_id": self.admin_chat_id,
                "text": text,
                "parse_mode": parse_mode
            }
            
            response = requests.post(url, json=payload, timeout=10)
            response.raise_for_status()
            
            result = response.json()
            if result.get("ok"):
                return result.get("result", {}).get("message_id")
            return None
            
        except Exception as e:
            print(f"Error sending Telegram message: {e}")
            return None
    
    def send_support_notification(
        self, 
        customer_name: str, 
        customer_email: str, 
        message: str,
        order_id: Optional[int] = None
    ) -> Optional[int]:
        """
        Send formatted support notification to admin
        """
        order_info = f"\n📦 <b>Order:</b> #{order_id}" if order_id else ""
        
        text = f"""
🔔 <b>New Support Message</b>

👤 <b>Customer:</b> {customer_name}
📧 <b>Email:</b> {customer_email}{order_info}

💬 <b>Message:</b>
{message}

━━━━━━━━━━━━━━━━
Reply to this message to respond to the customer.
        """.strip()
        
        return self.send_message(text)
    
    def send_reply_confirmation(self, customer_name: str, reply_text: str) -> Optional[int]:
        """
        Send confirmation that reply was sent to customer
        """
        text = f"""
✅ <b>Reply Sent</b>

Your reply to {customer_name} has been delivered:

"{reply_text}"
        """.strip()
        
        return self.send_message(text)

# Initialize service (will be imported in routes)
telegram_service = None

def init_telegram_service(bot_token: str, admin_chat_id: str):
    global telegram_service
    telegram_service = TelegramService(bot_token, admin_chat_id)
    return telegram_service
