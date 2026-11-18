"""
Test SMS Thank You Message at Stage 12 Completion
Sends SMS to registration phone number: +917447444532
"""

import os
from datetime import datetime
from dotenv import load_dotenv

# Load environment variables
load_dotenv()


def test_sms_thank_you_message():
    """
    Test sending SMS thank you message to patient phone number
    This simulates the exact SMS sent at Stage 12 completion
    """
    
    print("\n" + "="*70)
    print("SMS THANK YOU MESSAGE TEST - STAGE 12 COMPLETION")
    print("="*70)
    
    # Simulate registration data (as stored in workflow state)
    patient_name = "Test Patient"
    patient_phone = "+917447444532"  # YOUR TEST PHONE NUMBER
    journey_duration = "2 days"
    
    print(f"\n📋 Test Configuration:")
    print(f"   Patient Name: {patient_name}")
    print(f"   Phone Number: {patient_phone}")
    print(f"   Journey Duration: {journey_duration}")
    
    # Check Twilio configuration
    print(f"\n🔧 Twilio Configuration:")
    twilio_sid = os.getenv('TWILIO_ACCOUNT_SID')
    twilio_token = os.getenv('TWILIO_AUTH_TOKEN')
    twilio_from = os.getenv('TWILIO_FROM_NUMBER')
    
    if not twilio_sid:
        print("❌ TWILIO_ACCOUNT_SID not configured")
        return False
    if not twilio_token:
        print("❌ TWILIO_AUTH_TOKEN not configured")
        return False
    if not twilio_from:
        print("❌ TWILIO_FROM_NUMBER not configured")
        return False
    
    print(f"✅ Account SID: {twilio_sid[:8]}...")
    print(f"✅ Auth Token: ***configured***")
    print(f"✅ From Number: {twilio_from}")
    
    # Short SMS message (under 160 chars for international delivery)
    sms_message = f"Congratulations {patient_name}! Your healthcare journey at City Hospital is complete. Thank you for trusting us. Wishing you good health! - City Hospital"
    
    print(f"\n📱 SMS Message Preview:")
    print("-" * 70)
    print(sms_message)
    print("-" * 70)
    print(f"\nMessage Length: {len(sms_message)} characters")
    
    if len(sms_message) > 1600:
        print(f"⚠️  Message will be truncated to 1600 characters")
    
    # Confirm before sending
    print(f"\n🚨 READY TO SEND SMS TO: {patient_phone}")
    user_confirm = input("   Continue? (yes/no): ").strip().lower()
    
    if user_confirm != 'yes':
        print("\n❌ Test cancelled by user")
        return False
    
    # Send SMS using SendSMSTool
    print(f"\n📤 Sending SMS...")
    try:
        from tools.twilio_tool import SendSMSTool
        sms_tool = SendSMSTool()
        
        result = sms_tool._run(
            to=patient_phone,
            message=sms_message
        )
        
        print(f"\n📊 SMS Send Result:")
        print("=" * 70)
        
        if result and result.get('success'):
            print(f"✅ SUCCESS! SMS sent to {patient_phone}")
            print(f"\n📋 Details:")
            print(f"   To: {result.get('to', patient_phone)}")
            print(f"   Message SID: {result.get('message_sid', 'N/A')}")
            print(f"   Status: {result.get('status', 'sent')}")
            print(f"   Timestamp: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
            
            print(f"\n📱 CHECK YOUR PHONE: {patient_phone}")
            print(f"   You should receive the SMS within 1-2 minutes")
            
            return True
        else:
            print(f"❌ FAILED to send SMS")
            print(f"   Error: {result.get('error', 'Unknown error')}")
            
            # Debug common issues
            error = str(result.get('error', '')).lower()
            if 'unverified' in error or '21608' in error:
                print(f"\n💡 FIX: Phone number not verified in Twilio")
                print(f"   1. Go to: https://console.twilio.com/us1/develop/phone-numbers/manage/verified")
                print(f"   2. Click 'Add new number'")
                print(f"   3. Enter: {patient_phone}")
                print(f"   4. Verify via SMS or call")
            elif 'invalid' in error:
                print(f"\n💡 FIX: Check phone number format")
                print(f"   Current: {patient_phone}")
                print(f"   Required: E.164 format (e.g., +917447444532)")
            
            return False
            
    except Exception as e:
        print(f"\n❌ EXCEPTION: {str(e)}")
        import traceback
        traceback.print_exc()
        return False


def test_phone_number_format():
    """Test phone number format validation"""
    
    print("\n" + "="*70)
    print("PHONE NUMBER FORMAT VALIDATION")
    print("="*70)
    
    test_number = "+917447444532"
    
    print(f"\n📱 Testing Phone Number: {test_number}")
    
    # Check E.164 format
    checks = {
        "Starts with +": test_number.startswith('+'),
        "No spaces": ' ' not in test_number,
        "No dashes": '-' not in test_number,
        "Length 10-15 digits": 10 <= len(test_number.replace('+', '')) <= 15,
        "Country code +91": test_number.startswith('+91')
    }
    
    print(f"\n✅ Format Validation:")
    all_passed = True
    for check, result in checks.items():
        status = "✅" if result else "❌"
        print(f"   {status} {check}: {result}")
        if not result:
            all_passed = False
    
    if all_passed:
        print(f"\n✅ Phone number format is VALID (E.164)")
        return True
    else:
        print(f"\n❌ Phone number format is INVALID")
        return False


def verify_twilio_number():
    """Check if phone number is verified in Twilio"""
    
    print("\n" + "="*70)
    print("TWILIO PHONE NUMBER VERIFICATION STATUS")
    print("="*70)
    
    print(f"\n⚠️  IMPORTANT:")
    print(f"   Twilio Trial accounts can only send SMS to verified numbers")
    print(f"   Phone +917447444532 must be verified in Twilio console")
    
    print(f"\n📋 How to verify:")
    print(f"   1. Visit: https://console.twilio.com/us1/develop/phone-numbers/manage/verified")
    print(f"   2. Click 'Add new number' button")
    print(f"   3. Select 'Text you instead' option")
    print(f"   4. Enter: +917447444532")
    print(f"   5. Receive verification code via SMS")
    print(f"   6. Enter code to complete verification")
    
    print(f"\n💡 Alternative:")
    print(f"   If you have production Twilio account, verification not needed")
    
    return True


if __name__ == "__main__":
    print("\n" + "🔬"*35)
    print("STAGE 12 SMS COMPLETION TEST")
    print("🔬"*35)
    print(f"\nTest Date: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"Test Phone: +917447444532")
    
    # Run tests
    print("\n" + "━"*70)
    print("TEST 1: Phone Number Format Validation")
    print("━"*70)
    format_ok = test_phone_number_format()
    
    print("\n" + "━"*70)
    print("TEST 2: Twilio Verification Instructions")
    print("━"*70)
    verify_twilio_number()
    
    print("\n" + "━"*70)
    print("TEST 3: Send SMS Thank You Message")
    print("━"*70)
    sms_ok = test_sms_thank_you_message()
    
    # Summary
    print("\n" + "="*70)
    print("TEST SUMMARY")
    print("="*70)
    
    if sms_ok:
        print(f"\n✅ SMS SENT SUCCESSFULLY!")
        print(f"   Phone: +917447444532")
        print(f"   Message: Journey completion thank you")
        print(f"   Check your phone for the SMS!")
    else:
        print(f"\n⚠️  SMS NOT SENT")
        print(f"   Most likely reason: Phone not verified in Twilio trial account")
        print(f"   Action: Verify +917447444532 in Twilio console")
    
    print("\n" + "="*70)
    print("\n💡 NEXT STEPS:")
    print("   1. If SMS received: Integration working perfectly! ✅")
    print("   2. If error 21608: Verify phone in Twilio console")
    print("   3. If other error: Check Twilio credentials in .env")
    print("\n" + "="*70 + "\n")
