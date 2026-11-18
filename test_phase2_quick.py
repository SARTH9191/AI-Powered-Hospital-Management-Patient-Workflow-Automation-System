"""
🧪 PHASE 2 QUICK TEST - Test from Current Stage
Tests remaining stages based on where patient currently is

Usage: python test_phase2_quick.py
"""

import os
import sys
from datetime import datetime

os.environ['TESTING'] = 'true'

from src.workflow_chat_agent import WorkflowChatAgent


def main():
    print("\n" + "="*80)
    print("  🧪 PHASE 2 QUICK TEST")
    print("  Test from current patient stage")
    print("="*80 + "\n")
    
    # Initialize agent
    print("🚀 Initializing agent for: iamsamarth786@gmail.com\n")
    
    try:
        agent = WorkflowChatAgent(patient_email="iamsamarth786@gmail.com")
        
        patient_id = agent.patient_id
        current_stage = agent.state.get('current_stage', 1)
        doc_id = agent.state.get("workflow_doc_id")
        doc_url = agent.state.get("workflow_doc_url")
        
        print(f"✅ Agent initialized")
        print(f"   Patient ID: {patient_id}")
        print(f"   Current Stage: {current_stage}")
        print(f"   Workflow Doc: {doc_url if doc_url else 'Not created yet'}\n")
        
        print("="*80)
        print("CURRENT STATUS:")
        print("="*80)
        
        # Check stage data
        stage_data = agent.state.get("stage_data", {})
        
        print("\n📋 Stage Completion Status:")
        stages_info = {
            "registration": ("Stage 1", "Registration"),
            "bypass_otp": ("Stage 2", "OTP Verification"),
            "medical_history": ("Stage 3", "Medical History"),
            "test_determination": ("Stage 4", "Test Approval"),
            "lab_scheduling": ("Stage 5", "Lab Scheduling"),
            "lab_results": ("Stage 6", "Lab Results"),
            "doctor_consultation": ("Stage 7", "Doctor Consultation"),
            "followup": ("Stage 11", "Prescription & Follow-up"),
            "completion": ("Stage 12", "Completion")
        }
        
        for key, (stage_num, stage_name) in stages_info.items():
            data = stage_data.get(key, {})
            if data:
                status = "✅ Complete"
                details = []
                
                # Add specific details based on stage
                if key == "lab_scheduling":
                    if data.get("appointment_confirmed"):
                        details.append(f"Apt: {data.get('appointment_date', 'N/A')}")
                    if data.get("calendar_event_id"):
                        details.append("Calendar: ✅")
                
                elif key == "lab_results":
                    if data.get("results_retrieved"):
                        tests = data.get("completed_tests", [])
                        details.append(f"{len(tests)} tests")
                
                elif key == "test_determination":
                    tests = data.get("recommended_tests", [])
                    if tests:
                        details.append(f"{len(tests)} tests approved")
                
                elif key == "doctor_consultation":
                    if data.get("consultation_read"):
                        diagnosis = data.get("diagnosis", "N/A")
                        details.append(f"Diagnosis: {diagnosis[:30]}...")
                
                elif key == "followup":
                    if data.get("prescription_details_read"):
                        meds = data.get("medications", [])
                        details.append(f"{len(meds)} medications")
                    if data.get("followup_scheduled"):
                        details.append("Follow-up: ✅")
                
                detail_str = " | ".join(details) if details else ""
                print(f"   {stage_num:9s} {stage_name:25s} {status:15s} {detail_str}")
            else:
                print(f"   {stage_num:9s} {stage_name:25s} ⏳ Pending")
        
        print("\n" + "="*80)
        print("NEXT ACTIONS:")
        print("="*80 + "\n")
        
        if current_stage == 4:
            print("📍 Waiting for DOCTOR to approve tests in Section 3")
            print(f"   Document: {doc_url}")
            print("   After doctor updates, type: check")
        
        elif current_stage == 5:
            print("📍 Ready to schedule LAB APPOINTMENT")
            print("   Type: Schedule lab appointment for YYYY-MM-DD at HH:MM AM/PM")
        
        elif current_stage == 6:
            print("📍 Waiting for LAB RESULTS in Google Sheet")
            print("   After results added, type: check lab results")
        
        elif current_stage == 7:
            print("📍 Waiting for DOCTOR consultation in Section 6")
            print(f"   Document: {doc_url}")
            print("   After doctor updates, type: check consultation")
        
        elif current_stage == 11:
            print("📍 Waiting for PRESCRIPTION in Section 7")
            print(f"   Document: {doc_url}")
            print("   After doctor updates, type: check prescription")
        
        elif current_stage == 12:
            print("📍 Ready to COMPLETE workflow")
            print("   Type: complete")
        
        else:
            print(f"📍 Currently at Stage {current_stage}")
            print("   Continue with normal conversation")
        
        print("\n" + "="*80)
        print("MANUAL TESTING:")
        print("="*80 + "\n")
        
        print("You can now manually test the workflow:")
        print("1. Open the document and update the required section")
        print("2. Come back here and type the appropriate command")
        print("3. Verify the AI reads and processes correctly")
        print("4. Check calendar for scheduled appointments")
        print("5. Verify document sections are updated\n")
        
        print("Type 'exit' to quit, or start chatting with the AI:\n")
        
        # Interactive chat loop
        while True:
            try:
                user_input = input("You: ").strip()
                
                if user_input.lower() in ['exit', 'quit', 'q']:
                    print("\n👋 Ending test session")
                    break
                
                if not user_input:
                    continue
                
                # Process message
                print("\n🤖 AI Processing...")
                response = agent.process_message(user_input)
                
                print("\n" + "-"*80)
                print(response.get("response", "No response"))
                print("-"*80 + "\n")
                
                # Show updated stage
                new_stage = agent.state.get('current_stage', current_stage)
                if new_stage != current_stage:
                    print(f"📍 Stage changed: {current_stage} → {new_stage}\n")
                    current_stage = new_stage
                
            except KeyboardInterrupt:
                print("\n\n👋 Test interrupted")
                break
            except Exception as e:
                print(f"\n❌ Error: {str(e)}\n")
                import traceback
                traceback.print_exc()
        
        print("\n" + "="*80)
        print("TEST SESSION ENDED")
        print("="*80 + "\n")
        
    except Exception as e:
        print(f"❌ Failed to initialize: {str(e)}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    main()
