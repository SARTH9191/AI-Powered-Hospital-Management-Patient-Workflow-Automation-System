"""
Reset patient workflow state to Stage 2
"""
from database.db_manager import WorkflowStateDB

def reset_to_stage_2():
    patient_id = "PAT20251113001842"
    
    print(f"\n🔄 Resetting patient {patient_id} to Stage 2...")
    print("=" * 60)
    
    workflow_db = WorkflowStateDB()
    
    # Load current state
    state = workflow_db.load_state(patient_id)
    
    if state:
        print(f"\n📊 Current State:")
        print(f"   - Stage: {state.get('current_stage')}")
        print(f"   - Completed: {list(state.get('stage_data', {}).keys())}")
        
        # Reset to Stage 2
        state['current_stage'] = 2
        
        # Clear stage data except registration (keep patient registered)
        registration_data = state.get('stage_data', {}).get('registration', {})
        state['stage_data'] = {
            'registration': registration_data
        }
        
        # Save updated state
        workflow_db.save_state(patient_id, state)
        
        print(f"\n✅ Successfully reset to Stage 2!")
        print(f"   - New Stage: 2")
        print(f"   - Kept registration data")
        print(f"   - Cleared other stage data")
    else:
        print(f"\n❌ No workflow state found for patient {patient_id}")
    
    print("\n" + "=" * 60)

if __name__ == "__main__":
    try:
        reset_to_stage_2()
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()
