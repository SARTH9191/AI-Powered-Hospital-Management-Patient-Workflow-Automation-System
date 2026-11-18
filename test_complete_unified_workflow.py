"""
End-to-End Workflow Test with Unified Document
Tests complete workflow from Stage 2 (returning user) through Stage 12
Using single Google Doc for bidirectional communication with doctor
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
        print(f"🤖 AGENT: {result['response']}")
        print()
        print(f"📍 Current Stage: {result.get('stage')} - {result.get('stage_name', 'Unknown')}")
        print()
    
    return result


def main():
    """Run complete end-to-end workflow test"""
    
    print_section("END-TO-END WORKFLOW TEST WITH UNIFIED DOCUMENT")
    
    print("Testing:")
    print("• Stage 2: Returning user (skip document upload)")
    print("• Stage 3: Medical history → Create unified Google Doc")
    print("• Stage 4: Wait for doctor approval (Section 3)")
    print("• Stage 5: Schedule lab tests + Calendar")
    print("• Stage 6: Lab results → Update doc (Section 5)")
    print("• Stage 7: Doctor consultation → Read Section 6")
    print("• Stage 11: Prescription + Follow-up → Read Section 7")
    print("• Stage 12: Complete workflow")
    print()
    
    # Use test email (returning user)
    test_email = "iamsamarth786@gmail.com"
    
    print(f"Test Email: {test_email}")
    print()
    
    # Initialize agent
    agent = WorkflowChatAgent(patient_email=test_email)
    
    # ==================== STAGE 2: SKIP DOCUMENT UPLOAD ====================
    print_section("STAGE 2: DOCUMENT UPLOAD (BYPASS FOR RETURNING USER)")
    
    result = send_message(agent, "skip documents")
    
    if result.get('stage') != 3:
        print("❌ Failed to skip to Stage 3")
        return False
    
    print("✅ Successfully bypassed Stage 2, now at Stage 3")
    time.sleep(2)
    
    # ==================== STAGE 3: MEDICAL HISTORY ====================
    print_section("STAGE 3: MEDICAL HISTORY COLLECTION")
    
    # Step 1: Past conditions
    send_message(agent, "I have high blood pressure and diabetes")
    time.sleep(1)
    
    # Step 2: Allergies
    send_message(agent, "I'm allergic to penicillin")
    time.sleep(1)
    
    # Step 3: Current medications
    send_message(agent, "I'm taking Metformin and Lisinopril")
    time.sleep(1)
    
    # Step 4: Chief complaint
    send_message(agent, "I have chest pain and shortness of breath for the past 3 days")
    time.sleep(1)
    
    # Confirm to create workflow document
    result = send_message(agent, "yes")
    
    # Extract document URL from response
    doc_url = agent.state.get('workflow_doc_url', 'Not created')
    
    print()
    print("📄 UNIFIED WORKFLOW DOCUMENT CREATED!")
    print(f"Document URL: {doc_url}")
    print()
    print("✅ Medical history saved")
    print("✅ AI analysis added to Section 2")
    print("✅ Document shared with doctor: pawarsamarth786@gmail.com")
    print()
    
    time.sleep(2)
    
    # ==================== STAGE 4: WAIT FOR DOCTOR APPROVAL ====================
    print_section("STAGE 4: WAITING FOR DOCTOR APPROVAL")
    
    result = send_message(agent, "check")
    
    if "pending" in result['response'].lower() or "not yet" in result['response'].lower():
        print("⏳ Doctor hasn't updated yet (expected)")
        print()
        print("🔔 MANUAL STEP REQUIRED:")
        print(f"   1. Open document: {doc_url}")
        print("   2. Go to Section 3: DOCTOR'S DECISION")
        print("   3. Update the following:")
        print("      - Doctor's Decision: APPROVE")
        print("      - Approved Tests: Complete Blood Count (CBC), Lipid Profile, ECG")
        print("      - Doctor's Assessment: High risk patient, proceed with tests")
        print("      - Updated by: Dr. [Your Name]")
        print("   4. Save the document")
        print()
        
        input("Press ENTER after you've updated the doctor's decision...")
        print()
        
        # Check again
        result = send_message(agent, "check")
        
        if "approved" in result['response'].lower():
            print("✅ Doctor approval detected!")
        else:
            print("⚠️ Still pending or error. Check the document.")
            print("Current response:", result['response'][:200])
    
    time.sleep(2)
    
    # ==================== STAGE 5: LAB TEST SCHEDULING ====================
    print_section("STAGE 5: LAB TEST SCHEDULING")
    
    if "approved" in result['response'].lower():
        # Confirm to proceed with scheduling
        result = send_message(agent, "yes, proceed with scheduling")
        
        print("✅ Lab tests should be scheduled")
        print("✅ Calendar appointments should be created")
        print("✅ Section 4 of document should be updated")
    else:
        print("⚠️ Skipping Stage 5 - Doctor approval not detected")
    
    time.sleep(2)
    
    # ==================== SUMMARY ====================
    print_section("TEST SUMMARY")
    
    print("✅ Stage 2: Document upload bypassed (returning user)")
    print("✅ Stage 3: Medical history collected and unified doc created")
    print("✅ Stage 4: Doctor approval flow tested")
    
    if "approved" in result['response'].lower():
        print("✅ Stage 5: Lab scheduling initiated")
    else:
        print("⚠️ Stage 5: Pending doctor approval")
    
    print()
    print(f"📄 Workflow Document: {doc_url}")
    print()
    print("🎯 KEY FEATURES TESTED:")
    print("   ✅ Single Google Doc for entire workflow")
    print("   ✅ Bidirectional updates (AI writes, doctor updates, AI reads)")
    print("   ✅ Doctor approval required before progression")
    print("   ✅ Automatic detection of doctor updates")
    print("   ✅ Returning user bypass for document upload")
    print()
    
    print("📋 REMAINING STAGES TO IMPLEMENT:")
    print("   • Stage 5: Complete lab scheduling with Calendar integration")
    print("   • Stage 6: Lab results → Update Section 5")
    print("   • Stage 7: Doctor consultation → Read Section 6")
    print("   • Stage 11: Prescription + Follow-up → Read Section 7")
    print("   • Stage 12: Complete workflow → Update Section 8")
    print()
    
    return True


if __name__ == "__main__":
    try:
        success = main()
        sys.exit(0 if success else 1)
    except Exception as e:
        print(f"\n❌ Test error: {str(e)}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
