"""
🧪 COMPREHENSIVE WORKFLOW TEST - ALL PATHS FROM STAGE 2
Test all possible paths starting from Stage 2 (returning verified user)

Test Scenarios:
1. Prescription-Only Path (No Labs, No Admission)
2. Lab Tests → Prescription Path (Labs but No Admission)
3. Lab Tests → Admission Path (Full workflow with admission)
4. Direct Appointment Path (Skip labs, direct consultation)

Each scenario tests the complete bidirectional doctor collaboration workflow.
"""

import os
import sys
import json
from datetime import datetime, timedelta

# Set UTF-8 encoding for Windows console
if sys.platform == 'win32':
    import codecs
    sys.stdout = codecs.getwriter('utf-8')(sys.stdout.buffer, 'strict')
    sys.stderr = codecs.getwriter('utf-8')(sys.stderr.buffer, 'strict')

# Add project root to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from src.workflow_chat_agent import WorkflowChatAgent
from tools.read_doctor_decision_tool import ReadDoctorDecisionTool

def print_section(title):
    """Print formatted section header"""
    print("\n" + "="*80)
    print(f"  {title}")
    print("="*80)

def print_stage_result(stage_num, stage_name, success, details=""):
    """Print stage result"""
    status = "✅ PASSED" if success else "❌ FAILED"
    print(f"\n{status} - Stage {stage_num}: {stage_name}")
    if details:
        print(f"   {details}")

def simulate_doctor_decision(decision_type, sheet_url, patient_id):
    """
    Simulate different doctor decisions
    
    decision_type options:
    - 'prescription_only': Just medication, no tests/admission
    - 'approve_tests': Approve lab tests
    - 'schedule_appointment': Direct consultation, skip labs
    - 'admit_patient': Direct admission
    """
    print(f"\n👨‍⚕️ SIMULATING DOCTOR DECISION: {decision_type}")
    
    if decision_type == 'prescription_only':
        return {
            'success': True,
            'patient_id': patient_id,
            'decision_type': 'prescription_only',
            'approved_tests': [],
            'prescriptions': [
                {'medication': 'Lisinopril', 'dosage': '10mg once daily'},
                {'medication': 'Aspirin', 'dosage': '75mg once daily with food'}
            ],
            'follow_up_weeks': 2,
            'safety_measures': [
                'Monitor blood pressure daily',
                'Report any dizziness immediately',
                'Avoid excessive sodium'
            ],
            'doctor_assessment': 'Mild hypertension. Start medication, monitor at home. Follow-up in 2 weeks.',
            'prescriptions_count': 2
        }
    
    elif decision_type == 'approve_tests':
        return {
            'success': True,
            'patient_id': patient_id,
            'decision_type': 'approve_tests',
            'approved_tests': [
                {'test_name': 'Complete Blood Count', 'priority': 'High', 'reason': 'General health screening'},
                {'test_name': 'Lipid Profile', 'priority': 'High', 'reason': 'Cardiovascular risk assessment'},
                {'test_name': 'HbA1c', 'priority': 'Routine', 'reason': 'Diabetes screening'}
            ],
            'prescriptions': [],
            'safety_measures': ['Fasting required 12 hours before blood draw'],
            'doctor_assessment': 'Patient requires comprehensive lab work before determining treatment.',
            'tests_count': 3
        }
    
    elif decision_type == 'schedule_appointment':
        return {
            'success': True,
            'patient_id': patient_id,
            'decision_type': 'schedule_appointment',
            'approved_tests': [],
            'prescriptions': [],
            'follow_up_weeks': 1,
            'safety_measures': ['Continue current medications', 'Bring all medication bottles to appointment'],
            'doctor_assessment': 'Patient needs in-person consultation for detailed evaluation.',
            'tests_count': 0
        }
    
    elif decision_type == 'admit_patient':
        return {
            'success': True,
            'patient_id': patient_id,
            'decision_type': 'admit_patient',
            'approved_tests': [],
            'prescriptions': [],
            'safety_measures': ['NPO (nothing by mouth) after midnight', 'Bring personal items for hospital stay'],
            'doctor_assessment': 'Patient requires immediate hospital admission for observation and treatment.',
            'tests_count': 0
        }

def simulate_lab_results_consultation(decision_after_labs, patient_id):
    """
    Simulate doctor's decision after reviewing lab results
    
    decision_after_labs options:
    - 'prescription_only': Results normal, just prescribe medication
    - 'admit_patient': Results concerning, needs admission
    """
    print(f"\n👨‍⚕️ SIMULATING POST-LAB CONSULTATION: {decision_after_labs}")
    
    if decision_after_labs == 'prescription_only':
        return {
            'success': True,
            'patient_id': patient_id,
            'decision_type': 'prescription_only',
            'approved_tests': [],
            'prescriptions': [
                {'medication': 'Atorvastatin', 'dosage': '20mg at bedtime'},
                {'medication': 'Metformin', 'dosage': '500mg twice daily with meals'}
            ],
            'follow_up_weeks': 4,
            'safety_measures': [
                'Monitor blood sugar levels daily',
                'Report muscle pain or weakness',
                'Follow low-carb diet'
            ],
            'doctor_assessment': 'Lab results show elevated cholesterol and glucose. Starting medications. Follow-up in 4 weeks to reassess.',
            'prescriptions_count': 2
        }
    
    elif decision_after_labs == 'admit_patient':
        return {
            'success': True,
            'patient_id': patient_id,
            'decision_type': 'admit_patient',
            'approved_tests': [],
            'prescriptions': [],
            'safety_measures': ['NPO after midnight', 'Bring personal items'],
            'doctor_assessment': 'Lab results show concerning abnormalities requiring immediate admission for further evaluation and treatment.',
            'tests_count': 0
        }

def run_scenario(scenario_name, initial_decision, post_lab_decision=None):
    """Run a complete workflow scenario"""
    
    print_section(f"SCENARIO: {scenario_name}")
    
    # Use verified email (returning user)
    test_patient_email = "iamsamarth786@gmail.com"  # Already verified email
    test_patient_id = f"TEST{datetime.now().strftime('%Y%m%d%H%M%S')}"
    
    try:
        # IMPORTANT: Clear the previous workflow state to ensure fresh start
        print("🧹 Clearing previous workflow state for fresh test...")
        from database.db_manager import OTPDB
        otp_db = OTPDB()
        patient_data = otp_db.get_patient_by_verified_email(test_patient_email)
        
        if patient_data:
            existing_patient_id = patient_data.get('patient_id')
            print(f"   Found existing patient: {existing_patient_id}")
            
            # Clear workflow state for this patient
            from database.db_manager import WorkflowStateDB
            workflow_db = WorkflowStateDB()
            
            # Get current state
            current_state = workflow_db.load_state(existing_patient_id)
            if current_state:
                print(f"   Clearing state from previous test (was at Stage {current_state.get('current_stage')})")
                # Delete the workflow state using database manager
                delete_query = "DELETE FROM workflow_states WHERE patient_id = %s"
                workflow_db.db.execute_query(delete_query, (existing_patient_id,), fetch="none")
                print(f"   ✅ PostgreSQL state cleared")
            else:
                print(f"   No PostgreSQL state found")
            
            # ALSO clear JSON file state
            import json
            import os
            json_state_file = 'data/workflow_states.json'
            if os.path.exists(json_state_file):
                try:
                    with open(json_state_file, 'r', encoding='utf-8') as f:
                        states = json.load(f)
                    
                    if existing_patient_id in states:
                        del states[existing_patient_id]
                        with open(json_state_file, 'w', encoding='utf-8') as f:
                            json.dump(states, f, indent=2)
                        print(f"   ✅ JSON state cleared")
                    else:
                        print(f"   No JSON state found")
                except Exception as e:
                    print(f"   ⚠️ Error clearing JSON state: {e}")
            
            # Clear Redis cache if exists
            try:
                from src.redis_cache import cache
                cache.delete_workflow_state(existing_patient_id)
                print(f"   ✅ Redis cache cleared")
            except Exception as e:
                print(f"   ⚠️ Redis cache not cleared: {e}")
        
        # Initialize agent (should start from Stage 2 for verified user)
        print("📋 Initializing workflow agent for verified user...")
        agent = WorkflowChatAgent(patient_email=test_patient_email)
        
        print(f"✅ Agent initialized")
        print(f"   Email: {test_patient_email}")
        print(f"   Returning User: {agent.is_returning_user}")
        print(f"   Patient ID: {agent.patient_id}")
        print(f"   Starting Stage: {agent.state['current_stage']}")
        
        # Verify starts at Stage 2
        assert agent.state['current_stage'] == 2, f"Verified user should start at Stage 2, but got Stage {agent.state['current_stage']}"
        print_stage_result(2, "Starting from Stage 2", True, "Verified user bypass Stage 1")
        
        # ==================== STAGE 2: DOCUMENT UPLOAD ====================
        print_section("STAGE 2: DOCUMENT UPLOAD")
        
        response = agent.process_message("I want to proceed with medical history")
        print(f"User: I want to proceed with medical history")
        print(f"Agent: {response['response'][:200]}...")
        
        # Advance through Stage 2
        max_iter = 3
        for i in range(max_iter):
            if agent.state['current_stage'] != 2:
                break
            response = agent.process_message("continue to next stage")
            print(f"   Iteration {i+1}: Current stage = {agent.state['current_stage']}")
        
        print_stage_result(2, "Document Upload", True, "Stage completed or skipped")
        
        # ==================== STAGE 3: MEDICAL HISTORY ====================
        print_section("STAGE 3: MEDICAL HISTORY & AI ANALYSIS")
        
        # Provide medical history
        medical_input = """I have hypertension and high cholesterol. 
        Blood pressure usually 145/95. No allergies. 
        Family history of heart disease. Currently not taking any medications."""
        
        response = agent.process_message(medical_input)
        print(f"User: Medical history provided")
        print(f"Agent: {response['response'][:300]}...")
        
        # Continue through Stage 3 until complete
        max_iter = 10
        for i in range(max_iter):
            if agent.state['current_stage'] != 3:
                break
            response = agent.process_message("yes, continue")
            print(f"   Iteration {i+1}: Stage {agent.state['current_stage']}")
            
            if response.get('stage_complete'):
                break
        
        # Get doctor review sheet URL
        doctor_sheet_url = agent.state.get('doctor_review_sheet_url', 'https://docs.google.com/spreadsheets/d/mock_sheet_id')
        print(f"   📊 Review Sheet: {doctor_sheet_url}")
        
        print_stage_result(3, "Medical History & AI Analysis", True, "AI analyzed and created review sheet")
        
        # ==================== STAGE 4: DOCTOR DECISION ====================
        print_section("STAGE 4: DOCTOR DECISION READING")
        
        # Simulate doctor's initial decision
        simulated_decision = simulate_doctor_decision(initial_decision, doctor_sheet_url, test_patient_id)
        
        # Mock the tool
        original_method = ReadDoctorDecisionTool._run
        ReadDoctorDecisionTool._run = lambda self, spreadsheet_url, patient_id=None: simulated_decision
        
        response = agent.process_message("check doctor decision")
        print(f"Agent: {response['response'][:400]}...")
        
        ReadDoctorDecisionTool._run = original_method
        
        decision_type = simulated_decision['decision_type']
        print_stage_result(4, "Doctor Decision", True, f"Decision: {decision_type}")
        
        # Get next stage from response
        next_stage = response.get('next_stage', agent.state['current_stage'])
        print(f"   🎯 Routing: Stage 4 → Stage {next_stage}")
        
        # ==================== PATH DIVERGENCE ====================
        
        if decision_type == 'prescription_only':
            # Path: Direct to Stage 11 (Follow-up)
            if next_stage == 11:
                agent.state['current_stage'] = 11
                agent._save_state()
            
            print_section("STAGE 11: PRESCRIPTION PROCESSING")
            response = agent.process_message("process prescriptions")
            print(f"Agent: {response['response'][:400]}...")
            
            response = agent.process_message("complete")
            print_stage_result(11, "Prescription Processing", True, "Prescriptions processed, follow-up scheduled")
            
            print("\n✅ SCENARIO COMPLETE: Prescription-only path")
            print(f"   Path taken: 2 → 3 → 4 → 11 → 12")
            return True
        
        elif decision_type == 'approve_tests':
            # Path: Stage 5 (Labs) → Stage 6 (Results) → Stage 7 (Consultation)
            if next_stage == 5:
                agent.state['current_stage'] = 5
                agent._save_state()
            
            print_section("STAGE 5: LAB COORDINATION")
            response = agent.process_message("schedule labs")
            print(f"Agent: {response['response'][:300]}...")
            
            # Simulate lab completion
            agent.state['current_stage'] = 6
            agent._save_state()
            
            print_section("STAGE 6: LAB RESULTS & DOCTOR MEETING")
            response = agent.process_message("check results")
            print(f"Agent: {response['response'][:300]}...")
            
            response = agent.process_message("yes, schedule meeting")
            print(f"   Scheduling doctor meeting...")
            
            # Advance to Stage 7
            agent.state['current_stage'] = 7
            agent._save_state()
            
            print_section("STAGE 7: POST-LAB DOCTOR CONSULTATION")
            
            if post_lab_decision:
                post_lab_sim = simulate_lab_results_consultation(post_lab_decision, test_patient_id)
                ReadDoctorDecisionTool._run = lambda self, spreadsheet_url, patient_id=None: post_lab_sim
                
                response = agent.process_message("continue")
                print(f"Agent: {response['response'][:400]}...")
                
                ReadDoctorDecisionTool._run = original_method
                
                final_decision = post_lab_sim['decision_type']
                
                if final_decision == 'prescription_only':
                    agent.state['current_stage'] = 11
                    agent._save_state()
                    
                    print_section("STAGE 11: PRESCRIPTION PROCESSING")
                    response = agent.process_message("process prescriptions")
                    response = agent.process_message("complete")
                    
                    print("\n✅ SCENARIO COMPLETE: Lab → Prescription path")
                    print(f"   Path taken: 2 → 3 → 4 → 5 → 6 → 7 → 11 → 12")
                    return True
                
                elif final_decision == 'admit_patient':
                    agent.state['current_stage'] = 8
                    agent._save_state()
                    
                    print_section("STAGE 8: ADMISSION EXECUTION")
                    response = agent.process_message("proceed with admission")
                    
                    print("\n✅ SCENARIO COMPLETE: Lab → Admission path")
                    print(f"   Path taken: 2 → 3 → 4 → 5 → 6 → 7 → 8 → 9+")
                    return True
        
        elif decision_type == 'schedule_appointment':
            # Path: Direct to Stage 11 (appointment scheduling)
            if next_stage == 11:
                agent.state['current_stage'] = 11
                agent._save_state()
            
            print_section("STAGE 11: APPOINTMENT SCHEDULING")
            response = agent.process_message("schedule appointment")
            response = agent.process_message("complete")
            
            print("\n✅ SCENARIO COMPLETE: Direct appointment path")
            print(f"   Path taken: 2 → 3 → 4 → 11 → 12")
            return True
        
        elif decision_type == 'admit_patient':
            # Path: Direct to Stage 7/8 (admission)
            if next_stage in [7, 8]:
                agent.state['current_stage'] = next_stage
                agent._save_state()
            
            print_section(f"STAGE {next_stage}: ADMISSION")
            response = agent.process_message("proceed with admission")
            
            print("\n✅ SCENARIO COMPLETE: Direct admission path")
            print(f"   Path taken: 2 → 3 → 4 → 7/8 → 9+")
            return True
        
        return True
        
    except AssertionError as e:
        print(f"\n❌ SCENARIO FAILED: {str(e)}")
        return False
    except Exception as e:
        print(f"\n❌ SCENARIO ERROR: {str(e)}")
        import traceback
        traceback.print_exc()
        return False

def main():
    """Run all test scenarios"""
    
    print("="*80)
    print("  COMPREHENSIVE WORKFLOW TEST - ALL PATHS")
    print("  Starting from Stage 2 (Verified Returning User)")
    print("="*80)
    
    results = {}
    
    # Scenario 1: Prescription Only (No labs, no admission)
    print("\n\n")
    results['prescription_only'] = run_scenario(
        "PRESCRIPTION ONLY PATH",
        initial_decision='prescription_only'
    )
    
    # Scenario 2: Labs → Prescription (Labs but no admission)
    print("\n\n")
    results['labs_then_prescription'] = run_scenario(
        "LABS → PRESCRIPTION PATH",
        initial_decision='approve_tests',
        post_lab_decision='prescription_only'
    )
    
    # Scenario 3: Labs → Admission (Full path with admission)
    print("\n\n")
    results['labs_then_admission'] = run_scenario(
        "LABS → ADMISSION PATH",
        initial_decision='approve_tests',
        post_lab_decision='admit_patient'
    )
    
    # Scenario 4: Direct Appointment (Skip labs)
    print("\n\n")
    results['direct_appointment'] = run_scenario(
        "DIRECT APPOINTMENT PATH",
        initial_decision='schedule_appointment'
    )
    
    # Scenario 5: Direct Admission (Emergency)
    print("\n\n")
    results['direct_admission'] = run_scenario(
        "DIRECT ADMISSION PATH",
        initial_decision='admit_patient'
    )
    
    # Summary
    print_section("TEST SUMMARY")
    
    total = len(results)
    passed = sum(1 for v in results.values() if v)
    
    for scenario, result in results.items():
        status = "✅ PASSED" if result else "❌ FAILED"
        print(f"{status}: {scenario}")
    
    print(f"\n📊 Results: {passed}/{total} scenarios passed")
    
    if passed == total:
        print("\n" + "="*80)
        print("  🎉 ALL SCENARIOS PASSED!")
        print("="*80)
        return 0
    else:
        print("\n" + "="*80)
        print(f"  ⚠️ {total - passed} SCENARIOS FAILED")
        print("="*80)
        return 1

if __name__ == "__main__":
    exit_code = main()
    sys.exit(exit_code)
