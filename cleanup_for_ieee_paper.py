"""
Complete Database Cleanup Script for IEEE Paper Testing
Deletes all test data from all storage layers to start fresh
"""
import os
import sys
import json
import shutil
from pathlib import Path

def cleanup_all_data():
    """Clean all databases and storage for fresh IEEE paper testing"""
    
    print("="*80)
    print("🧹 COMPLETE DATA CLEANUP - IEEE PAPER TESTING")
    print("="*80)
    
    # 1. Clean JSON workflow states
    print("\n📁 1. Cleaning JSON workflow states...")
    try:
        workflow_states_dir = Path("data/workflow_states")
        if workflow_states_dir.exists():
            # Delete individual patient files
            for file in workflow_states_dir.glob("REG*.json"):
                file.unlink()
                print(f"   ✅ Deleted: {file.name}")
            
            # Clean combined file
            combined_file = Path("data/workflow_states.json")
            if combined_file.exists():
                with open(combined_file, 'w') as f:
                    json.dump({}, f)
                print(f"   ✅ Cleared: workflow_states.json")
        print("   ✅ JSON cleanup complete")
    except Exception as e:
        print(f"   ⚠️ JSON cleanup error: {e}")
    
    # 2. Clean patients database
    print("\n👥 2. Cleaning patients database...")
    try:
        patients_file = Path("data/patients_database.json")
        if patients_file.exists():
            with open(patients_file, 'r') as f:
                data = json.load(f)
            
            # Keep only structure, remove all patient records except system defaults
            cleaned_data = {}
            print(f"   ✅ Removed {len(data)} patient records")
            
            with open(patients_file, 'w') as f:
                json.dump(cleaned_data, f, indent=2)
        print("   ✅ Patients database cleanup complete")
    except Exception as e:
        print(f"   ⚠️ Patients database cleanup error: {e}")
    
    # 3. Clean Redis cache
    print("\n💾 3. Cleaning Redis cache...")
    try:
        from database.redis_cache import cache
        
        # Get all workflow state keys
        import redis
        r = redis.Redis(host='localhost', port=6379, db=0, decode_responses=True)
        
        # Delete all workflow state keys
        workflow_keys = r.keys("workflow:*")
        session_keys = r.keys("session:*")
        
        for key in workflow_keys + session_keys:
            r.delete(key)
        
        print(f"   ✅ Deleted {len(workflow_keys)} workflow states")
        print(f"   ✅ Deleted {len(session_keys)} sessions")
        print("   ✅ Redis cleanup complete")
    except Exception as e:
        print(f"   ⚠️ Redis cleanup error: {e}")
    
    # 4. Clean PostgreSQL
    print("\n🗄️ 4. Cleaning PostgreSQL database...")
    try:
        from database.db_manager import DatabaseManager
        
        db = DatabaseManager()
        
        # Clean workflow_states table
        result = db.execute_query("DELETE FROM workflow_states WHERE patient_id LIKE 'REG%'")
        print("   ✅ Cleaned workflow_states table")
        
        # Clean patients table (keep only test defaults if any)
        result = db.execute_query("DELETE FROM patients WHERE email NOT LIKE '%@hospital.com'")
        print("   ✅ Cleaned patients table")
        
        # Clean otp_verifications table
        result = db.execute_query("DELETE FROM otp_verifications WHERE email NOT LIKE '%@hospital.com'")
        print("   ✅ Cleaned otp_verifications table")
        
        print("   ✅ PostgreSQL cleanup complete")
    except Exception as e:
        print(f"   ⚠️ PostgreSQL cleanup error: {e}")
    
    # 5. Summary
    print("\n" + "="*80)
    print("✅ CLEANUP COMPLETE - READY FOR IEEE PAPER TESTING")
    print("="*80)
    print("\n📋 Next Steps:")
    print("   1. Use a fresh email (e.g., test.patient@gmail.com)")
    print("   2. Follow the end-to-end test plan")
    print("   3. Take screenshots at each marked point")
    print("   4. Document results in IEEE paper")
    print("\n" + "="*80)

if __name__ == "__main__":
    confirmation = input("\n⚠️ This will DELETE ALL test data. Continue? (yes/no): ")
    if confirmation.lower() == 'yes':
        cleanup_all_data()
    else:
        print("❌ Cleanup cancelled")
