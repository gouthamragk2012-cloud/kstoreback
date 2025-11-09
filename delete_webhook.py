"""Delete Telegram webhook to enable polling"""
import requests
from config import Config

TELEGRAM_BOT_TOKEN = Config.TELEGRAM_BOT_TOKEN

if not TELEGRAM_BOT_TOKEN:
    print("❌ TELEGRAM_BOT_TOKEN not configured")
    exit(1)

url = f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}/deleteWebhook"

try:
    response = requests.get(url)
    data = response.json()
    
    if data.get('ok'):
        print("✅ Webhook deleted successfully!")
        print("   You can now use polling mode")
    else:
        print(f"❌ Failed to delete webhook: {data.get('description')}")
        
except Exception as e:
    print(f"❌ Error: {e}")
