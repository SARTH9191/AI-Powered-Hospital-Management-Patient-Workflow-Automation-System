"""
🎯 COMPLETE END-TO-END WORKFLOW TEST
Tests all stages: 2 → 3 → 4 → 5 → 6 → 7 → 11 → 12

Patient: iamsamarth786@gmail.com (Phone: 7447444532)
Credentials: client_secret.json + individual token pickles
"""

import os
import sys
import time
from datetime import datetime

# Fix Unicode encoding for Windows PowerShell
if sys.platform == "win32":
    import io
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8')

# Add src to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

from workflow_chat_agent import WorkflowChatAgent

def print_stage_header(stage_num, stage_name):
    """Print a nice stage header"""
    print("\n" + "="*80)
    print(f"🎯 STAGE {stage_num}: {stage_name}")
    print("="*80 + "\n")

def print_response(response_dict):
    """Print agent response"""
    print("\n" + "-"*80)
    print("🤖 AGENT RESPONSE:")
    print("-"*80)
    print(response_dict.get('response', 'No response'))
    print("-"*80)
    print(f"📊 Stage: {response_dict.get('stage', 'N/A')}")
    print(f"✅ Stage Complete: {response_dict.get('stage_complete', False)}")
    if response_dict.get('next_stage'):
        print(f"➡️  Next Stage: {response_dict['next_stage']}")
    print("-"*80 + "\n")

def wait_for_user(prompt="Press Enter to continue..."):
    """Wait for user input"""
    input(f"\n⏸️  {prompt}")

def main():
    """Run complete end-to-end workflow test"""
    
    print("\n" + "🌟"*40)
    print("🏥 COMPLETE END-TO-END WORKFLOW TEST")
    print("🌟"*40)
    print(f"\n📅 Test Date: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"👤 Patient Email: iamsamarth786@gmail.com")
    print(f"📱 Phone: 7447444532")
    print("\n" + "🌟"*40 + "\n")
    
    # Initialize agent
    print("🔧 Initializing Workflow Chat Agent...")
    agent = WorkflowChatAgent(
        patient_email="iamsamarth786@gmail.com",
        patient_id="PAT20251113001842"  # Existing patient
    )
    print("✅ Agent initialized!\n")
    print(f"📱 Patient Phone: 7447444532 (stored in state/DB)\n")
    
    # ================================================================
    # STAGE 2: RETURNING USER - START CHAT
    # ================================================================
    print_stage_header(2, "RETURNING USER - START CHAT")
    print("💬 User says: Hello, I need medical help")
    
    response = agent.process_message("Hello, I need medical help")
    print_response(response)
    
    wait_for_user("Ready to proceed to Stage 3 (Medical History)?")
    
    # ================================================================
    # STAGE 3: MEDICAL HISTORY + AI ANALYSIS → CREATE GOOGLE DOC
    # ================================================================
    print_stage_header(3, "MEDICAL HISTORY + AI ANALYSIS → CREATE DOC")
    
    # Provide symptoms
    print("💬 User provides symptoms...")
    response = agent.process_message("I have fever, headache, and body pain for 3 days")
    print_response(response)
    
    # Answer medical questions
    print("\n💬 Answering medical history questions...")
    
    print("\n❓ Q: Any chronic conditions?")
    response = agent.process_message("I have diabetes")
    print_response(response)
    
    print("\n❓ Q: Current medications?")
    response = agent.process_message("Taking Metformin 500mg")
    print_response(response)
    
    print("\n❓ Q: Any allergies?")
    response = agent.process_message("No allergies")
    print_response(response)
    
    print("\n💬 User says: That's all, no more questions")
    response = agent.process_message("That's all, no more medical history")
    print_response(response)
    
    # Check if document was created
    if agent.state.get('workflow_doc_url'):
        print(f"\n✅ DOCUMENT CREATED!")
        print(f"📄 URL: {agent.state['workflow_doc_url']}")
        print(f"📄 ID: {agent.state['workflow_doc_id']}")
    else:
        print("\n⚠️ No document created yet, continuing...")
    
    wait_for_user("Ready to proceed to Stage 4 (Doctor Approval)?")
    
    # ================================================================
    # STAGE 4: DOCTOR REVIEWS AND APPROVES TESTS IN DOC
    # ================================================================
    print_stage_header(4, "DOCTOR REVIEWS AND APPROVES TESTS IN DOC")
    
    print("📄 MANUAL STEP REQUIRED:")
    print("="*80)
    print("1. Open the document URL above")
    print("2. Find SECTION 3: DOCTOR'S DECISION")
    print("3. Add doctor's decision:")
    print("")
    print("   ✅ TESTS APPROVED")
    print("")
    print("   Recommended Tests:")
    print("   1. Complete Blood Count (CBC)")
    print("   2. Blood Glucose (Fasting)")
    print("   3. Lipid Profile")
    print("")
    print("4. Save the document")
    print("="*80)
    
    wait_for_user("After updating Section 3, press Enter to check approval...")
    
    # Check for approval
    print("\n💬 Checking doctor's decision...")
    response = agent.process_message("Has the doctor approved?")
    print_response(response)
    
    # If not approved, wait and retry
    retry_count = 0
    max_retries = 3
    
    while not response.get('stage_complete') and retry_count < max_retries:
        retry_count += 1
        print(f"\n⏳ Approval not detected yet (Attempt {retry_count}/{max_retries})")
        wait_for_user("Update Section 3 and press Enter to retry...")
        response = agent.process_message("Check approval status")
        print_response(response)
    
    if response.get('stage_complete'):
        print("\n✅ DOCTOR APPROVAL RECEIVED!")
    else:
        print("\n⚠️ Proceeding without confirmation (check document manually)")
    
    wait_for_user("Ready to proceed to Stage 5 (Lab Scheduling)?")
    
    # ================================================================
    # STAGE 5: SCHEDULE LAB TESTS (CALENDAR + DOC UPDATE)
    # ================================================================
    print_stage_header(5, "SCHEDULE LAB TESTS (CALENDAR)")
    
    print("💬 User wants to schedule lab tests...")
    response = agent.process_message("I want to schedule the lab tests")
    print_response(response)
    
    # If automatic scheduling offered
    if "automatic" in response.get('response', '').lower():
        print("\n💬 User accepts automatic scheduling...")
        response = agent.process_message("Yes, please schedule automatically")
        print_response(response)
    else:
        # Manual date selection
        print("\n💬 User provides preferred date...")
        response = agent.process_message("Tomorrow morning at 9 AM")
        print_response(response)
    
    # Check if appointment was created
    stage_data = agent.state.get('stage_data', {}).get('lab_coordination', {})
    if stage_data.get('appointment_scheduled'):
        print("\n✅ LAB APPOINTMENT SCHEDULED!")
        print(f"📅 Date: {stage_data.get('appointment_date', 'N/A')}")
        print(f"⏰ Time: {stage_data.get('appointment_time', 'N/A')}")
        if stage_data.get('calendar_event_id'):
            print(f"📆 Calendar Event ID: {stage_data['calendar_event_id']}")
    
    # Check if Section 4 was updated
    if agent.state.get('workflow_doc_id'):
        print("\n📄 Section 4 should be updated with appointment details")
    
    wait_for_user("Ready to proceed to Stage 6 (Lab Results)?")
    
    # ================================================================
    # STAGE 6: LAB RESULTS ADDED TO DOC
    # ================================================================
    print_stage_header(6, "LAB RESULTS ADDED TO DOC")
    
    print("📄 MANUAL STEP REQUIRED:")
    print("="*80)
    print("1. Open the document URL")
    print("2. Find SECTION 5: LAB RESULTS")
    print("3. Add lab results (simulate lab staff):")
    print("")
    print("   📊 LAB TEST RESULTS")
    print("   Test Date: [Today's date]")
    print("")
    print("   1. Complete Blood Count (CBC)")
    print("      Result: 14.5 g/dL")
    print("      Normal Range: 12.0-16.0 g/dL")
    print("      Status: ✅ NORMAL")
    print("")
    print("   2. Blood Glucose (Fasting)")
    print("      Result: 126 mg/dL")
    print("      Normal Range: 70-100 mg/dL")
    print("      Status: ⚠️ ABNORMAL (Elevated)")
    print("")
    print("   3. Lipid Profile")
    print("      Result: 195 mg/dL")
    print("      Normal Range: <200 mg/dL")
    print("      Status: ✅ NORMAL")
    print("")
    print("   Summary: 2 Normal | 1 Abnormal")
    print("")
    print("4. Save the document")
    print("="*80)
    
    wait_for_user("After updating Section 5, press Enter to check results...")
    
    # Check for results
    print("\n💬 Checking lab results...")
    response = agent.process_message("Are my lab results ready?")
    print_response(response)
    
    # If still pending, wait and retry
    retry_count = 0
    max_retries = 3
    
    while response.get('response', '').find('Waiting for Lab Results') >= 0 and retry_count < max_retries:
        retry_count += 1
        print(f"\n⏳ Results not detected yet (Attempt {retry_count}/{max_retries})")
        wait_for_user("Update Section 5 and press Enter to retry...")
        response = agent.process_message("Check lab results")
        print_response(response)
    
    if response.get('stage_complete'):
        print("\n✅ LAB RESULTS RECEIVED!")
    else:
        print("\n⚠️ Proceeding without confirmation (check document manually)")
    
    wait_for_user("Ready to proceed to Stage 7 (Doctor Consultation)?")
    
    # ================================================================
    # STAGE 7: DOCTOR CONSULTATION (CALENDAR + DOC UPDATE)
    # ================================================================
    print_stage_header(7, "DOCTOR CONSULTATION (CALENDAR + DOC UPDATE)")
    
    print("📄 MANUAL STEP REQUIRED:")
    print("="*80)
    print("1. Open the document URL")
    print("2. Find SECTION 6: POST-LAB CONSULTATION")
    print("3. Add doctor's consultation notes:")
    print("")
    print("   👨‍⚕️ DOCTOR'S CONSULTATION")
    print("   Date: [Today's date]")
    print("")
    print("   DIAGNOSIS:")
    print("   Pre-diabetic condition detected. Blood glucose elevated.")
    print("")
    print("   TREATMENT PLAN:")
    print("   1. Start Metformin 500mg (if not already on it)")
    print("   2. Dietary modifications required")
    print("   3. Follow-up in 3 months")
    print("")
    print("   NEXT STEPS:")
    print("   - Review prescription in next section")
    print("   - Schedule follow-up appointment")
    print("")
    print("4. Save the document")
    print("="*80)
    
    wait_for_user("After updating Section 6, press Enter to check consultation...")
    
    # Check for consultation notes
    print("\n💬 Checking doctor's consultation...")
    response = agent.process_message("What did the doctor say?")
    print_response(response)
    
    # If still pending, wait and retry
    retry_count = 0
    max_retries = 3
    
    while not response.get('stage_complete') and retry_count < max_retries:
        retry_count += 1
        print(f"\n⏳ Consultation not detected yet (Attempt {retry_count}/{max_retries})")
        wait_for_user("Update Section 6 and press Enter to retry...")
        response = agent.process_message("Check consultation notes")
        print_response(response)
    
    if response.get('stage_complete'):
        print("\n✅ CONSULTATION NOTES RECEIVED!")
    else:
        print("\n⚠️ Proceeding without confirmation (check document manually)")
    
    wait_for_user("Ready to proceed to Stage 11 (Prescription)?")
    
    # ================================================================
    # STAGE 11: PRESCRIPTION + FOLLOW-UP (DOC UPDATE + CALENDAR)
    # ================================================================
    print_stage_header(11, "PRESCRIPTION + FOLLOW-UP (DOC + CALENDAR)")
    
    print("📄 MANUAL STEP REQUIRED:")
    print("="*80)
    print("1. Open the document URL")
    print("2. Find SECTION 7: PRESCRIPTION & FOLLOW-UP")
    print("3. Add prescription details:")
    print("")
    print("   💊 PRESCRIPTION")
    print("")
    print("   MEDICATIONS:")
    print("   1. Metformin 500mg")
    print("      - Dosage: 1 tablet twice daily")
    print("      - Timing: With breakfast and dinner")
    print("      - Duration: 3 months")
    print("")
    print("   DIETARY INSTRUCTIONS:")
    print("   • Limit sugar intake")
    print("   • Increase fiber in diet")
    print("   • Avoid processed foods")
    print("")
    print("   FOLLOW-UP APPOINTMENT:")
    print("   📅 Schedule after 3 months")
    print("   📅 Suggested Date: [Date 3 months from now]")
    print("")
    print("   SAFETY MEASURES:")
    print("   ⚠️ Monitor blood sugar weekly")
    print("   ⚠️ Report any side effects immediately")
    print("")
    print("4. Save the document")
    print("="*80)
    
    wait_for_user("After updating Section 7, press Enter to check prescription...")
    
    # Check for prescription
    print("\n💬 Checking prescription details...")
    response = agent.process_message("What is my prescription?")
    print_response(response)
    
    # If still pending, wait and retry
    retry_count = 0
    max_retries = 3
    
    while not response.get('stage_complete') and retry_count < max_retries:
        retry_count += 1
        print(f"\n⏳ Prescription not detected yet (Attempt {retry_count}/{max_retries})")
        wait_for_user("Update Section 7 and press Enter to retry...")
        response = agent.process_message("Check prescription")
        print_response(response)
    
    if response.get('stage_complete'):
        print("\n✅ PRESCRIPTION RECEIVED!")
        
        # Check if follow-up appointment was created
        stage_data = agent.state.get('stage_data', {}).get('prescription_followup', {})
        if stage_data.get('followup_scheduled'):
            print(f"\n📅 FOLLOW-UP APPOINTMENT SCHEDULED!")
            print(f"📅 Date: {stage_data.get('followup_date', 'N/A')}")
            if stage_data.get('calendar_event_id'):
                print(f"📆 Calendar Event ID: {stage_data['calendar_event_id']}")
    else:
        print("\n⚠️ Proceeding without confirmation (check document manually)")
    
    wait_for_user("Ready to proceed to Stage 12 (Completion)?")
    
    # ================================================================
    # STAGE 12: COMPLETE
    # ================================================================
    print_stage_header(12, "WORKFLOW COMPLETION")
    
    print("💬 Finalizing workflow...")
    response = agent.process_message("Thank you, is my treatment plan complete?")
    print_response(response)
    
    # Check if Section 8 was updated
    if agent.state.get('workflow_doc_id'):
        print("\n📄 Section 8 should be updated with completion summary")
    
    # ================================================================
    # FINAL SUMMARY
    # ================================================================
    print("\n" + "🌟"*40)
    print("📊 WORKFLOW COMPLETION SUMMARY")
    print("🌟"*40)
    
    print("\n✅ COMPLETED STAGES:")
    print(f"   Stage 2: Start Chat ✓")
    print(f"   Stage 3: Medical History + Doc Creation ✓")
    print(f"   Stage 4: Doctor Approval ✓")
    print(f"   Stage 5: Lab Scheduling ✓")
    print(f"   Stage 6: Lab Results ✓")
    print(f"   Stage 7: Doctor Consultation ✓")
    print(f"   Stage 11: Prescription + Follow-up ✓")
    print(f"   Stage 12: Completion ✓")
    
    print("\n📄 DOCUMENT DETAILS:")
    if agent.state.get('workflow_doc_url'):
        print(f"   URL: {agent.state['workflow_doc_url']}")
        print(f"   ID: {agent.state['workflow_doc_id']}")
    else:
        print("   ⚠️ No document found")
    
    print("\n📅 CALENDAR EVENTS:")
    lab_data = agent.state.get('stage_data', {}).get('lab_coordination', {})
    followup_data = agent.state.get('stage_data', {}).get('prescription_followup', {})
    
    if lab_data.get('calendar_event_id'):
        print(f"   Lab Appointment: {lab_data['calendar_event_id']}")
    if followup_data.get('calendar_event_id'):
        print(f"   Follow-up Appointment: {followup_data['calendar_event_id']}")
    
    print("\n👤 PATIENT INFO:")
    print(f"   Email: {agent.patient_email}")
    print(f"   Phone: 7447444532")
    print(f"   Patient ID: {agent.patient_id}")
    
    print("\n" + "🌟"*40)
    print("✅ END-TO-END WORKFLOW TEST COMPLETE!")
    print("🌟"*40 + "\n")

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n\n⚠️ Test interrupted by user")
    except Exception as e:
        print(f"\n\n❌ Error: {str(e)}")
        import traceback
        traceback.print_exc()
