"""Completely delete all data for sarthp9191@gmail.com"""
import sys
sys.path.insert(0, 'D:/ai agent by myself/ai agent')

from database.db_manager import WorkflowStateDB, PatientDB
from database.redis_cache import cache

email = 'sarthp9191@gmail.com'

# Get patient info
patient_db = PatientDB()
patient = patient_db.get_patient_by_email(email)

if patient:
    patient_id = patient['patient_id']
    print(f"✅ Found Patient:")
    print(f"   ID: {patient_id}")
    print(f"   Email: {patient['email']}")
    print(f"   Name: {patient.get('name', 'Unknown')}")
    
    # 1. Delete workflow state
    print(f"\n🗑️ Step 1: Deleting workflow state...")
    workflow_db = WorkflowStateDB()
    workflow_db.db.execute_query(
        "DELETE FROM workflow_states WHERE patient_id = %s",
        (patient_id,),
        fetch="none"
    )
    print(f"   ✅ Workflow state deleted")
    
    # 2. Delete patient record completely
    print(f"\n🗑️ Step 2: Deleting patient record from database...")
    patient_db.db.execute_query(
        "DELETE FROM patients WHERE patient_id = %s",
        (patient_id,),
        fetch="none"
    )
    print(f"   ✅ Patient record deleted")
    
    # 3. 🔥 CRITICAL: Delete OTP verification record (this causes "returning user" detection!)
    print(f"\n🗑️ Step 3: Deleting OTP verification record...")
    patient_db.db.execute_query(
        "DELETE FROM otp_verifications WHERE email = %s",
        (email,),
        fetch="none"
    )
    print(f"   ✅ OTP verification record deleted (was causing returning user detection!)")
    
    # 4. Clear all Redis cache
    print(f"\n🗑️ Step 4: Clearing all Redis sessions...")
    try:
        if cache.is_available():
            keys = cache._redis_client.keys('session:*')
            if keys:
                cache._redis_client.delete(*keys)
                print(f"   ✅ Deleted {len(keys)} Redis session keys")
            else:
                print(f"   ✅ No Redis sessions found")
        else:
            print(f"   ⚠️ Redis not available")
    except Exception as e:
        print(f"   ⚠️ Redis error: {e}")
    
    print(f"\n✅ COMPLETE DATA DELETION SUCCESSFUL!")
    print(f"\n💡 Next Steps:")
    print(f"   1. Close browser completely")
    print(f"   2. Open new browser window")
    print(f"   3. Go to http://localhost:3000")
    print(f"   4. Login with {email}")
    print(f"   5. Will start fresh at Stage 1 (Registration)")
    
else:
    print(f"❌ Patient with email {email} not found in database")
