"""Force delete OTP verification records for an email"""
import sys
sys.path.insert(0, 'D:/ai agent by myself/ai agent')

from database.db_manager import OTPDB

email = 'sarthp9191@gmail.com'

print(f"🗑️ Force deleting OTP verifications for: {email}")

otp_db = OTPDB()

# Check existing records
print(f"\n🔍 Checking existing OTP records...")
existing = otp_db.db.execute_query(
    "SELECT * FROM otp_verifications WHERE email = %s",
    (email,),
    fetch="all"
)

if existing:
    print(f"   Found {len(existing)} OTP record(s):")
    for record in existing:
        print(f"   - Created: {record.get('created_at')}, Verified: {record.get('verified')}")
else:
    print(f"   No OTP records found")

# Delete all OTP records
print(f"\n🗑️ Deleting OTP verification records...")
otp_db.db.execute_query(
    "DELETE FROM otp_verifications WHERE email = %s",
    (email,),
    fetch="none"
)

# Verify deletion
print(f"\n✅ Verifying deletion...")
remaining = otp_db.db.execute_query(
    "SELECT * FROM otp_verifications WHERE email = %s",
    (email,),
    fetch="all"
)

if remaining:
    print(f"   ⚠️ Still found {len(remaining)} record(s) - deletion may have failed")
else:
    print(f"   ✅ All OTP records deleted successfully")

# Test is_email_verified
print(f"\n🔍 Testing is_email_verified() method...")
is_verified = otp_db.is_email_verified(email)
print(f"   is_email_verified('{email}'): {is_verified}")

if is_verified:
    print(f"\n❌ Email still shows as verified! Check otp_verifications table manually.")
else:
    print(f"\n✅ Email no longer verified - system will start at Stage 1")

print(f"\n💡 Next Steps:")
print(f"   1. Close backend if running (Ctrl+C)")
print(f"   2. Close browser completely")
print(f"   3. Restart backend: python main.py")
print(f"   4. Open browser: http://localhost:3000")
print(f"   5. Login with {email}")
print(f"   6. Should see 'Stage 1/12: Registration'")
