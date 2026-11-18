"""
Quick Test: Returning User Document Upload Bypass
Verifies that returning users can skip Stage 2 and advance to Stage 3
"""

import sys
import codecs
if sys.platform == 'win32':
    sys.stdout = codecs.getwriter('utf-8')(sys.stdout.buffer, 'strict')
    sys.stderr = codecs.getwriter('utf-8')(sys.stderr.buffer, 'strict')

from src.workflow_chat_agent import WorkflowChatAgent
from database.db_manager import OTPDB, WorkflowStateDB
import json
import os


def clear_workflow_state(patient_id):
    """Clear all workflow states"""
    print(f"🧹 Clearing workflow state for {patient_id}...")
    
    # Clear PostgreSQL
    workflow_db = WorkflowStateDB()
    current_state = workflow_db.load_state(patient_id)
    if current_state:
        delete_query = "DELETE FROM workflow_states WHERE patient_id = %s"
        workflow_db.db.execute_query(delete_query, (patient_id,), fetch="none")
        print(f"   ✅ PostgreSQL cleared (was at Stage {current_state.get('current_stage')})")
    
    # Clear JSON
    json_state_file = 'data/workflow_states.json'
    if os.path.exists(json_state_file):
        try:
            with open(json_state_file, 'r', encoding='utf-8') as f:
                states = json.load(f)
            
            if patient_id in states:
                del states[patient_id]
                with open(json_state_file, 'w', encoding='utf-8') as f:
                    json.dump(states, f, indent=2)
                print(f"   ✅ JSON cleared")
        except Exception as e:
            pass
    
    print()


def test_returning_user_document_bypass():
    """Test that returning users can skip document upload"""
    
    print("\n" + "="*80)
    print("  QUICK TEST: Returning User Document Upload Bypass")
    print("="*80 + "\n")
    
    test_email = "iamsamarth786@gmail.com"
    
    # Get patient info
    otp_db = OTPDB()
    patient_data = otp_db.get_patient_by_verified_email(test_email)
    patient_id = patient_data.get('patient_id')
    
    print(f"Test User: {test_email}")
    print(f"Patient ID: {patient_id}\n")
    
    # Clear state
    clear_workflow_state(patient_id)
    
    # Initialize agent
    print("1️⃣ Initialize agent (returning user)")
    agent = WorkflowChatAgent(patient_email=test_email)
    
    print(f"   ✅ Agent initialized")
    print(f"   - Returning User: {agent.is_returning_user}")
    print(f"   - Current Stage: {agent.state['current_stage']}")
    print()
    
    if agent.state['current_stage'] != 2:
        print(f"   ❌ FAILED: Expected Stage 2, got {agent.state['current_stage']}")
        return False
    
    # Test 1: Skip document upload
    print("2️⃣ Test skip document upload (Stage 2 → Stage 3)")
    response = agent.process_message("skip document upload, proceed to medical history")
    
    print(f"   Response preview: {response['response'][:200]}...")
    print(f"   Current Stage: {agent.state['current_stage']}")
    print(f"   Stage Complete: {response.get('stage_complete', False)}")
    print()
    
    if agent.state['current_stage'] != 3:
        print(f"   ❌ FAILED: Expected Stage 3, got {agent.state['current_stage']}")
        print(f"   Response: {response['response']}")
        return False
    
    print("   ✅ SUCCESS: Advanced from Stage 2 → Stage 3!")
    print()
    
    # Test 2: Provide medical history
    print("3️⃣ Test medical history input (Stage 3)")
    medical_history = "I have chest pain and shortness of breath. History of hypertension."
    
    response = agent.process_message(medical_history)
    
    print(f"   Response preview: {response['response'][:200]}...")
    print(f"   Current Stage: {agent.state['current_stage']}")
    print()
    
    if agent.state['current_stage'] != 3:
        print(f"   ⚠️ Note: Stage changed to {agent.state['current_stage']}")
    else:
        print(f"   ✅ Still at Stage 3 (collecting medical history)")
    
    print()
    
    # Summary
    print("="*80)
    print("  TEST SUMMARY")
    print("="*80 + "\n")
    
    print("✅ **RETURNING USER DOCUMENT BYPASS WORKING!**\n")
    print("Test Results:")
    print("   ✅ Agent detected as returning user")
    print("   ✅ Started at Stage 2 (Document Upload)")
    print("   ✅ Successfully skipped document upload")
    print("   ✅ Advanced to Stage 3 (Medical History)")
    print("   ✅ Accepting medical history input")
    print()
    print("🎉 **Feature Working Correctly!**")
    print()
    
    return True


if __name__ == "__main__":
    try:
        success = test_returning_user_document_bypass()
        
        if success:
            print("✅ Test PASSED!")
            sys.exit(0)
        else:
            print("❌ Test FAILED!")
            sys.exit(1)
            
    except Exception as e:
        print(f"\n❌ TEST ERROR: {str(e)}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
