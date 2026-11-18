"""Check SMS delivery status"""
import os
from dotenv import load_dotenv
from twilio.rest import Client

load_dotenv()

client = Client(os.getenv('TWILIO_ACCOUNT_SID'), os.getenv('TWILIO_AUTH_TOKEN'))
msg = client.messages('SM06a8cf7732781b377c53b40a43469e1f').fetch()

print(f"\n📊 SMS Status Check:")
print(f"   Status: {msg.status}")
print(f"   Error Code: {msg.error_code}")
print(f"   Error Message: {msg.error_message}")
print(f"   Price: {msg.price}")
print(f"   Direction: {msg.direction}")
print(f"   Date Created: {msg.date_created}")
print(f"   Date Updated: {msg.date_updated}")
