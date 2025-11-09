"""Setup Telegram webhook with ngrok URL"""
import requests
from config import Config
import sys

TELEGRAM_BOT_TOKEN = Config.TELEGRAM_BOT_TOKEN

if len(sys.argv) < 2:
    print("❌ Please provide your ngrok URL")
    print("\nUsage: python setup_telegram_webhook.py https://your-ngrok-url.ngrok.io")
    print("\nSteps:")
    print("1. Run: ngrok http 5000")
    print("2. Copy the https URL (e.g., https://abc123.ngrok.io)")
    print("3. Run: python setup_telegram_webhook.py https://abc123.ngrok.io")
    sys.exit(1)

ngrok_url = sys.argv[1].rstrip('/')
webhook_url = f"{ngrok_url}/api/support/webhook"

print(f"🔧 Setting up Telegram webhook...")
print(f"📡 Webhook URL: {webhook_url}\n")

# Set webhook
url = f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}/setWebhook"
response = requests.post(url, json={'url': webhook_url})
data = response.json()

if data.get('ok'):
    print("✅ Webhook set successfully!")
    print(f"📱 Telegram will now send your replies to: {webhook_url}")
    print("\n🎉 Your chatbot is now live! Replies will appear automatically.")
else:
    print(f"❌ Failed to set webhook: {data}")

# Check webhook info
info_url = f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}/getWebhookInfo"
info_response = requests.get(info_url)
info_data = info_response.json()

if info_data.get('ok'):
    webhook_info = info_data.get('result', {})
    print(f"\n📊 Current webhook status:")
    print(f"   URL: {webhook_info.get('url', 'Not set')}")
    print(f"   Pending updates: {webhook_info.get('pending_update_count', 0)}")
