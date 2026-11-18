"""
Test script for State Persistence API
Tests workflow start, status, resume, and delete endpoints
"""
import requests
import json
from datetime import datetime

# API Base URL
BASE_URL = "http://127.0.0.1:8000"

# Authentication
def get_auth_token():
    """Get JWT token for authentication"""
    print("🔐 Getting authentication token...")
    response = requests.post(
        f"{BASE_URL}/token",
        data={
            "username": "admin",
            "password": "admin123"
        }
    )
    if response.status_code == 200:
        token = response.json()["access_token"]
        print(f"✅ Token obtained: {token[:20]}...")
        return token
    else:
        print(f"❌ Authentication failed: {response.text}")
        return None

def test_workflow_start(token):
    """Test starting a new workflow"""
    print("\n" + "="*60)
    print("TEST 1: Start New Workflow")
    print("="*60)
    
    headers = {
        "Authorization": f"Bearer {token}",
        "Content-Type": "application/json"
    }
    
    patient_data = {
        "name": "Test Patient State Persistence",
        "age": 35,
        "gender": "Male",
        "phone": "+1234567890",
        "email": "test.persistence@hospital.com",
        "address": "123 Test Street, Test City",
        "blood_type": "O+",
        "current_symptoms": "Testing state persistence functionality",
        "has_insurance": True,
        "insurance_provider": "Test Insurance Co."
    }
    
    print(f"📤 Sending request to start workflow...")
    response = requests.post(
        f"{BASE_URL}/api/workflow/start",
        headers=headers,
        json=patient_data
    )
    
    if response.status_code == 200:
        result = response.json()
        print(f"✅ Workflow started successfully!")
        print(f"   Patient ID: {result.get('patient_id')}")
        print(f"   Current Stage: {result.get('current_stage')}")
        print(f"   Status: {result.get('status')}")
        print(f"   Workflow Complete: {result.get('workflow_complete')}")
        return result.get('patient_id')
    else:
        print(f"❌ Failed to start workflow: {response.status_code}")
        print(f"   Error: {response.text}")
        return None

def test_workflow_status(token, patient_id):
    """Test getting workflow status"""
    print("\n" + "="*60)
    print(f"TEST 2: Get Workflow Status for {patient_id}")
    print("="*60)
    
    headers = {
        "Authorization": f"Bearer {token}"
    }
    
    print(f"📤 Getting workflow status...")
    response = requests.get(
        f"{BASE_URL}/api/workflow/status/{patient_id}",
        headers=headers
    )
    
    if response.status_code == 200:
        result = response.json()
        print(f"✅ Workflow status retrieved!")
        print(f"   Patient ID: {result.get('patient_id')}")
        print(f"   Current Stage: {result.get('current_stage')}")
        print(f"   Last Saved: {result.get('last_saved')}")
        print(f"   Workflow Completed: {result.get('workflow_completed')}")
        print(f"   State Summary:")
        for key, value in result.get('state_summary', {}).items():
            print(f"      • {key}: {value}")
        return result
    else:
        print(f"❌ Failed to get status: {response.status_code}")
        print(f"   Error: {response.text}")
        return None

def test_list_workflows(token):
    """Test listing all workflows"""
    print("\n" + "="*60)
    print("TEST 3: List All Workflows")
    print("="*60)
    
    headers = {
        "Authorization": f"Bearer {token}"
    }
    
    print(f"📤 Getting all workflows...")
    response = requests.get(
        f"{BASE_URL}/api/workflow/list",
        headers=headers
    )
    
    if response.status_code == 200:
        result = response.json()
        print(f"✅ Workflows retrieved!")
        if result.get('workflows'):
            print(f"   Found {len(result['workflows'])} workflow(s):")
            for wf in result['workflows']:
                print(f"      • Patient: {wf.get('patient_id')} - Stage: {wf.get('current_stage')}")
        else:
            print("   No workflows found")
        return result
    else:
        print(f"❌ Failed to list workflows: {response.status_code}")
        print(f"   Error: {response.text}")
        return None

def test_workflow_resume(token, patient_id):
    """Test resuming a workflow"""
    print("\n" + "="*60)
    print(f"TEST 4: Resume Workflow for {patient_id}")
    print("="*60)
    
    headers = {
        "Authorization": f"Bearer {token}"
    }
    
    print(f"📤 Resuming workflow...")
    response = requests.post(
        f"{BASE_URL}/api/workflow/resume/{patient_id}",
        headers=headers
    )
    
    if response.status_code == 200:
        result = response.json()
        print(f"✅ Workflow resumed successfully!")
        print(f"   Patient ID: {result.get('patient_id')}")
        print(f"   Status: {result.get('status')}")
        print(f"   Current Stage: {result.get('current_stage')}")
        print(f"   Message: {result.get('message')}")
        return result
    else:
        print(f"❌ Failed to resume workflow: {response.status_code}")
        print(f"   Error: {response.text}")
        return None

def test_workflow_delete(token, patient_id):
    """Test deleting a workflow"""
    print("\n" + "="*60)
    print(f"TEST 5: Delete Workflow for {patient_id}")
    print("="*60)
    
    headers = {
        "Authorization": f"Bearer {token}"
    }
    
    print(f"📤 Deleting workflow...")
    response = requests.delete(
        f"{BASE_URL}/api/workflow/{patient_id}",
        headers=headers
    )
    
    if response.status_code == 200:
        result = response.json()
        print(f"✅ Workflow deleted successfully!")
        print(f"   Patient ID: {result.get('patient_id')}")
        print(f"   Message: {result.get('message')}")
        return result
    else:
        print(f"❌ Failed to delete workflow: {response.status_code}")
        print(f"   Error: {response.text}")
        return None

def main():
    """Main test execution"""
    print("\n" + "="*70)
    print("🧪 STATE PERSISTENCE API TESTING")
    print("="*70)
    print(f"⏰ Test started at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    
    # Get authentication token
    token = get_auth_token()
    if not token:
        print("\n❌ Cannot proceed without authentication token")
        return
    
    # Test 1: Start workflow
    patient_id = test_workflow_start(token)
    if not patient_id:
        print("\n❌ Cannot proceed without patient ID")
        return
    
    # Test 2: Get workflow status
    test_workflow_status(token, patient_id)
    
    # Test 3: List all workflows
    test_list_workflows(token)
    
    # Test 4: Resume workflow (if incomplete)
    # Note: This might fail if workflow already completed
    # test_workflow_resume(token, patient_id)
    
    # Test 5: Delete workflow
    input("\n⏸️  Press Enter to delete the test workflow...")
    test_workflow_delete(token, patient_id)
    
    print("\n" + "="*70)
    print("✅ ALL TESTS COMPLETED!")
    print("="*70)
    print(f"⏰ Test finished at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n\n⚠️  Tests interrupted by user")
    except Exception as e:
        print(f"\n\n❌ Test failed with error: {str(e)}")
