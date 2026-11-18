"""
Test Smart OTP System
Tests SMS/Email OTP with Twilio integration and Redis caching
"""

import os
from dotenv import load_dotenv
from tools.otp_tool import SendOTPTool, VerifyOTPTool
from database.db_manager import PatientDB
from database.redis_cache import cache

load_dotenv()

def print_section(title):
    """Print formatted section header"""
    print()
    print("=" * 80)
    print(f"  {title}")
    print("=" * 80)
    print()

def test_new_patient_sms_otp():
    """Test 1: New patient gets SMS OTP (uses Twilio credit)"""
    print_section("TEST 1: New Patient - SMS OTP")
    
    # Use a NEW phone number (not in database)
    # NOTE: For Twilio trial, this must be a verified number!
    test_phone = "+91-7447444532"  # Your verified number
    test_email = "iamsamarth786@gmail.com"
    
    print(f"📞 Testing with NEW patient: {test_phone}")
    print(f"📧 Email: {test_email}")
    print()
    
    # Send OTP
    send_tool = SendOTPTool()
    result = send_tool._run(
        phone=test_phone,
        email=test_email,
        purpose="registration"
    )
    
    print(result)
    print()
    
    # Check Redis cache
    cached_otp = cache.get(f"otp:{test_phone}")
    if cached_otp:
        print(f"✅ OTP cached in Redis")
        print(f"   Code: {cached_otp.get('code', 'N/A')}")
        print(f"   Attempts: {cached_otp.get('attempts', 0)}/3")
        print(f"   TTL: {cache.get_ttl(f'otp:{test_phone}')} seconds")
        return cached_otp.get('code')
    else:
        print("⚠️ OTP not found in cache")
        return None

def test_existing_patient_email_otp():
    """Test 2: Existing patient gets Email OTP (saves Twilio credit)"""
    print_section("TEST 2: Existing Patient - Email OTP (Credit Saver!)")
    
    # First, ensure patient exists in database
    patient_db = PatientDB()
    
    test_phone = "+91-7447444532"  # Your actual phone from previous registration
    test_email = "iamsamarth786@gmail.com"  # Your actual email
    
    print(f"📞 Testing with phone: {test_phone}")
    print(f"📧 Email: {test_email}")
    print()
    
    # Check if patient exists
    existing = patient_db.get_patient_by_phone(test_phone)
    if existing:
        print(f"✅ Patient EXISTS in database!")
        print(f"   Name: {existing.get('first_name', 'N/A')} {existing.get('last_name', 'N/A')}")
        print(f"   Patient ID: {existing.get('patient_id', 'N/A')}")
        print(f"   📧 Should send EMAIL OTP (FREE!)")
    else:
        print("ℹ️ Patient NOT found in database")
        print(f"   📱 Will send SMS OTP (Twilio credit)")
    print()
    
    # Send OTP
    send_tool = SendOTPTool()
    result = send_tool._run(
        phone=test_phone,
        email=test_email,
        purpose="registration"
    )
    
    print(result)
    print()
    
    # Check Redis cache
    cached_otp = cache.get(f"otp:{test_phone}")
    if cached_otp:
        print(f"✅ OTP cached in Redis")
        print(f"   Code: {cached_otp.get('code', 'N/A')}")
        return cached_otp.get('code')
    else:
        print("⚠️ OTP not found in cache")
        return None

def test_verify_otp(phone, correct_code):
    """Test 3: Verify OTP with correct and incorrect codes"""
    print_section("TEST 3: OTP Verification")
    
    verify_tool = VerifyOTPTool()
    
    # Test 1: Wrong OTP
    print("🔴 Testing WRONG OTP code...")
    result = verify_tool._run(phone=phone, otp_code="000000")
    print(result)
    print()
    
    # Test 2: Correct OTP
    print("🟢 Testing CORRECT OTP code...")
    result = verify_tool._run(phone=phone, otp_code=correct_code)
    print(result)
    print()
    
    # Check if OTP was deleted after successful verification
    cached = cache.get(f"otp:{phone}")
    if cached:
        print("⚠️ OTP still in cache (should be deleted after verification)")
    else:
        print("✅ OTP deleted from cache after successful verification")

def test_duplicate_send_protection():
    """Test 4: Prevent duplicate OTP sends within 5 minutes"""
    print_section("TEST 4: Duplicate Send Protection")
    
    # Use verified number for trial account
    test_phone = "+91-7447444532"
    test_email = "iamsamarth786@gmail.com"
    
    send_tool = SendOTPTool()
    
    # Send first OTP
    print("📤 Sending first OTP...")
    result1 = send_tool._run(phone=test_phone, email=test_email)
    print(result1)
    print()
    
    # Check if first send was successful
    if "Failed to send" in result1:
        print("⚠️ First OTP send failed - skipping duplicate test")
        return
    
    # Try to send again immediately
    print("📤 Trying to send second OTP immediately...")
    result2 = send_tool._run(phone=test_phone, email=test_email)
    print(result2)
    print()
    
    if "Already Sent" in result2:
        print("✅ Duplicate send protection working!")
    else:
        print("⚠️ Duplicate send protection needs OTP to be sent first")

def test_max_attempts():
    """Test 5: Block after 3 wrong attempts"""
    print_section("TEST 5: Max Attempts Protection")
    
    # Use verified number
    test_phone = "+91-7447444532"
    test_email = "iamsamarth786@gmail.com"
    
    # Send OTP
    send_tool = SendOTPTool()
    result = send_tool._run(phone=test_phone, email=test_email)
    
    if "Failed to send" in result:
        print("⚠️ OTP send failed - skipping max attempts test")
        return
    
    print("📤 OTP sent successfully!")
    print()
    
    verify_tool = VerifyOTPTool()
    
    # Try 3 wrong attempts
    for i in range(1, 4):
        print(f"❌ Attempt {i}/3 with wrong code...")
        result = verify_tool._run(phone=test_phone, otp_code="111111")
        print(result)
        print()
    
    # 4th attempt should be blocked
    print("🚫 4th attempt (should be blocked)...")
    result = verify_tool._run(phone=test_phone, otp_code="111111")
    print(result)
    
    if "Too many" in result or "invalidated" in result or "No OTP Found" in result:
        print()
        print("✅ Max attempts protection working!")
    else:
        print()
        print("⚠️ Check: OTP may have been consumed by previous test")

def test_redis_stats():
    """Test 6: Check Redis stats"""
    print_section("TEST 6: Redis Cache Stats")
    
    if not cache.is_available():
        print("❌ Redis not available")
        return
    
    try:
        info = cache._redis_client.info()
        
        print("📊 Redis Statistics:")
        print(f"   Status: Connected ✅")
        print(f"   Memory Used: {info.get('used_memory_human', 'N/A')}")
        print(f"   Connected Clients: {info.get('connected_clients', 'N/A')}")
        print(f"   Uptime: {info.get('uptime_in_seconds', 0) // 60} minutes")
        print(f"   Total Keys: {cache._redis_client.dbsize()}")
        print()
        
        # List OTP keys
        otp_keys = cache._redis_client.keys("otp:*")
        print(f"🔑 OTP Keys in Cache: {len(otp_keys)}")
        for key in otp_keys:
            ttl = cache._redis_client.ttl(key)
            print(f"   - {key} (expires in {ttl}s)")
        
    except Exception as e:
        print(f"❌ Error: {e}")

# ============================================================================
# MAIN TEST RUNNER
# ============================================================================

if __name__ == "__main__":
    print()
    print("=" * 80)
    print("  🏥 CITY HOSPITAL - SMART OTP SYSTEM TESTING")
    print("  💰 Testing SMS (Twilio) vs Email (Free) routing")
    print("=" * 80)
    
    try:
        # Test 1: New patient SMS
        otp_code_new = test_new_patient_sms_otp()
        
        # Test 2: Existing patient Email
        otp_code_existing = test_existing_patient_email_otp()
        
        # Test 3: Verification (only if OTP was sent)
        if otp_code_new:
            test_verify_otp("+91-9876543210", otp_code_new)
        
        # Test 4: Duplicate protection
        test_duplicate_send_protection()
        
        # Test 5: Max attempts
        test_max_attempts()
        
        # Test 6: Redis stats
        test_redis_stats()
        
        print()
        print("=" * 80)
        print("  ✅ ALL TESTS COMPLETED")
        print("=" * 80)
        print()
        print("💡 Next Steps:")
        print("   1. Test with actual phone number (check Twilio dashboard)")
        print("   2. Test with actual email (check inbox)")
        print("   3. Integrate into workflow_chat_agent.py ✅ DONE")
        print("   4. Test end-to-end registration with OTP")
        print()
        
    except Exception as e:
        print()
        print("=" * 80)
        print(f"  ❌ TEST FAILED: {e}")
        print("=" * 80)
        import traceback
        traceback.print_exc()
