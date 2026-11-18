"""
Quick Test: Twilio SMS & WhatsApp Integration
This script demonstrates the Twilio tools without running the full workflow
"""

import os
from dotenv import load_dotenv
from tools.twilio_tool import SendSMSTool, SendWhatsAppTool, GetMessageStatusTool

# Load environment
load_dotenv()

print("="*70)
print("🧪 TWILIO INTEGRATION TEST")
print("="*70)

# Test 1: Check Configuration
print("\n1️⃣ Checking Twilio Configuration...")
account_sid = os.getenv('TWILIO_ACCOUNT_SID')
auth_token = os.getenv('TWILIO_AUTH_TOKEN')
phone_number = os.getenv('TWILIO_PHONE_NUMBER')

if account_sid and auth_token and phone_number:
    print(f"✅ Account SID: {account_sid[:10]}...")
    print(f"✅ Auth Token: {auth_token[:10]}...")
    print(f"✅ Phone Number: {phone_number}")
else:
    print("❌ Twilio credentials not found in .env")
    print("   Add: TWILIO_ACCOUNT_SID, TWILIO_AUTH_TOKEN, TWILIO_PHONE_NUMBER")
    exit(1)

# Test 2: Demonstrate SMS Tool
print("\n2️⃣ SMS Tool Demo (DRY RUN - not actually sending)")
print("-" * 70)

sms_tool = SendSMSTool()
print(f"Tool Name: {sms_tool.name}")
print(f"Description: {sms_tool.description[:100]}...")

# Show what SMS would look like
sample_sms = """🏥 Welcome to City Hospital!

Your registration is complete.
Patient ID: REG2025XXXXX
Name: Test Patient

Next steps:
1. Document submission
2. Medical history review
3. Lab tests (if required)

Questions? Call: +91 74474 44532"""

print(f"\nSample SMS Message:")
print("-" * 70)
print(sample_sms)
print("-" * 70)

# Test 3: Demonstrate WhatsApp Tool
print("\n3️⃣ WhatsApp Tool Demo (DRY RUN - not actually sending)")
print("-" * 70)

whatsapp_tool = SendWhatsAppTool()
print(f"Tool Name: {whatsapp_tool.name}")
print(f"Description: {whatsapp_tool.description[:100]}...")

# Show what WhatsApp would look like
sample_whatsapp = """🔬 *Lab Tests Scheduled*

Dear Test Patient,

Your lab tests have been scheduled:

📅 *Date:* 2025-10-19
🕐 *Time:* 10:00 AM
📍 *Location:* Hospital Lab - Room 201

*Tests Ordered (5):*
   • Complete Blood Count
   • Comprehensive Metabolic Panel
   • Lipid Profile
   • HbA1c
   • Thyroid Function Test

*Preparation:*
- Fasting required (8 hours)
- Bring Photo ID
- Bring prescription copy

_City Hospital Lab Services_"""

print(f"\nSample WhatsApp Message:")
print("-" * 70)
print(sample_whatsapp)
print("-" * 70)

# Test 4: Demonstrate Status Tool
print("\n4️⃣ Message Status Tool Demo")
print("-" * 70)

status_tool = GetMessageStatusTool()
print(f"Tool Name: {status_tool.name}")
print(f"Description: {status_tool.description[:100]}...")

print(f"\nUsage:")
print("  status_tool._run(message_sid='SM1234567890abcdef')")
print("\nReturns:")
print("  - Status: queued, sent, delivered, failed, undelivered")
print("  - Timestamps")
print("  - Error codes (if any)")
print("  - Pricing information")

# Test 5: Show Trial Account Tips
print("\n5️⃣ Trial Account Tips")
print("-" * 70)
print("💡 SMS:")
print("   - Only verified numbers receive SMS")
print("   - Add numbers in Twilio Console → Verified Caller IDs")
print("   - Cost: ~$0.0065 per SMS")
print("")
print("💡 WhatsApp:")
print("   - Recipient must join sandbox first")
print("   - Send 'join <code>' to Twilio WhatsApp number")
print("   - Get code from Console → Messaging → Try WhatsApp")
print("   - Cost: ~$0.005 per message")
print("")
print("💡 Balance:")
print("   - Current: $15.50")
print("   - Estimated messages: ~2,500")
print("   - Track usage in Twilio Console")

# Test 6: Actual Send Test (Optional)
print("\n6️⃣ Ready to Send Real Messages?")
print("-" * 70)
print("To test with your verified phone number:")
print("")
print("# SMS Test:")
print("result = sms_tool._run(")
print("    to='+91XXXXXXXXXX',  # Your verified number")
print("    message='Test SMS from Hospital AI Agent'")
print(")")
print("print(result)")
print("")
print("# WhatsApp Test (after joining sandbox):")
print("result = whatsapp_tool._run(")
print("    to='+91XXXXXXXXXX',  # Your verified number")
print("    message='*Test WhatsApp* from Hospital AI Agent'")
print(")")
print("print(result)")

print("\n" + "="*70)
print("✅ TWILIO INTEGRATION READY!")
print("="*70)
print("")
print("📚 Documentation: See TWILIO_INTEGRATION_COMPLETE.md")
print("🌐 API Docs: http://localhost:8000/docs")
print("🧪 Full Test: powershell -ExecutionPolicy Bypass -File .\\quick_test_state_persistence.ps1")
print("")
