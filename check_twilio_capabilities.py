"""Check Twilio account capabilities and sending number details"""
import os
from dotenv import load_dotenv
from twilio.rest import Client

load_dotenv()

client = Client(os.getenv('TWILIO_ACCOUNT_SID'), os.getenv('TWILIO_AUTH_TOKEN'))

print("\n" + "="*70)
print("TWILIO ACCOUNT & NUMBER CAPABILITIES")
print("="*70)

# Check account info
account = client.api.accounts(os.getenv('TWILIO_ACCOUNT_SID')).fetch()
print(f"\n📋 Account Info:")
print(f"   Status: {account.status}")
print(f"   Type: {account.type}")

# Check sending number capabilities
from_number = os.getenv('TWILIO_PHONE_NUMBER')
print(f"\n📱 From Number: {from_number}")

try:
    # Get number capabilities
    phone_numbers = client.incoming_phone_numbers.list(phone_number=from_number)
    if phone_numbers:
        number = phone_numbers[0]
        print(f"   SMS Enabled: {number.capabilities.get('sms', False)}")
        print(f"   MMS Enabled: {number.capabilities.get('mms', False)}")
        print(f"   Voice Enabled: {number.capabilities.get('voice', False)}")
except Exception as e:
    print(f"   ⚠️  Could not fetch number details: {e}")

# Check recent messages
print(f"\n📨 Recent Messages (last 5):")
messages = client.messages.list(limit=5)
for msg in messages:
    print(f"\n   SID: {msg.sid}")
    print(f"   To: {msg.to}")
    print(f"   Status: {msg.status}")
    print(f"   Error Code: {msg.error_code}")
    print(f"   Num Segments: {msg.num_segments}")
    print(f"   Body Length: {len(msg.body) if msg.body else 0} chars")
    
    # If failed, get more details
    if msg.status == 'failed' and msg.error_code:
        print(f"   ⚠️  ERROR {msg.error_code}: Check https://www.twilio.com/docs/api/errors/{msg.error_code}")

print("\n" + "="*70)
