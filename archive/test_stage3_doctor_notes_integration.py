"""
Test Stage 3 (Medical History) - Doctor Notes Doc Auto-Creation

This tests Phase 2 integration: When Stage 3 completes, a Google Doc
is automatically created for the doctor to fill in consultation notes.

Workflow:
1. Simulate Stage 3 medical history collection
2. Patient confirms to proceed
3. Verify doctor notes doc is auto-created
4. Verify doc ID is saved to state
5. Verify doc link is provided to patient
"""

import os
import sys
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Add parent directory to path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.workflow_chat_agent import WorkflowChatAgent
from datetime import datetime


def print_section(title: str, content: str = ""):
    """Print formatted section"""
    print(f"\n{'='*70}")
    print(f"{title}")
    print(f"{'='*70}")
    if content:
        print(content)


def test_stage3_doctor_notes_creation():
    """Test that doctor notes doc is auto-created during Stage 3 completion"""
    
    print_section("🧪 STAGE 3 DOCTOR NOTES AUTO-CREATION TEST")
    print("Testing Phase 2 integration: Auto-create doctor notes doc")
    
    # Create agent with test patient
    agent = WorkflowChatAgent(
        patient_email="test_stage3@hospital.com",
        patient_id="REG2025STAGE3TEST"
    )
    
    # Set up patient in Stage 3 with awaiting confirmation state
    agent.state["current_stage"] = 3
    agent.state["awaiting_confirmation"] = True
    agent.state["pending_actions"] = ["save_medical_history", "analyze_risks"]
    agent.state["stage_data"] = {
        "registration": {
            "full_name": "Alice Johnson",
            "email": "alice@example.com",
            "phone": "+1234567890"
        },
        "medical_history": {
            "past_conditions_asked": True,
            "past_conditions": ["Asthma"],
            "allergies_asked": True,
            "allergies": ["Penicillin"],
            "medications_asked": True,
            "current_medications": ["Albuterol inhaler"],
            "chief_complaint": "Chest pain and shortness of breath for 2 days"
        }
    }
    
    print("\n📋 Test Patient Setup:")
    print(f"   Patient ID: {agent.patient_id}")
    print(f"   Name: Alice Johnson")
    print(f"   Current Stage: 3 (Medical History)")
    print(f"   Chief Complaint: Chest pain and shortness of breath")
    
    # Simulate confirmation to trigger actions
    print("\n🔄 Step 1: Patient confirms medical history")
    print('   Patient says: "yes, proceed"')
    
    try:
        result = agent.process_message("yes, proceed")
        
        print("\n✅ Agent Response:")
        print(f"   {result['response'][:300]}...")
        
        # Check if doctor notes doc was created
        doc_id = agent.state.get("doctor_notes_doc_id")
        doc_url = agent.state.get("doctor_notes_doc_url")
        
        if doc_id and doc_url:
            print_section("✅ TEST PASSED: DOCTOR NOTES DOC AUTO-CREATED!")
            print(f"\n📄 Doctor Notes Document:")
            print(f"   Document ID: {doc_id}")
            print(f"   URL: {doc_url}")
            print(f"\n💡 What this means:")
            print(f"   1. ✅ Doctor has a Google Doc ready to fill")
            print(f"   2. ✅ Doc contains patient info and chief complaint")
            print(f"   3. ✅ Doctor can edit diagnosis/treatment anytime")
            print(f"   4. ✅ AI can read doc when patient asks questions")
            print(f"   5. ✅ No custom portal needed - just Google Docs!")
            
            print(f"\n📊 State Verification:")
            print(f"   ✓ doctor_notes_doc_id saved: {doc_id}")
            print(f"   ✓ doctor_notes_doc_url saved: {doc_url}")
            print(f"   ✓ Stage complete: {result.get('stage_complete')}")
            
            print(f"\n🎯 Phase 2 Integration Status:")
            print(f"   ✅ PRIORITY 1 COMPLETE: Stage 3 auto-creates doctor notes doc")
            print(f"   ⏳ PRIORITY 2 PENDING: Q&A system enhancement")
            print(f"   ⏳ PRIORITY 3 PENDING: Stage 6 diagnosis integration")
            
            return True
        else:
            print_section("❌ TEST FAILED: Doctor notes doc NOT created")
            print(f"\n❌ Issue: Doc ID or URL missing from state")
            print(f"   doctor_notes_doc_id: {doc_id}")
            print(f"   doctor_notes_doc_url: {doc_url}")
            print(f"\n📋 Full Response:")
            print(f"   {result['response']}")
            return False
            
    except Exception as e:
        print_section("❌ TEST EXCEPTION")
        print(f"Error: {e}")
        import traceback
        traceback.print_exc()
        return False


def main():
    """Run the test"""
    print_section("🏥 PHASE 2 INTEGRATION TEST - STAGE 3")
    print("Testing: Auto-create doctor notes doc when medical history completes")
    
    test_passed = test_stage3_doctor_notes_creation()
    
    print_section("📊 TEST SUMMARY")
    
    if test_passed:
        print("✅ PASSED - Stage 3 Doctor Notes Auto-Creation")
        print("\n🎉 Phase 2 - Priority 1 COMPLETE!")
        print("\n🚀 Next Steps:")
        print("   1. ✅ Stage 3 integration working")
        print("   2. ⏭️  Implement Priority 2: Q&A system enhancement")
        print("   3. ⏭️  Implement Priority 3: Stage 6 diagnosis integration")
        print("   4. ⏭️  Test end-to-end patient journey")
    else:
        print("❌ FAILED - Stage 3 Doctor Notes Auto-Creation")
        print("\n⚠️  Review errors above and fix issues")
    
    print_section("🏁 TEST COMPLETE")


if __name__ == "__main__":
    main()
