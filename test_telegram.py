"""
Test Telegram notification
"""
from utils.telegram_service import init_telegram_service
from config import Config

# Initialize service
telegram_service = init_telegram_service(
    Config.TELEGRAM_BOT_TOKEN,
    Config.TELEGRAM_ADMIN_CHAT_ID
)

# Send test message
if telegram_service:
    message_id = telegram_service.send_support_notification(
        customer_name="Test Customer",
        customer_email="test@example.com",
        message="This is a test message from KStore support system!",
        order_id=12345
    )
    
    if message_id:
        print(f"✅ Test message sent successfully! Message ID: {message_id}")
        print("Check your Telegram app!")
    else:
        print("❌ Failed to send message")
else:
    print("❌ Telegram service not initialized")
