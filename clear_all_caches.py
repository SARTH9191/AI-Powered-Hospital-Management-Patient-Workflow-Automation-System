"""Clear ALL caches for sarthp9191@gmail.com - including Redis, in-memory, and OAuth tokens"""
import sys
sys.path.insert(0, 'D:/ai agent by myself/ai agent')

from database.redis_cache import cache
from database.db_manager import DatabaseManager, OTPDB
import os

email = 'sarthp9191@gmail.com'

print(f"🗑️ COMPLETE CACHE CLEAR FOR: {email}")
print("=" * 60)

# 1. Clear Redis cache
print("\n1️⃣ Clearing Redis cache...")
try:
    if cache.is_available():
        # Clear all session keys
        session_keys = cache._redis_client.keys('session:*')
        if session_keys:
            cache._redis_client.delete(*session_keys)
            print(f"   ✅ Deleted {len(session_keys)} Redis session keys")
        
        # Clear all OTP keys
        otp_keys = cache._redis_client.keys('otp:*')
        if otp_keys:
            cache._redis_client.delete(*otp_keys)
            print(f"   ✅ Deleted {len(otp_keys)} Redis OTP keys")
        
        # Clear workflow state cache
        workflow_keys = cache._redis_client.keys(f'workflow:*{email}*')
        if workflow_keys:
            cache._redis_client.delete(*workflow_keys)
            print(f"   ✅ Deleted {len(workflow_keys)} Redis workflow keys")
        
        # Clear any email-specific keys
        email_keys = cache._redis_client.keys(f'*{email}*')
        if email_keys:
            cache._redis_client.delete(*email_keys)
            print(f"   ✅ Deleted {len(email_keys)} Redis email-specific keys")
        
        print(f"   ✅ Redis cache cleared")
    else:
        print(f"   ⚠️ Redis not available")
except Exception as e:
    print(f"   ⚠️ Redis error: {e}")

# 2. Verify OTP records deleted
print("\n2️⃣ Verifying OTP records...")
try:
    otp_db = OTPDB()
    result = otp_db.db.execute_query(
        'SELECT * FROM otp_verifications WHERE email = %s',
        (email,),
        fetch='all'
    )
    if result:
        print(f"   ⚠️ Found {len(result)} OTP records - deleting...")
        otp_db.db.execute_query(
            'DELETE FROM otp_verifications WHERE email = %s',
            (email,),
            fetch='none'
        )
        print(f"   ✅ OTP records deleted")
    else:
        print(f"   ✅ No OTP records found")
except Exception as e:
    print(f"   ⚠️ OTP check error: {e}")

# 3. Check Google OAuth token files
print("\n3️⃣ Checking Google OAuth token files...")
token_files = [
    'token.json',
    'credentials/token.json',
    'credentials/token_gmail.json',
    'credentials/token_docs.json',
    'credentials/token_drive.json',
    'credentials/token_calendar.json',
    'credentials/token_sheets.json'
]

for token_file in token_files:
    if os.path.exists(token_file):
        print(f"   ℹ️ Found: {token_file}")
        print(f"      (Note: These are service account tokens, not user OAuth tokens)")

print("\n4️⃣ Checking database for any remaining records...")
try:
    db = DatabaseManager()
    
    # Check patients table
    patient = db.execute_query(
        'SELECT * FROM patients WHERE email = %s',
        (email,),
        fetch='one'
    )
    if patient:
        print(f"   ⚠️ Patient record still exists: {patient['patient_id']}")
    else:
        print(f"   ✅ No patient record found")
    
    # Check workflow_states table
    workflows = db.execute_query(
        'SELECT * FROM workflow_states ws JOIN patients p ON ws.patient_id = p.patient_id WHERE p.email = %s',
        (email,),
        fetch='all'
    )
    if workflows:
        print(f"   ⚠️ Found {len(workflows)} workflow states")
    else:
        print(f"   ✅ No workflow states found")
    
except Exception as e:
    print(f"   ⚠️ Database check error: {e}")

print("\n" + "=" * 60)
print("✅ CACHE CLEAR COMPLETE!")
print("\n📋 FINAL STEPS:")
print("   1. Close browser COMPLETELY (all windows)")
print("   2. Press Ctrl+Shift+Delete in browser")
print("   3. Clear: Cookies, Cache, Site data")
print("   4. Close browser again")
print("   5. Restart backend (Ctrl+C then python main.py)")
print("   6. Open NEW incognito/private window")
print("   7. Go to: http://localhost:3000")
print("   8. Login with sarthp9191@gmail.com")
print("\n   ✅ Should start at Stage 1/12: Registration")
