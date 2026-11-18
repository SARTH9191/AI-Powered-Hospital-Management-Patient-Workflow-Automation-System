"""
Script to manually verify a user in the database
This simulates the OTP verification process for testing
"""

import sys
import os
from datetime import datetime, timedelta

# Add parent directory to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from database.db_manager import OTPDB, PatientDB

def verify_user(email, phone, full_name="Samarth Pawar", patient_id=None):
    """
    Verify a user by creating an OTP record and marking it as verified
    Also creates/updates patient record
    """
    
    print(f"📋 Verifying user: {email}")
    print(f"   Phone: {phone}")
    print(f"   Name: {full_name}")
    
    try:
        # Initialize database managers
        otp_db = OTPDB()
        patient_db = PatientDB()
        
        # Generate patient ID if not provided
        if not patient_id:
            patient_id = f"PAT{datetime.now().strftime('%Y%m%d%H%M%S')}"
        
        print(f"\n1️⃣ Checking existing verification status...")
        
        # Check if user is already verified
        is_already_verified = otp_db.is_email_verified(email)
        existing_patient = otp_db.get_patient_by_verified_email(email)
        
        if is_already_verified and existing_patient:
            print(f"   ✅ User is already verified!")
            print(f"   Patient ID: {existing_patient.get('patient_id')}")
            print(f"   Patient Name: {existing_patient.get('first_name')} {existing_patient.get('last_name')}")
            print(f"\n🎉 User {email} is already verified and ready!")
            print(f"   They will start from Stage 2 on next login.")
            return True
        
        print(f"\n2️⃣ Creating OTP record...")
        
        # Create OTP record
        otp_created = otp_db.create_otp(
            phone=phone,
            email=email,
            otp_code="123456",  # Dummy OTP code
            otp_type="sms",
            purpose="registration",
            patient_id=patient_id
        )
        
        if otp_created:
            print(f"   ✅ OTP record created")
        else:
            print(f"   ℹ️ OTP record may already exist")
        
        # Manually mark OTP as verified
        print(f"\n3️⃣ Marking OTP as verified...")
        verified = otp_db.verify_otp(phone=phone, otp_code="123456")
        
        if verified:
            print(f"   ✅ OTP verified successfully")
        else:
            print(f"   ⚠️ OTP verification failed, trying direct SQL update...")
            
            # Direct SQL update to mark as verified
            from database.db_manager import DatabaseManager
            db = DatabaseManager()
            
            update_query = """
            UPDATE otp_verifications
            SET is_verified = TRUE, verified_at = CURRENT_TIMESTAMP
            WHERE email = %s AND phone = %s
            """
            db.execute_query(update_query, (email, phone), fetch="none")
            print(f"   ✅ OTP marked as verified via direct SQL")
        
        # Create patient record
        print(f"\n4️⃣ Creating/verifying patient record...")
        
        # Split full name into first and last
        name_parts = full_name.split(" ", 1)
        first_name = name_parts[0]
        last_name = name_parts[1] if len(name_parts) > 1 else ""
        
        patient_data = {
            'patient_id': patient_id,
            'first_name': first_name,
            'last_name': last_name,
            'email': email,
            'phone': phone,
            'date_of_birth': "1990-01-01",  # Default DOB
            'gender': "Male",
            'address': "Test Address",
            'city': "Test City",
            'state': "Test State",
            'pincode': "000000",
            'drive_folder_id': None,
            'drive_folder_url': None,
            'spreadsheet_id': None,
            'emergency_contact_name': None,
            'emergency_contact_phone': None,
            'emergency_contact_relation': None
        }
        
        patient_created = patient_db.create_patient(patient_data)
        
        if patient_created:
            print(f"   ✅ Patient record created/verified: {patient_created}")
            patient_id = patient_created  # Update with actual patient ID
        else:
            print(f"   ⚠️ Patient record operation completed")
        
        # Verify the verification worked
        print(f"\n5️⃣ Verifying user status...")
        
        is_verified = otp_db.is_email_verified(email)
        patient_data = otp_db.get_patient_by_verified_email(email)
        
        print(f"\n✅ VERIFICATION COMPLETE!")
        print(f"   Email Verified: {is_verified}")
        print(f"   Patient ID: {patient_id}")
        print(f"   Patient Data Found: {patient_data is not None}")
        
        if patient_data:
            print(f"   Patient Name: {patient_data.get('full_name')}")
            print(f"   Patient Email: {patient_data.get('email')}")
            print(f"   Patient Phone: {patient_data.get('phone')}")
        
        print(f"\n🎉 User {email} is now verified and ready for testing!")
        print(f"   Next time they login, they will start from Stage 2")
        
        return True
        
    except Exception as e:
        print(f"\n❌ Error verifying user: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    # Verify the test user
    success = verify_user(
        email="iamsamarth786@gmail.com",
        phone="7447444532",
        full_name="Samarth Pawar"
    )
    
    if success:
        print("\n" + "="*60)
        print("  ✅ USER VERIFICATION SUCCESSFUL")
        print("="*60)
        print("\nYou can now run the workflow test with this verified user.")
        print("The user will automatically start from Stage 2.")
        sys.exit(0)
    else:
        print("\n" + "="*60)
        print("  ❌ USER VERIFICATION FAILED")
        print("="*60)
        sys.exit(1)
