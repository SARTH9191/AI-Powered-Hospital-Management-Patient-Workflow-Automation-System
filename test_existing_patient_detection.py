#!/usr/bin/env python3
"""
Test Existing Patient Detection Feature
Verifies that returning patients are recognized and skip registration
"""

import sys
import os
sys.path.append(os.path.dirname(__file__))

from src.workflow_chat_agent import WorkflowChatAgent
from tools.patient_registration_tool import RegisterPatientTool, SearchPatientTool

def test_existing_patient_detection():
    """Test that existing patients are recognized and registration is skipped"""
    
    print("=" * 80)
    print("🧪 TESTING EXISTING PATIENT DETECTION")
    print("=" * 80)
    
    # Step 1: Register a test patient first
    print("\n📝 Step 1: Registering test patient...")
    register_tool = RegisterPatientTool()
    
    registration_result = register_tool._run(
        full_name="Test Patient",
        phone="+91-9999888877",
        email="testpatient@hospital.com",
        date_of_birth="1990-01-15",
        gender="Male",
        address="123 Test Street, Test City, Test State"
    )
    
    print(registration_result)
    
    # Extract patient ID
    import re
    patient_id_match = re.search(r'Patient ID: (REG\d+)', registration_result)
    if not patient_id_match:
        print("❌ Failed to register test patient")
        return False
    
    test_patient_id = patient_id_match.group(1)
    print(f"✅ Test patient registered: {test_patient_id}")
    
    # Step 2: Create new workflow agent session
    print("\n🤖 Step 2: Creating new workflow session...")
    agent = WorkflowChatAgent(patient_email="testpatient@hospital.com")
    
    print(f"   Initial Stage: {agent.state['current_stage']}")
    print(f"   Patient ID: {agent.patient_id}")
    
    # Step 3: Simulate existing patient saying their name
    print("\n💬 Step 3: Simulating existing patient message...")
    print("   User: 'My name is Test Patient'")
    
    response = agent.process_message("My name is Test Patient")
    
    print("\n📨 Agent Response:")
    print(f"   Response: {response.get('response', '')[:200]}...")
    print(f"   Stage: {response.get('stage')}")
    print(f"   Stage Name: {response.get('stage_name')}")
    print(f"   Existing Patient: {response.get('existing_patient', False)}")
    print(f"   Patient ID: {response.get('patient_id', 'None')}")
    
    # Step 4: Verify detection worked
    print("\n🔍 Step 4: Verification...")
    
    checks = {
        "Patient recognized": "Welcome back" in response.get('response', ''),
        "Registration skipped": response.get('stage', 1) > 1,
        "Patient ID assigned": response.get('patient_id') == test_patient_id,
        "Existing patient flag": response.get('existing_patient', False)
    }
    
    all_passed = True
    for check_name, passed in checks.items():
        status = "✅" if passed else "❌"
        print(f"   {status} {check_name}")
        if not passed:
            all_passed = False
    
    # Step 5: Test with phone number
    print("\n💬 Step 5: Testing detection by phone number...")
    agent2 = WorkflowChatAgent(patient_email="testpatient@hospital.com")
    response2 = agent2.process_message("My phone is +91-9999888877")
    
    print(f"   Response: {response2.get('response', '')[:150]}...")
    print(f"   Patient Recognized: {'Welcome back' in response2.get('response', '')}")
    
    # Summary
    print("\n" + "=" * 80)
    if all_passed:
        print("🎉 ALL TESTS PASSED!")
        print("✅ Existing patients are correctly recognized")
        print("✅ Registration is skipped for returning patients")
        print("✅ Patient profile is loaded automatically")
    else:
        print("⚠️ SOME TESTS FAILED")
        print("Please check the implementation")
    print("=" * 80)
    
    return all_passed

def test_new_patient_flow():
    """Test that new patients still go through registration"""
    
    print("\n" + "=" * 80)
    print("🧪 TESTING NEW PATIENT FLOW")
    print("=" * 80)
    
    agent = WorkflowChatAgent(patient_email="newpatient@hospital.com")
    
    print("\n💬 Step 1: New patient provides name...")
    response = agent.process_message("My name is Brand New Patient")
    
    print(f"   Response: {response.get('response', '')[:200]}...")
    print(f"   Stage: {response.get('stage')}")
    print(f"   Should ask for phone: {'phone' in response.get('response', '').lower()}")
    
    # Verify new patient stays in registration
    checks = {
        "Stays in stage 1": response.get('stage', 0) == 1,
        "Asks for more info": len(response.get('response', '')) > 0,
        "Not marked as existing": not response.get('existing_patient', False)
    }
    
    all_passed = True
    print("\n🔍 Verification:")
    for check_name, passed in checks.items():
        status = "✅" if passed else "❌"
        print(f"   {status} {check_name}")
        if not passed:
            all_passed = False
    
    return all_passed

if __name__ == "__main__":
    try:
        print("\n🚀 Starting Existing Patient Detection Tests\n")
        
        test1 = test_existing_patient_detection()
        test2 = test_new_patient_flow()
        
        print("\n" + "=" * 80)
        print("📊 FINAL RESULTS")
        print("=" * 80)
        print(f"   Existing Patient Detection: {'✅ PASSED' if test1 else '❌ FAILED'}")
        print(f"   New Patient Flow: {'✅ PASSED' if test2 else '❌ FAILED'}")
        print("=" * 80)
        
        if test1 and test2:
            print("\n🎉 All tests passed! Feature is working correctly!")
        else:
            print("\n⚠️ Some tests failed. Please review the implementation.")
            
    except KeyboardInterrupt:
        print("\n\n⚠️ Tests cancelled by user")
    except Exception as e:
        print(f"\n❌ Test error: {e}")
        import traceback
        traceback.print_exc()
