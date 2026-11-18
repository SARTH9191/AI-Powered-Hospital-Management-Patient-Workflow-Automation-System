"""
Check if patient exists and what stage they should start from
"""
import sys
from database.db_manager import PatientDB, WorkflowStateDB

def check_patient_stage():
    patient_email = "iamsamarth786@gmail.com"
    
    print(f"\n🔍 Checking patient: {patient_email}")
    print("=" * 60)
    
    # Check if patient exists
    patient_db = PatientDB()
    patients = patient_db.search_patients(patient_email)
    
    if patients:
        print(f"\n✅ Patient EXISTS in database:")
        for patient in patients:
            print(f"   - Patient ID: {patient.get('patient_id')}")
            print(f"   - Name: {patient.get('name', 'N/A')}")
            print(f"   - Email: {patient.get('email')}")
            print(f"   - Phone: {patient.get('phone', 'N/A')}")
            print(f"   - Created: {patient.get('created_at', 'N/A')}")
            
            # Check workflow state
            patient_id = patient.get('patient_id')
            workflow_db = WorkflowStateDB()
            state = workflow_db.load_state(patient_id)
            
            if state:
                print(f"\n📊 Workflow State:")
                print(f"   - Current Stage: {state.get('current_stage', 1)}")
                print(f"   - Last Updated: {state.get('last_updated_at', 'N/A')}")
                
                stage_data = state.get('stage_data', {})
                if stage_data:
                    print(f"   - Completed Stages: {list(stage_data.keys())}")
            else:
                print(f"\n⚠️ No workflow state found - Will start from Stage 1")
            
            print(f"\n💡 EXPECTED BEHAVIOR:")
            if state and state.get('current_stage', 1) > 1:
                print(f"   → Should start from Stage {state.get('current_stage')}")
            else:
                print(f"   → Existing patient should skip Stage 1 and start from Stage 2")
    else:
        print(f"\n❌ Patient NOT FOUND in database")
        print(f"   → Will need to complete registration (Stage 1) first")
    
    print("\n" + "=" * 60)

if __name__ == "__main__":
    try:
        check_patient_stage()
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()
