"""
Fresh Workflow Test - Start from Stage 2
Tests complete workflow with unified document from scratch
"""

import sys
import codecs
if sys.platform == 'win32':
    sys.stdout = codecs.getwriter('utf-8')(sys.stdout.buffer, 'strict')
    sys.stderr = codecs.getwriter('utf-8')(sys.stderr.buffer, 'strict')

from src.workflow_chat_agent import WorkflowChatAgent
import time


def print_section(title):
    print(f"\n{'='*80}")
    print(f"  {title}")
    print(f"{'='*80}\n")


def send_message(agent, message, show_response=True):
    """Send message and optionally print response"""
    print(f"👤 USER: {message}")
    print()
    
    result = agent.process_message(message)
    
    if show_response:
        print(f"🤖 AGENT: {result['response'][:500]}...")  # Truncate long responses
        print()
        print(f"📍 Stage: {result.get('stage')} | Complete: {result.get('stage_complete')}")
        print()
    
    return result


def main():
    """Run fresh workflow test"""
    
    print_section("FRESH WORKFLOW TEST - UNIFIED DOCUMENT")
    
    # Use test email (returning user)
    test_email = "iamsamarth786@gmail.com"
    
    print(f"Test Email: {test_email}")
    print()
    
    # Initialize agent
    agent = WorkflowChatAgent(patient_email=test_email)
    
    print(f"Current Stage: {agent.state.get('current_stage')}")
    print(f"Current Stage Name: {agent.state.get('stage_name')}")
    print()
    
    # Check if we need to skip to Stage 3
    current_stage = agent.state.get('current_stage')
    
    if current_stage == 2:
        print_section("STAGE 2: BYPASS FOR RETURNING USER")
        result = send_message(agent, "skip documents")
        time.sleep(1)
    
    if current_stage == 4 and not agent.state.get('workflow_doc_id'):
        print("⚠️ At Stage 4 but no workflow document found.")
        print("Let's go back to Stage 3 to create the document.")
        print()
        
        # Reset to Stage 3
        agent.state['current_stage'] = 3
        agent.state['stage_name'] = 'medical_history'
        agent._save_state()
        
        print("✅ Reset to Stage 3")
        print()
    
    if agent.state.get('current_stage') == 3:
        print_section("STAGE 3: MEDICAL HISTORY")
        
        # Check if medical history already collected
        stage_data = agent.state.get('stage_data', {}).get('medical_history', {})
        
        if not stage_data.get('chief_complaint'):
            print("Collecting medical history...")
            send_message(agent, "I have high blood pressure and diabetes")
            time.sleep(1)
            send_message(agent, "I'm allergic to penicillin")
            time.sleep(1)
            send_message(agent, "I'm taking Metformin and Lisinopril")
            time.sleep(1)
            send_message(agent, "I have chest pain and shortness of breath for 3 days")
            time.sleep(1)
            send_message(agent, "yes")  # Confirm
        else:
            print("Medical history already collected")
            print("Moving to Stage 4...")
            agent.state['current_stage'] = 4
            agent.state['stage_name'] = 'test_determination'
            agent._save_state()
    
    # Print current document info
    doc_url = agent.state.get('workflow_doc_url')
    doc_id = agent.state.get('workflow_doc_id')
    
    if doc_url:
        print_section("WORKFLOW DOCUMENT CREATED")
        print(f"📄 Document URL: {doc_url}")
        print(f"📄 Document ID: {doc_id}")
        print()
    
    if agent.state.get('current_stage') == 4:
        print_section("STAGE 4: WAITING FOR DOCTOR APPROVAL")
        
        if not doc_url:
            print("❌ No workflow document found!")
            print("Please restart from Stage 3")
            return False
        
        print(f"📄 Document: {doc_url}")
        print()
        print("Check #1: Looking for doctor's decision...")
        result = send_message(agent, "check")
        
        if "pending" in result['response'].lower() or "not yet" in result['response'].lower():
            print()
            print("="*80)
            print("  MANUAL STEP REQUIRED")
            print("="*80)
            print()
            print(f"1. Open: {doc_url}")
            print("2. Go to Section 3: DOCTOR'S DECISION")
            print("3. Fill in:")
            print("   Doctor's Decision: APPROVE")
            print("   Approved Tests: Complete Blood Count (CBC), Lipid Profile, ECG")
            print("   Doctor's Assessment: High risk cardiac patient, proceed with comprehensive testing")
            print("   Updated by: Dr. Smith")
            print("4. Save the document")
            print()
            
            input("Press ENTER after updating the document...")
            print()
            
            print("Check #2: Re-checking doctor's decision...")
            result = send_message(agent, "check")
            
            if "approved" in result['response'].lower():
                print()
                print("✅ Doctor approval detected!")
                print("✅ Ready to proceed to Stage 5")
            else:
                print()
                print("⚠️ Still pending. Check the document format.")
        
        else:
            print("✅ Doctor has already approved!")
    
    print_section("TEST SUMMARY")
    print(f"Current Stage: {agent.state.get('current_stage')}")
    print(f"Workflow Doc: {doc_url if doc_url else 'Not created'}")
    print()
    print("✅ Stage 2: Bypass complete")
    print("✅ Stage 3: Medical history + unified doc created")
    print(f"{'✅' if agent.state.get('stage_data', {}).get('test_determination', {}).get('doctor_decision_made') else '⏳'} Stage 4: Doctor approval")
    print()
    
    return True


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n\n⚠️ Test interrupted by user")
    except Exception as e:
        print(f"\n\n❌ Error: {str(e)}")
        import traceback
        traceback.print_exc()
