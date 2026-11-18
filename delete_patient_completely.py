import sys
import os
sys.path.insert(0, os.path.dirname(__file__))

from database.db_manager import WorkflowStateDB, PatientDB, OTPDB
from database.redis_cache import cache
import json
from pathlib import Path

PATIENT_EMAIL = "samarth.pawar243@vit.edu"
PATIENT_ID = "REG2025441318"

def delete_all_patient_data():
    print(f"\nDeleting ALL data for: {PATIENT_EMAIL}\n")
    print("=" * 60)
    
    print("\n1. Redis Cache Cleanup:")
    try:
        deleted = cache._redis_client.delete(f"workflow_state:{PATIENT_ID}")
        print(f"   Deleted: {deleted} cache entries")
    except Exception as e:
        print(f"   Error: {e}")
    
    print("\n2. JSON Files Cleanup:")
    patient_json = Path(f"data/workflow_states/{PATIENT_ID}.json")
    if patient_json.exists():
        patient_json.unlink()
        print(f"   Deleted: {patient_json}")
    else:
        print(f"   Not found: {patient_json}")
    
    combined_json = Path("data/workflow_states.json")
    if combined_json.exists():
        try:
            with open(combined_json, "r", encoding="utf-8") as f:
                all_states = json.load(f)
            if PATIENT_ID in all_states:
                del all_states[PATIENT_ID]
                with open(combined_json, "w", encoding="utf-8") as f:
                    json.dump(all_states, f, indent=2)
                print(f"   Removed from workflow_states.json")
        except Exception as e:
            print(f"   Error: {e}")
    
    print("\n3. PostgreSQL Workflow States:")
    try:
        workflow_db = WorkflowStateDB()
        workflow_db.db.execute_query("DELETE FROM workflow_states WHERE patient_id = %s", (PATIENT_ID,), fetch="none")
        print(f"   Deleted workflow state records")
    except Exception as e:
        print(f"   Error: {e}")
    
    print("\n4. PostgreSQL Patients Table:")
    try:
        patient_db = PatientDB()
        patient_db.db.execute_query("DELETE FROM patients WHERE patient_id = %s OR email = %s", (PATIENT_ID, PATIENT_EMAIL), fetch="none")
        print(f"   Deleted patient records")
    except Exception as e:
        print(f"   Error: {e}")
    
    print("\n5. PostgreSQL OTP Verifications:")
    try:
        otp_db = OTPDB()
        otp_db.db.execute_query("DELETE FROM otp_verifications WHERE email = %s", (PATIENT_EMAIL,), fetch="none")
        print(f"   Deleted OTP records")
    except Exception as e:
        print(f"   Error: {e}")
    
    print("\n" + "=" * 60)
    print("CLEANUP COMPLETE!")
    print("=" * 60)
    print(f"\nPatient {PATIENT_EMAIL} can now register fresh from Stage 1\n")

if __name__ == "__main__":
    response = input(f"DELETE ALL DATA for {PATIENT_EMAIL}? (yes/no): ")
    if response.lower() == "yes":
        delete_all_patient_data()
    else:
        print("Deletion cancelled")
