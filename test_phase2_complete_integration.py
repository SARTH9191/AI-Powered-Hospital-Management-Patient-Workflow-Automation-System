"""
🧪 PHASE 2 REAL INTEGRATION TEST
Complete end-to-end workflow with REAL Google Workspace interactions

Workflow Stages:
Stage 2: Start (returning user)
Stage 3: Medical history + AI analysis → Create Google Doc
Stage 4: Doctor reviews and approves tests in Doc (YOU UPDATE MANUALLY)
Stage 5: Schedule lab tests → Calendar event + Doc Section 4
Stage 6: Lab results → Doc Section 5 (YOU ADD TO SHEET MANUALLY)
Stage 7: Doctor consultation in Doc (YOU UPDATE MANUALLY)
Stage 11: Prescription + follow-up → Calendar event + Read Doc Section 7
Stage 12: Complete → Doc Section 8

Requirements:
- client_secret.json in credentials folder
- Redis server running
- Existing patient: iamsamarth786@gmail.com
- You will manually update Google Doc as doctor at prompted stages
"""

import os
import sys
import time
from datetime import datetime, timedelta

# Set test environment
os.environ['TESTING'] = 'true'

from src.workflow_chat_agent import WorkflowChatAgent
from tools.unified_workflow_doc_tool import (
    read_doctor_decision,
    read_doctor_consultation,
    read_prescription_details
)
from tools.google_calendar_tool import CreateAppointmentTool


def print_section(title: str):
    """Print formatted section header"""
    print(f"\n{'='*80}")
    print(f"  {title}")
    print(f"{'='*80}\n")


def print_result(test_name: str, passed: bool, details: str = ""):
    """Print test result"""
    status = "✅ PASS" if passed else "❌ FAIL"
    print(f"{status} | {test_name}")
    if details:
        print(f"      {details}")


def wait_for_user_action(action_description: str, doc_url: str = None, section: str = None):
    """Wait for user to manually perform an action"""
    print(f"\n{'='*80}")
    print(f"⏸️  MANUAL ACTION REQUIRED")
    print(f"{'='*80}")
    print(f"\n📋 {action_description}\n")
    
    if doc_url:
        print(f"📄 Document URL: {doc_url}")
    if section:
        print(f"� Section to update: {section}")
    
    print(f"\n{'='*80}")
    input("Press ENTER when you have completed this action... ")
    print("✅ Continuing test...\n")


def test_stage_4_doctor_approval(agent: WorkflowChatAgent):
    """Test Stage 4: Wait for doctor to approve tests in Section 3"""
    print_section("STAGE 4: DOCTOR'S DECISION (MANUAL)")
    
    try:
        doc_id = agent.state.get("workflow_doc_id")
        doc_url = agent.state.get("workflow_doc_url")
        
        if not doc_id:
            print_result("Stage 4 Prerequisites", False, "No workflow document found")
            return False
        
        print(f"📄 Workflow Document: {doc_url}\n")
        
        # Wait for doctor to update Section 3
        wait_for_user_action(
            "Please open the document and update Section 3 with your decision.\n\n"
            "Example format:\n"
            "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n"
            "DOCTOR'S DECISION: ✅ APPROVED FOR LAB TESTS\n\n"
            "RECOMMENDED TESTS:\n"
            "1. Complete Blood Count (CBC)\n"
            "2. Lipid Profile\n"
            "3. Blood Glucose (Fasting)\n\n"
            "SPECIAL INSTRUCTIONS:\n"
            "- 8-12 hour fasting required\n"
            "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━",
            doc_url,
            "Section 3: DOCTOR'S DECISION"
        )
        
        # AI checks the decision
        print("🤖 AI Agent checking doctor's decision...")
        response = agent.process_message("check")
        
        decision_text = response.get("response", "").lower()
        stage_4_passed = "approved" in decision_text or "proceed" in decision_text
        
        print_result("Stage 4 - Doctor approval received", stage_4_passed)
        
        if stage_4_passed:
            # Display approved tests
            test_data = agent.state.get("stage_data", {}).get("test_determination", {})
            recommended_tests = test_data.get("recommended_tests", [])
            print(f"\n   📋 Approved Tests: {', '.join(recommended_tests)}")
        
        return stage_4_passed
        
    except Exception as e:
        print_result("Stage 4 Test", False, f"Error: {str(e)}")
        import traceback
        traceback.print_exc()
        return False


def test_stage_5_lab_scheduling(agent: WorkflowChatAgent):
    """Test Stage 5: Lab scheduling with Section 4 update and calendar"""
    print_section("STAGE 5: LAB APPOINTMENT SCHEDULING")
    
    try:
        doc_id = agent.state.get("workflow_doc_id")
        doc_url = agent.state.get("workflow_doc_url")
        
        if not doc_id:
            print_result("Stage 5 Prerequisites", False, "No workflow document found")
            return False
        
        # Get recommended tests from Stage 4
        test_data = agent.state.get("stage_data", {}).get("test_determination", {})
        recommended_tests = test_data.get("recommended_tests", [])
        
        if not recommended_tests:
            print_result("Stage 5 Prerequisites", False, "No approved tests found")
            return False
        
        print(f"📋 Scheduling tests: {', '.join(recommended_tests)}\n")
        
        # Schedule lab appointment
        print("🔄 Requesting lab appointment scheduling...")
        target_date = (datetime.now() + timedelta(days=3)).strftime('%Y-%m-%d')
        
        print(f"   Requesting: {target_date} at 8:30 AM\n")
        schedule_message = f"Schedule lab appointment for {target_date} at 8:30 AM"
        
        response = agent.process_message(schedule_message)
        
        # Verify appointment was scheduled
        time.sleep(3)
        stage_5_data = agent.state.get("stage_data", {}).get("lab_scheduling", {})
        appointment_confirmed = stage_5_data.get("appointment_confirmed", False)
        calendar_event_id = stage_5_data.get("calendar_event_id")
        
        print_result("✅ Appointment scheduled", appointment_confirmed)
        print_result("✅ Calendar event created", bool(calendar_event_id),
                    f"Event ID: {calendar_event_id}")
        
        # Verify Section 4 update
        print("\n� Verifying Section 4 was updated in document...")
        time.sleep(2)
        
        from google.oauth2.credentials import Credentials
        from google_auth_oauthlib.flow import InstalledAppFlow
        from googleapiclient.discovery import build
        import pickle
        
        # Load OAuth credentials
        creds = None
        if os.path.exists('credentials/token.pickle'):
            with open('credentials/token.pickle', 'rb') as token:
                creds = pickle.load(token)
        else:
            flow = InstalledAppFlow.from_client_secrets_file(
                'credentials/client_secret.json',
                scopes=['https://www.googleapis.com/auth/documents.readonly']
            )
            creds = flow.run_local_server(port=0)
            with open('credentials/token.pickle', 'wb') as token:
                pickle.dump(creds, token)
        
        docs_service = build('docs', 'v1', credentials=creds)
        document = docs_service.documents().get(documentId=doc_id).execute()
        content = document.get('body', {}).get('content', [])
        
        # Extract text
        full_text = ""
        for element in content:
            if 'paragraph' in element:
                for text_run in element['paragraph'].get('elements', []):
                    if 'textRun' in text_run:
                        full_text += text_run['textRun'].get('content', '')
        
        section_4_found = "4: LAB TEST SCHEDULING" in full_text
        appointment_in_doc = target_date in full_text
        
        print_result("✅ Section 4 created", section_4_found)
        print_result("✅ Appointment details in doc", appointment_in_doc)
        
        # Open document for user verification
        print(f"\n📄 Check the document: {doc_url}")
        print("   Look for Section 4 with appointment details and calendar link")
        
        stage_5_passed = appointment_confirmed and calendar_event_id and section_4_found
        
        print(f"\n{'='*80}")
        if stage_5_passed:
            print("✅ STAGE 5 COMPLETE: Lab appointment scheduled + Calendar + Doc updated")
        else:
            print("❌ STAGE 5 FAILED")
        print(f"{'='*80}")
        
        return stage_5_passed
        
    except Exception as e:
        print_result("Stage 5 Test", False, f"Error: {str(e)}")
        import traceback
        traceback.print_exc()
        return False


def test_stage_6_lab_results(agent: WorkflowChatAgent):
    """Test Stage 6: Lab results - Doctor adds to Section 5, AI reads from Section 5"""
    print_section("STAGE 6: LAB RESULTS (DOC-BASED)")
    
    try:
        doc_id = agent.state.get("workflow_doc_id")
        doc_url = agent.state.get("workflow_doc_url")
        
        if not doc_id:
            print_result("Stage 6 Prerequisites", False, "No workflow document found")
            return False
        
        print("\n" + "="*80)
        print("📋 MANUAL ACTION REQUIRED: ADD LAB RESULTS TO SECTION 5 OF DOC")
        print("="*80)
        print("\n🔄 Stage 6 Workflow (FULLY DOC-BASED):")
        print("   1. ✅ Lab staff adds results to Section 5 of Document")
        print("   2. ✅ AI reads results from Section 5")
        print("   3. ✅ AI displays to patient")
        print("\n📄 Document URL:", doc_url)
        print("📍 Section to update: Section 5 (LAB RESULTS)")
        print("\n" + "━"*80)
        print("Add the following content to Section 5:")
        print("━"*80)
        
        test_date = datetime.now().strftime('%Y-%m-%d')
        
        section_5_content = f"""
TEST DATE: {test_date} | TIME: 10:30

RESULTS SUMMARY:
✅ Normal: 3 tests
⚠️ Abnormal: 1 test

DETAILED RESULTS:

1. Complete Blood Count (CBC)
   Result: 14.5 g/dL
   Normal Range: 13.0-17.0 g/dL
   Status: ✅ NORMAL

2. Blood Glucose (Fasting)
   Result: 126 mg/dL
   Normal Range: 70-100 mg/dL
   Status: ⚠️ ABNORMAL
   Clinical Significance: Pre-diabetic range

3. Lipid Profile
   Result: 195 mg/dL
   Normal Range: <200 mg/dL
   Status: ✅ NORMAL

4. Liver Function Test
   Result: Within normal limits
   Normal Range: Normal
   Status: ✅ NORMAL

ABNORMAL FLAGS:
⚠️ Blood Glucose (Fasting) - Pre-diabetic range, requires dietary management and follow-up

AI ANALYSIS:
Overall health status shows one area of concern. Your Complete Blood Count and Lipid Profile are within healthy ranges - great job! 

However, your fasting blood glucose (126 mg/dL) is elevated, indicating pre-diabetes. This is manageable with lifestyle changes including:
- Balanced diet with reduced sugar intake
- Regular exercise (30 minutes daily)
- Weight management
- Regular monitoring

Your liver function is normal, which is excellent. Recommend follow-up glucose testing in 3 months.

Updated by: Lab System
Last Updated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
"""
        
        print(section_5_content)
        print("━"*80)
        print("\n� Instructions:")
        print("   1. Open the document: " + doc_url)
        print("   2. Find Section 5: LAB RESULTS")
        print("   3. Copy the content above and paste it into Section 5")
        print("   4. Save the document")
        print("\n" + "="*80)
        input("Press ENTER when you have updated Section 5...")
        print("="*80 + "\n")
        
        # AI checks lab results from Section 5
        print("🤖 AI Agent reading lab results from Section 5...")
        response = agent.process_message("check")
        
        # Verify results were retrieved
        time.sleep(3)
        stage_6_data = agent.state.get("stage_data", {}).get("lab_results", {})
        results_retrieved = stage_6_data.get("results_retrieved", False)
        
        print_result("✅ Lab results fetched", results_retrieved)
        
        if results_retrieved:
            completed_tests = stage_6_data.get("completed_tests", [])
            print(f"   📋 Retrieved {len(completed_tests)} test results")
        
        # Verify Section 5 update
        print("\n� Verifying Section 5 was updated in document...")
        time.sleep(2)
        
        from google.oauth2.credentials import Credentials
        from googleapiclient.discovery import build
        import pickle
        
        creds = None
        if os.path.exists('credentials/token.pickle'):
            with open('credentials/token.pickle', 'rb') as token:
                creds = pickle.load(token)
        
        docs_service = build('docs', 'v1', credentials=creds)
        document = docs_service.documents().get(documentId=doc_id).execute()
        content = document.get('body', {}).get('content', [])
        
        full_text = ""
        for element in content:
            if 'paragraph' in element:
                for text_run in element['paragraph'].get('elements', []):
                    if 'textRun' in text_run:
                        full_text += text_run['textRun'].get('content', '')
        
        section_5_found = "5: LAB RESULTS" in full_text
        results_in_doc = "RESULTS SUMMARY" in full_text or "Normal:" in full_text
        
        print_result("✅ Section 5 created", section_5_found)
        print_result("✅ Results in document", results_in_doc)
        
        print(f"\n📄 Check the document: {doc_url}")
        print("   Look for Section 5 with lab results and AI analysis")
        
        stage_6_passed = results_retrieved and section_5_found
        
        print(f"\n{'='*80}")
        if stage_6_passed:
            print("✅ STAGE 6 COMPLETE: Lab results fetched + Doc Section 5 updated")
        else:
            print("❌ STAGE 6 FAILED")
        print(f"{'='*80}")
        
        return stage_6_passed
        
    except Exception as e:
        print_result("Stage 6 Test", False, f"Error: {str(e)}")
        import traceback
        traceback.print_exc()
        return False


def test_stage_7_consultation(agent: WorkflowChatAgent):
    """Test Stage 7: Doctor consultation"""
    print_section("STAGE 7: POST-LAB CONSULTATION (MANUAL)")
    
    try:
        doc_id = agent.state.get("workflow_doc_id")
        doc_url = agent.state.get("workflow_doc_url")
        
        if not doc_id:
            print_result("Stage 7 Prerequisites", False, "No workflow document found")
            return False
        
        # Wait for doctor to update Section 6
        wait_for_user_action(
            "Please update Section 6 with post-lab consultation.\n\n"
            "Example format:\n"
            "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n"
            "POST-LAB CONSULTATION NOTES\n\n"
            "DIAGNOSIS: Pre-diabetes mellitus\n\n"
            "CLINICAL ASSESSMENT:\n"
            "Based on lab results:\n"
            "- Blood glucose: 126 mg/dL (elevated)\n"
            "- Other parameters: Normal\n\n"
            "TREATMENT PLAN:\n"
            "1. Lifestyle modifications\n"
            "2. Medication for glucose control\n"
            "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━",
            doc_url,
            "Section 6: POST-LAB CONSULTATION"
        )
        
        # AI reads consultation
        print("🤖 AI Agent reading consultation notes...")
        response = agent.process_message("check consultation")
        
        consultation_text = response.get("response", "").lower()
        stage_7_passed = "diagnosis" in consultation_text or "treatment" in consultation_text
        
        print_result("✅ Consultation notes read", stage_7_passed)
        
        if stage_7_passed:
            consultation_data = agent.state.get("stage_data", {}).get("doctor_consultation", {})
            diagnosis = consultation_data.get("diagnosis", "N/A")
            print(f"   📋 Diagnosis: {diagnosis}")
        
        print(f"\n{'='*80}")
        if stage_7_passed:
            print("✅ STAGE 7 COMPLETE: Doctor consultation read from Section 6")
        else:
            print("❌ STAGE 7 FAILED")
        print(f"{'='*80}")
        
        return stage_7_passed
        
    except Exception as e:
        print_result("Stage 7 Test", False, f"Error: {str(e)}")
        import traceback
        traceback.print_exc()
        return False


def test_stage_11_prescription_reading(agent: WorkflowChatAgent):
    """Test Stage 11: Prescription reading from Section 7 + Follow-up calendar"""
    print_section("STAGE 11: PRESCRIPTION & FOLLOW-UP (MANUAL)")
    
    try:
        doc_id = agent.state.get("workflow_doc_id")
        doc_url = agent.state.get("workflow_doc_url")
        
        if not doc_id:
            print_result("Stage 11 Prerequisites", False, "No workflow document found")
            return False
        
        # Wait for doctor to update Section 7
        follow_up_date = (datetime.now() + timedelta(days=90)).strftime('%Y-%m-%d')
        
        wait_for_user_action(
            f"Please update Section 7 with prescription details.\n\n"
            "Example format:\n"
            "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n"
            "PRESCRIPTION & FOLLOW-UP PLAN\n\n"
            "💊 MEDICATIONS PRESCRIBED:\n\n"
            "1. Metformin 500mg\n"
            "   Dosage: 1 tablet twice daily\n"
            "   Timing: With breakfast and dinner\n"
            "   Duration: 3 months\n"
            "   Purpose: Blood glucose control\n\n"
            "⚠️ SAFETY MEASURES:\n"
            "• Monitor blood sugar weekly\n"
            "• Avoid alcohol\n\n"
            "🍽️ DIETARY INSTRUCTIONS:\n"
            "• Limit sugar intake\n"
            "• Increase fiber\n\n"
            f"📅 FOLLOW-UP SCHEDULE:\n"
            f"Follow-up Date: {follow_up_date}\n"
            "Tests Required: Fasting glucose, HbA1c\n"
            "Location: City Hospital OPD\n"
            "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━",
            doc_url,
            "Section 7: PRESCRIPTION & FOLLOW-UP"
        )
        
        # AI reads prescription
        print("🤖 AI Agent reading prescription from Section 7...")
        response = agent.process_message("check prescription")
        
        # Verify prescription was read and parsed
        time.sleep(3)
        stage_11_data = agent.state.get("stage_data", {}).get("followup", {})
        prescription_read = stage_11_data.get("prescription_details_read", False)
        medications = stage_11_data.get("medications", [])
        followup_scheduled = stage_11_data.get("followup_scheduled", False)
        calendar_event_id = stage_11_data.get("calendar_event_id")
        
        print_result("✅ Prescription read from Section 7", prescription_read)
        print_result("✅ Medications parsed", len(medications) > 0,
                    f"Found {len(medications)} medications")
        
        # Display parsed medications
        if medications:
            print("\n   📋 Parsed Medications:")
            for idx, med in enumerate(medications, 1):
                print(f"\n      {idx}. {med.get('name', 'Unknown')}")
                print(f"         Dosage: {med.get('dosage', 'N/A')}")
                print(f"         Timing: {med.get('timing', 'N/A')}")
                print(f"         Duration: {med.get('duration', 'N/A')}")
        
        print_result("\n✅ Follow-up appointment scheduled", followup_scheduled,
                    f"Event ID: {calendar_event_id}")
        
        stage_11_passed = prescription_read and len(medications) > 0 and followup_scheduled
        
        print(f"\n{'='*80}")
        if stage_11_passed:
            print("✅ STAGE 11 COMPLETE: Prescription read + Parsed + Follow-up calendar created")
        else:
            print("❌ STAGE 11 FAILED")
        print(f"{'='*80}")
        
        return stage_11_passed
        
    except Exception as e:
        print_result("Stage 11 Test", False, f"Error: {str(e)}")
        import traceback
        traceback.print_exc()
        return False


def test_stage_12_completion(agent: WorkflowChatAgent):
    """Test Stage 12: Completion with Section 8 update"""
    print_section("STAGE 12: WORKFLOW COMPLETION")
    
    try:
        doc_id = agent.state.get("workflow_doc_id")
        doc_url = agent.state.get("workflow_doc_url")
        
        if not doc_id:
            print_result("Stage 12 Prerequisites", False, "No workflow document found")
            return False
        
        # Trigger completion
        print("🔄 Triggering workflow completion...")
        response = agent.process_message("complete")
        
        # Verify completion
        time.sleep(3)
        stage_12_data = agent.state.get("stage_data", {}).get("completion", {})
        completion_triggered = stage_12_data.get("completion_triggered", False)
        
        print_result("✅ Completion triggered", completion_triggered)
        
        # Verify Section 8 update
        print("\n� Verifying Section 8 was updated in document...")
        time.sleep(2)
        
        from google.oauth2.credentials import Credentials
        from googleapiclient.discovery import build
        import pickle
        
        creds = None
        if os.path.exists('credentials/token.pickle'):
            with open('credentials/token.pickle', 'rb') as token:
                creds = pickle.load(token)
        
        docs_service = build('docs', 'v1', credentials=creds)
        document = docs_service.documents().get(documentId=doc_id).execute()
        content = document.get('body', {}).get('content', [])
        
        full_text = ""
        for element in content:
            if 'paragraph' in element:
                for text_run in element['paragraph'].get('elements', []):
                    if 'textRun' in text_run:
                        full_text += text_run['textRun'].get('content', '')
        
        section_8_found = "8: WORKFLOW COMPLETION" in full_text
        completion_status = "COMPLETED" in full_text
        journey_summary = "JOURNEY SUMMARY" in full_text or "Stage" in full_text
        
        print_result("✅ Section 8 created", section_8_found)
        print_result("✅ Completion status in doc", completion_status)
        print_result("✅ Journey summary in doc", journey_summary)
        
        print(f"\n📄 Check the final document: {doc_url}")
        print("   Look for Section 8 with complete journey summary")
        
        stage_12_passed = completion_triggered and section_8_found and completion_status
        
        print(f"\n{'='*80}")
        if stage_12_passed:
            print("✅ STAGE 12 COMPLETE: Workflow completed + Section 8 updated")
        else:
            print("❌ STAGE 12 FAILED")
        print(f"{'='*80}")
        
        return stage_12_passed
        
    except Exception as e:
        print_result("Stage 12 Test", False, f"Error: {str(e)}")
        import traceback
        traceback.print_exc()
        return False


def main():
    """Run complete Phase 2 integration test"""
    print("\n" + "="*80)
    print("  🧪 PHASE 2 COMPLETE INTEGRATION TEST SUITE")
    print("  Testing Stages 5, 6, 11, 12 with Unified Document")
    print("="*80 + "\n")
    
    print("📋 Test Configuration:")
    print(f"   • Test Patient: iamsamarth786@gmail.com (Existing)")
    print(f"   • Phone: 7447444532")
    print(f"   • Environment: {'TESTING' if os.environ.get('TESTING') == 'true' else 'PRODUCTION'}")
    print(f"   • OTP Bypass: {'ENABLED' if os.environ.get('BYPASS_OTP') == 'true' else 'DISABLED'}")
    print(f"   • Start Time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
    
    # Initialize agent with existing patient
    print("🚀 Initializing WorkflowChatAgent with existing patient...")
    try:
        agent = WorkflowChatAgent(
            patient_email="iamsamarth786@gmail.com"
        )
        print("✅ Agent initialized successfully")
        print(f"   • Patient ID: {agent.patient_id}")
        print(f"   • Current Stage: {agent.state.get('current_stage', 1)}\n")
    except Exception as e:
        print(f"❌ Failed to initialize agent: {str(e)}")
        return
    
    # Check if workflow document exists (from previous stages)
    doc_id = agent.state.get("workflow_doc_id")
    if not doc_id:
        print("⚠️ No workflow document found. Running prerequisite stages...")
        
        # Run Stage 2 (bypass OTP if needed)
        current_stage = agent.state.get('current_stage', 1)
        if current_stage == 1:
            print("\n🔄 Running Stage 2: Bypass OTP...")
            agent.process_message("bypass")
            time.sleep(2)
        
        # Run Stage 3 (create workflow document)
        current_stage = agent.state.get('current_stage', 1)
        if current_stage <= 2:
            print("\n🔄 Running Stage 3: Medical History...")
            response = agent.process_message("I have fever, headache and fatigue for 3 days. Also experiencing body aches.")
            
            # Wait for document creation
            time.sleep(3)
            
            doc_id = agent.state.get("workflow_doc_id")
            if not doc_id:
                print("❌ Failed to create workflow document")
                print(f"   Response: {response.get('response', 'No response')[:200]}")
                return
            
            print(f"✅ Workflow document created: {doc_id}\n")
    else:
        print(f"✅ Using existing workflow document: {doc_id}\n")
    
    # Refresh doc_id in case it was just created
    doc_id = agent.state.get("workflow_doc_id")
    if not doc_id:
        print("❌ Cannot proceed without workflow document")
        return
    
    # Track test results
    results = {
        "stage_5": False,
        "stage_6": False,
        "stage_11": False,
        "stage_12": False
    }
    
    # Run tests sequentially (stages depend on each other)
    
    # Test 1: Stage 5 - Lab Scheduling
    results["stage_5"] = test_stage_5_lab_scheduling(agent)
    time.sleep(3)
    
    # Test 2: Stage 6 - Lab Results
    results["stage_6"] = test_stage_6_lab_results(agent)
    time.sleep(3)
    
    # Test 3: Stage 11 - Prescription & Follow-up
    results["stage_11"] = test_stage_11_prescription_reading(agent)
    time.sleep(3)
    
    # Test 4: Stage 12 - Completion
    results["stage_12"] = test_stage_12_completion(agent)
    
    # Print final summary
    print_section("FINAL TEST SUMMARY")
    
    print("📊 Test Results:\n")
    print(f"   Stage 5 (Lab Scheduling):     {'✅ PASS' if results['stage_5'] else '❌ FAIL'}")
    print(f"   Stage 6 (Lab Results):        {'✅ PASS' if results['stage_6'] else '❌ FAIL'}")
    print(f"   Stage 11 (Prescription):      {'✅ PASS' if results['stage_11'] else '❌ FAIL'}")
    print(f"   Stage 12 (Completion):        {'✅ PASS' if results['stage_12'] else '❌ FAIL'}")
    
    total_passed = sum(results.values())
    total_tests = len(results)
    pass_rate = (total_passed / total_tests) * 100
    
    print(f"\n   {'='*60}")
    print(f"   TOTAL: {total_passed}/{total_tests} tests passed ({pass_rate:.1f}%)")
    print(f"   {'='*60}\n")
    
    if total_passed == total_tests:
        print("   🎉 ALL TESTS PASSED! Phase 2 integration is working correctly!")
        print(f"   📄 Workflow Document: https://docs.google.com/document/d/{doc_id}")
    else:
        print("   ⚠️ Some tests failed. Please review the failures above.")
    
    print(f"\n   End Time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("="*80 + "\n")


if __name__ == "__main__":
    main()
