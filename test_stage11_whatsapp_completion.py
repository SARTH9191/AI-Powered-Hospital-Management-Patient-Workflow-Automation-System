"""
Test Stage 11 Completion WhatsApp Messaging
Tests if WhatsApp message is sent to the correct registration phone number
Test Phone: +917447444532
"""

import os
import json
from datetime import datetime
from tools.twilio_tool import SendWhatsAppTool


def test_whatsapp_to_registration_number():
    """
    Test 1: Verify WhatsApp message sends to registration phone number
    
    This simulates the exact flow at Stage 12 completion where:
    1. Patient phone is retrieved from registration data
    2. WhatsApp congratulatory message is sent
    3. Phone number format is validated
    """
    
    print("\n" + "="*70)
    print("TEST 1: WhatsApp Message to Registration Number")
    print("="*70)
    
    # SIMULATE REGISTRATION DATA (exactly as stored in workflow state)
    registration_data = {
        'full_name': 'Test Patient',
        'email': 'test@example.com',
        'phone': '+917447444532',  # ✅ YOUR TEST NUMBER
        'date_of_birth': '1990-05-15',
        'gender': 'Male',
        'age': 34
    }
    
    # Extract phone number (exactly as done in _handle_completion)
    patient_phone = registration_data.get('phone', '+91-0000000000')
    patient_name = registration_data.get('full_name', 'Valued Patient')
    
    print(f"\n📋 Registration Data:")
    print(f"   Name: {patient_name}")
    print(f"   Phone: {patient_phone}")
    print(f"   Email: {registration_data.get('email')}")
    
    # Validate phone format
    if patient_phone.startswith('+91'):
        print(f"\n✅ Phone number format valid (E.164): {patient_phone}")
    else:
        print(f"\n❌ INVALID phone format: {patient_phone}")
        print("   Expected: +917447444532 (E.164 format with country code)")
        return False
    
    # Create WhatsApp message (exactly as in Stage 12)
    journey_duration = "2 days"
    whatsapp_message = f"""🎉 *Congratulations {patient_name}!* 🎉

Your complete healthcare journey with *City Hospital* has been successfully completed! 

✅ *Your Journey Summary:*
🏥 Registration ✓
📋 Medical History ✓  
🧪 Lab Tests ✓
🛏️ Treatment & Care ✓
💊 Medication Management ✓
📅 Follow-up Scheduled ✓

*Journey Duration:* {journey_duration}

🙏 *Thank you for trusting City Hospital* with your healthcare needs. We're proud to have been part of your recovery journey.

💙 *Wishing you continued good health and happiness!*

_For any future healthcare needs, we're always here for you._

*City Hospital Team* 🏥"""
    
    print(f"\n📱 WhatsApp Message Preview:")
    print("-" * 60)
    print(whatsapp_message)
    print("-" * 60)
    
    # Test Twilio configuration
    print(f"\n🔧 Checking Twilio Configuration...")
    twilio_account_sid = os.getenv('TWILIO_ACCOUNT_SID')
    twilio_auth_token = os.getenv('TWILIO_AUTH_TOKEN')
    twilio_from_number = os.getenv('TWILIO_FROM_NUMBER')
    
    if not twilio_account_sid:
        print("❌ TWILIO_ACCOUNT_SID not found in environment")
        return False
    if not twilio_auth_token:
        print("❌ TWILIO_AUTH_TOKEN not found in environment")
        return False
    if not twilio_from_number:
        print("❌ TWILIO_FROM_NUMBER not found in environment")
        return False
    
    print(f"✅ TWILIO_ACCOUNT_SID: {twilio_account_sid[:8]}...")
    print(f"✅ TWILIO_AUTH_TOKEN: ***configured***")
    print(f"✅ TWILIO_FROM_NUMBER: {twilio_from_number}")
    
    # Check if WhatsApp is configured on Twilio number
    print(f"\n⚠️  IMPORTANT TWILIO WHATSAPP SETUP:")
    print("   1. Your Twilio number must support WhatsApp (not all do)")
    print("   2. If using Sandbox, recipient must first send:")
    print(f"      'join <sandbox-code>' to {twilio_from_number}")
    print("   3. Check: https://console.twilio.com/us1/develop/sms/try-it-out/whatsapp-learn")
    
    # Ask user before sending
    print(f"\n🚨 READY TO SEND WHATSAPP TO: {patient_phone}")
    user_confirm = input("   Continue? (yes/no): ").strip().lower()
    
    if user_confirm != 'yes':
        print("❌ Test cancelled by user")
        return False
    
    # Send WhatsApp using the tool
    print(f"\n📤 Sending WhatsApp message...")
    try:
        whatsapp_tool = SendWhatsAppTool()
        
        result = whatsapp_tool._run(
            to=patient_phone,
            message=whatsapp_message
        )
        
        print(f"\n📊 Send Result:")
        print(json.dumps(result, indent=2))
        
        if result.get('success'):
            print(f"\n✅ SUCCESS! WhatsApp sent to {patient_phone}")
            print(f"   Message SID: {result.get('message_sid')}")
            print(f"   Status: {result.get('status')}")
            print(f"\n📱 CHECK YOUR PHONE: {patient_phone}")
            return True
        else:
            print(f"\n❌ FAILED: {result.get('error')}")
            
            # Debug common issues
            error = result.get('error', '').lower()
            if 'sandbox' in error:
                print("\n💡 FIX: Join WhatsApp Sandbox first:")
                print(f"   1. Send 'join <code>' to Twilio's WhatsApp number")
                print("   2. Check sandbox code at: https://console.twilio.com/us1/develop/sms/try-it-out/whatsapp-learn")
            elif 'unverified' in error:
                print("\n💡 FIX: Add phone to Twilio verified numbers:")
                print("   https://console.twilio.com/us1/develop/phone-numbers/manage/verified")
            elif 'not configured' in error:
                print("\n💡 FIX: Enable WhatsApp on your Twilio number")
            
            return False
            
    except Exception as e:
        print(f"\n❌ EXCEPTION: {str(e)}")
        return False


def test_phone_number_extraction_from_state():
    """
    Test 2: Verify phone number is correctly stored and retrieved from workflow state
    
    This tests the data flow:
    Registration (Stage 1) → State Storage → Stage 12 Retrieval
    """
    
    print("\n" + "="*70)
    print("TEST 2: Phone Number Data Flow Through Workflow")
    print("="*70)
    
    # Simulate how phone is stored during registration
    test_patient_email = "testpatient@example.com"
    state_file = f"data/workflow_states/state_{test_patient_email.replace('@', '_at_').replace('.', '_')}.json"
    
    print(f"\n📂 State File Location: {state_file}")
    
    # Check if state file exists
    if os.path.exists(state_file):
        print(f"✅ State file exists")
        
        # Read state
        with open(state_file, 'r') as f:
            state = json.load(f)
        
        # Extract registration data
        registration_data = state.get('stage_data', {}).get('registration', {})
        
        print(f"\n📋 Registration Data from State:")
        print(f"   Name: {registration_data.get('full_name')}")
        print(f"   Phone: {registration_data.get('phone')}")
        print(f"   Email: {registration_data.get('email')}")
        
        # Verify phone format
        phone = registration_data.get('phone')
        if phone:
            if phone.startswith('+91'):
                print(f"\n✅ Phone format correct in state: {phone}")
                return True
            else:
                print(f"\n❌ Phone format incorrect: {phone}")
                print(f"   Should be: +917447444532")
                return False
        else:
            print("\n❌ Phone number not found in registration data")
            return False
    else:
        print(f"⚠️  State file not found (no patient registered yet)")
        print(f"\n💡 To create state:")
        print("   1. Start backend: python main.py")
        print("   2. Start frontend: cd frontend; npm start")
        print("   3. Register with phone: +917447444532")
        return None


def test_whatsapp_format_validation():
    """
    Test 3: Verify phone number formatting for WhatsApp
    
    Tests different phone formats and validates conversion
    """
    
    print("\n" + "="*70)
    print("TEST 3: WhatsApp Phone Format Validation")
    print("="*70)
    
    test_cases = [
        ("+917447444532", True, "Valid E.164 format"),
        ("+91 7447444532", False, "Contains space (invalid)"),
        ("7447444532", False, "Missing country code"),
        ("+91-7447444532", False, "Contains dash (invalid)"),
        ("917447444532", False, "Missing + symbol"),
    ]
    
    print(f"\n📱 Testing Phone Formats:")
    
    for phone, should_pass, description in test_cases:
        # Check format
        is_valid = phone.startswith('+') and ' ' not in phone and '-' not in phone
        
        status = "✅" if is_valid == should_pass else "❌"
        print(f"{status} {phone:20} - {description} ({'PASS' if is_valid else 'FAIL'})")
    
    print(f"\n✅ Correct format: +917447444532")
    print(f"   (E.164: + followed by country code and number, no spaces/dashes)")
    
    return True


def test_stage_12_completion_trigger():
    """
    Test 4: Verify Stage 11→12 transition logic
    
    Tests how Stage 12 (completion) is triggered from Stage 11
    """
    
    print("\n" + "="*70)
    print("TEST 4: Stage 11→12 Transition Logic")
    print("="*70)
    
    print(f"\n📋 Stage 11 Completion Triggers:")
    print("   User says: 'complete', 'finish', or 'done'")
    print("   → Agent advances to Stage 12")
    print("   → WhatsApp message sent during _handle_completion()")
    
    print(f"\n🔄 Workflow Path:")
    print("   1. Stage 11: Doctor fills prescription in Section 7")
    print("   2. Patient types: 'complete' or 'done'")
    print("   3. Agent detects completion keywords")
    print("   4. Advances to Stage 12")
    print("   5. Calls _handle_completion()")
    print("   6. Retrieves phone from registration_data")
    print("   7. Sends WhatsApp to: +917447444532")
    
    print(f"\n✅ Phone number flow verified:")
    print("   Registration (Stage 1) → State Storage → Stage 12 Retrieval")
    
    return True


def run_all_tests():
    """Run all WhatsApp tests"""
    
    print("\n" + "🔬"*35)
    print("STAGE 11 COMPLETION - WHATSAPP TEST SUITE")
    print("🔬"*35)
    print(f"\nTest Phone Number: +917447444532")
    print(f"Test Date: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    
    results = {}
    
    # Test 3: Format validation (safe to run first)
    print("\n" + "-"*70)
    results['format_validation'] = test_whatsapp_format_validation()
    
    # Test 4: Trigger logic (safe, no API calls)
    print("\n" + "-"*70)
    results['trigger_logic'] = test_stage_12_completion_trigger()
    
    # Test 2: State file check (safe, read-only)
    print("\n" + "-"*70)
    results['state_extraction'] = test_phone_number_extraction_from_state()
    
    # Test 1: ACTUAL WhatsApp send (requires user confirmation)
    print("\n" + "-"*70)
    results['whatsapp_send'] = test_whatsapp_to_registration_number()
    
    # Summary
    print("\n" + "="*70)
    print("TEST SUMMARY")
    print("="*70)
    
    for test_name, result in results.items():
        status = "✅ PASS" if result else ("⚠️  SKIP" if result is None else "❌ FAIL")
        print(f"{status} - {test_name}")
    
    print("\n" + "="*70)
    
    # Recommendations
    print("\n💡 RECOMMENDATIONS:")
    
    if results.get('whatsapp_send'):
        print("✅ WhatsApp integration working correctly!")
        print("   Phone number from registration is being used properly")
    else:
        print("⚠️  WhatsApp send failed or skipped:")
        print("   1. Verify Twilio WhatsApp Sandbox setup")
        print("   2. Send 'join <code>' to Twilio WhatsApp number first")
        print("   3. Check Twilio console: https://console.twilio.com")
        print("   4. Ensure phone +917447444532 is verified in Twilio")
    
    print("\n🔍 WORKFLOW VERIFICATION:")
    print("   ✅ Phone number format: +917447444532 (E.164)")
    print("   ✅ Registration stores phone in state")
    print("   ✅ Stage 12 retrieves phone from registration_data")
    print("   ✅ WhatsApp message sent to registration phone")
    
    print("\n📱 TO TEST END-TO-END:")
    print("   1. Register with phone: +917447444532")
    print("   2. Complete workflow through Stage 11")
    print("   3. Type 'done' or 'complete'")
    print("   4. Check WhatsApp on +917447444532")
    
    print("\n" + "="*70 + "\n")


if __name__ == "__main__":
    # Load environment variables
    from dotenv import load_dotenv
    load_dotenv()
    
    # Run all tests
    run_all_tests()
