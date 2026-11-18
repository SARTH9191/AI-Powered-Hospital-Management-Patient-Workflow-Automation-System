"""
Reset patient samarth.pawar243@vit.edu to Stage 3 with proper data initialization
Ensures workflow document is created with all patient information
"""

import sys
import os
sys.path.insert(0, os.path.dirname(__file__))

from database.db_manager import WorkflowStateDB, PatientDB
from database.redis_cache import cache
import json
from datetime import datetime

# Patient details
PATIENT_EMAIL = "samarth.pawar243@vit.edu"
PATIENT_NAME = "Samarth Pawar"
PATIENT_ID = "REG2025055769"

def reset_to_stage3():
    """Reset patient to Stage 3 with complete registration data"""
    
    print(f"\n🔄 Resetting patient {PATIENT_EMAIL} to Stage 3...\n")
    
    # Create complete workflow state with Stage 1 data included
    workflow_state = {
        "patient_id": PATIENT_ID,
        "email": PATIENT_EMAIL,
        "current_stage": 3,
        "stage_data": {
            "registration": {
                "full_name": PATIENT_NAME,
                "email": PATIENT_EMAIL,
                "phone": "+91-9876543210",  # Default phone
                "date_of_birth": "1995-01-15",
                "gender": "Male",
                "address": "Pune, Maharashtra, India",
                "patient_id": PATIENT_ID,
                "registration_complete": True,
                "drive_folder_created": True,
                "workflow_doc_created": False  # Will be created at Stage 3
            },
            "document_upload": {
                "documents_uploaded": True,
                "id_proof_verified": True,
                "stage_complete": True
            },
            "medical_history": {
                "stage_started": True,
                "history_retrieved": False,
                "past_conditions_asked": False,
                "allergies_asked": False,
                "medications_asked": False,
                "chief_complaint": None
            }
        },
        "conversation_history": [],
        "workflow_started_at": datetime.now().isoformat(),
        "last_updated_at": datetime.now().isoformat(),
        "awaiting_confirmation": False,
        "pending_actions": [],
        "messages": [],
        "visit_number": 1
    }
    
    # Save to PostgreSQL
    try:
        workflow_db = WorkflowStateDB()
        success = workflow_db.save_state(PATIENT_ID, workflow_state)
        if success:
            print(f"✅ Saved workflow state to PostgreSQL")
        else:
            print(f"⚠️ Failed to save to PostgreSQL")
    except Exception as e:
        print(f"❌ PostgreSQL error: {e}")
    
    # Save to Redis cache
    try:
        cache.cache_workflow_state(PATIENT_ID, workflow_state)
        print(f"✅ Cached workflow state in Redis")
    except Exception as e:
        print(f"❌ Redis cache error: {e}")
    
    # Save to JSON backup
    try:
        json_dir = "data/workflow_states"
        os.makedirs(json_dir, exist_ok=True)
        json_path = os.path.join(json_dir, f"{PATIENT_ID}.json")
        
        with open(json_path, 'w') as f:
            json.dump(workflow_state, f, indent=2)
        
        print(f"✅ Saved JSON backup to {json_path}")
    except Exception as e:
        print(f"❌ JSON backup error: {e}")
    
    # Create/Update patient record in PostgreSQL
    try:
        patient_db = PatientDB()
        
        # Check if patient exists
        existing = patient_db.get_patient_by_email(PATIENT_EMAIL)
        
        if existing:
            print(f"✅ Patient already exists in database: {existing['patient_id']}")
        else:
            # Create new patient record - split full_name into first_name and last_name
            name_parts = PATIENT_NAME.split(' ', 1)
            first_name = name_parts[0]
            last_name = name_parts[1] if len(name_parts) > 1 else ""
            
            patient_data = {
                "patient_id": PATIENT_ID,
                "first_name": first_name,
                "last_name": last_name,
                "email": PATIENT_EMAIL,
                "phone": "+91-9876543210",
                "date_of_birth": "1995-01-15",
                "gender": "Male",
                "address": "Pune, Maharashtra, India",
                "city": None,
                "state": None,
                "pincode": None,
                "drive_folder_id": None,
                "drive_folder_url": None,
                "spreadsheet_id": None,
                "emergency_contact_name": None,
                "emergency_contact_phone": None,
                "emergency_contact_relation": None
            }
            
            created = patient_db.create_patient(patient_data)
            if created:
                print(f"✅ Created patient record in database: {created}")
            else:
                print(f"⚠️ Failed to create patient record")
                
    except Exception as e:
        print(f"❌ Patient DB error: {e}")
    
    print(f"\n✅ Reset complete!")
    print(f"\n📋 Current State:")
    print(f"   Patient ID: {PATIENT_ID}")
    print(f"   Email: {PATIENT_EMAIL}")
    print(f"   Name: {PATIENT_NAME}")
    print(f"   Current Stage: 3 (Medical History Collection)")
    print(f"\n🔧 Next Steps:")
    print(f"   1. Patient can now continue chatting")
    print(f"   2. When medical history is collected, workflow doc will be created")
    print(f"   3. Workflow doc will include patient name, email, and all details from Stage 1")
    print()

if __name__ == "__main__":
    reset_to_stage3()
