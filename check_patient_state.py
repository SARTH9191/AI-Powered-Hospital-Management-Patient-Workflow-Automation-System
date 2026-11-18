"""Check and reset patient workflow state"""
import sys
sys.path.insert(0, 'D:/ai agent by myself/ai agent')

from database.db_manager import WorkflowStateDB, PatientDB

# Check current state
workflow_db = WorkflowStateDB()
patient_db = PatientDB()

patient = patient_db.get_patient_by_email('sarthp9191@gmail.com')
if patient:
    patient_id = patient['patient_id']
    print(f"✅ Patient ID: {patient_id}")
    print(f"   Email: {patient['email']}")
    print(f"   Name: {patient.get('name', 'Unknown')}")
    
    # Check workflow state
    workflow = workflow_db.load_state(patient_id)
    if workflow:
        print(f"\n📋 Current Workflow State:")
        print(f"   Stage: {workflow.get('current_stage')}")
        print(f"   Stage Name: {workflow.get('stage_name')}")
        print(f"   Visit Number: {workflow.get('visit_number', 1)}")
        
        # DELETE workflow state
        print(f"\n🗑️ Deleting workflow state...")
        workflow_db.db.execute_query(
            "DELETE FROM workflow_states WHERE patient_id = %s",
            (patient_id,),
            fetch="none"
        )
        print(f"✅ Workflow state deleted!")
        print(f"\n💡 Patient will now start at Stage 1 on next login")
    else:
        print(f"\n✅ No workflow state found - patient will start at Stage 1")
else:
    print("❌ Patient not found!")
