"""Clear Redis cache for patient session"""
import sys
sys.path.insert(0, 'D:/ai agent by myself/ai agent')

from database.redis_cache import cache
from database.db_manager import PatientDB

# Get patient info
patient_db = PatientDB()
patient = patient_db.get_patient_by_email('sarthp9191@gmail.com')

if patient:
    patient_id = patient['patient_id']
    print(f"✅ Patient ID: {patient_id}")
    print(f"   Email: {patient['email']}")
    
    # Clear all Redis sessions
    print(f"\n🗑️ Clearing Redis cache...")
    try:
        # Clear all session keys
        if cache.is_available():
            # Delete all keys matching session:*
            keys = cache._redis_client.keys('session:*')
            if keys:
                cache._redis_client.delete(*keys)
                print(f"✅ Deleted {len(keys)} Redis session keys")
            else:
                print(f"✅ No Redis sessions found")
        else:
            print(f"⚠️ Redis not available - that's OK!")
    except Exception as e:
        print(f"⚠️ Redis error: {e}")
        print(f"💡 Redis might not be running - that's OK, workflow state already deleted from PostgreSQL")
    
    print(f"\n💡 Next login will start fresh at Stage 1")
    print(f"📋 Frontend needs to refresh (Ctrl+F5) to get new session")
else:
    print("❌ Patient not found!")
