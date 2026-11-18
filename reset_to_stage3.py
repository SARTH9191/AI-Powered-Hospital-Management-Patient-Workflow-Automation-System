"""
Reset Patient to Stage 3 for Testing
Resets iamsamarth786@gmail.com back to Stage 3 (Medical History Collection)
"""

from database.db_manager import WorkflowStateDB, PatientDB
from database.redis_cache import RedisCache
import json

PATIENT_EMAIL = "iamsamarth786@gmail.com"

def reset_to_stage3():
    """Reset patient to Stage 3 for retesting"""
    
    print(f"🔄 Resetting {PATIENT_EMAIL} to Stage 3...")
    
    # Step 1: Find patient by email
    patient_db = PatientDB()
    try:
        patient = patient_db.get_patient_by_email(PATIENT_EMAIL)
        if not patient:
            print(f"❌ No patient found with email: {PATIENT_EMAIL}")
            return False
        
        patient_id = patient['patient_id']
        patient_name = patient.get('full_name') or f"{patient.get('first_name', '')} {patient.get('last_name', '')}".strip()
        print(f"✅ Found patient: {patient_name} ({patient_id})")
        
    except Exception as e:
        print(f"❌ Error finding patient: {e}")
        return False
    
    # Step 2: Update PostgreSQL workflow state to Stage 3
    workflow_db = WorkflowStateDB()
    
    stage3_state = {
        'patient_id': patient_id,
        'current_stage': 3,
        'stage_name': 'medical_history',
        'stage_data': {
            'registration': {
                'full_name': patient_name,
                'email': PATIENT_EMAIL,
                'phone': patient.get('phone', ''),
                'registration_complete': True
            },
            'document_upload': {
                'documents_checked': True,
                'upload_complete': True
            },
            'medical_history': {
                'history_retrieved': False,
                'past_conditions_asked': False,
                'allergies_asked': False,
                'medications_asked': False
            }
        },
        'conversation_history': [],
        'awaiting_confirmation': False,
        'pending_actions': [],
        'session_id': f'reset-stage3-{patient_id}',
        'is_active': True
    }
    
    try:
        workflow_db.save_state(patient_id, stage3_state)
        print(f"✅ PostgreSQL updated: Stage 3 (medical_history)")
    except Exception as e:
        print(f"❌ Error updating PostgreSQL: {e}")
        return False
    
    # Step 3: Clear Redis cache for this patient
    cache = RedisCache()
    if cache.is_available():
        try:
            # Find and delete all session keys for this patient
            import redis
            r = redis.Redis(
                host='localhost',
                port=6379,
                db=0,
                decode_responses=True
            )
            
            deleted = 0
            for key in r.keys('session:*'):
                session_data = r.get(key)
                if session_data and PATIENT_EMAIL in session_data:
                    r.delete(key)
                    deleted += 1
            
            print(f"✅ Cleared {deleted} Redis session(s)")
        except Exception as e:
            print(f"⚠️ Redis clear warning: {e}")
    
    print("\n" + "="*60)
    print("✅ RESET COMPLETE!")
    print("="*60)
    print(f"Patient: {patient_name}")
    print(f"Email: {PATIENT_EMAIL}")
    print(f"Patient ID: {patient_id}")
    print(f"Current Stage: 3 - Medical History Collection")
    print("="*60)
    print("\n📋 NEXT STEPS:")
    print("1. In FRONTEND: Clear localStorage")
    print("   - Press F12 → Console")
    print("   - Type: localStorage.clear()")
    print("   - Press Enter → Refresh page")
    print("\n2. Login again with: iamsamarth786@gmail.com")
    print("\n3. You should now be at Stage 3!")
    print("\n4. Test with:")
    print("   'I have diabetes and high blood pressure. I'm having severe")
    print("    stomach pain and vomiting for 2 days.'")
    print("="*60)
    
    return True

if __name__ == "__main__":
    print("\n" + "="*60)
    print("🔧 PATIENT RESET TOOL - Stage 3")
    print("="*60)
    print(f"Email: {PATIENT_EMAIL}")
    print(f"Target Stage: 3 - Medical History Collection")
    print("="*60)
    
    confirm = input("\nProceed with reset? (yes/no): ")
    
    if confirm.lower() in ['yes', 'y']:
        success = reset_to_stage3()
        if success:
            print("\n✅ You're ready to test Stage 3!")
        else:
            print("\n❌ Reset failed. Check errors above.")
    else:
        print("\n❌ Reset cancelled.")
