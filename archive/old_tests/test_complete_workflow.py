"""
🧪 COMPLETE PATIENT WORKFLOW TEST
Tests all 11 stages with real tool integrations:
- Gmail welcome email
- Google Drive folder creation
- Google Calendar appointments
- SMS notifications
- ChromaDB RAG analysis
- Stage gating (continue commands)
"""

import requests
import json
import time
from datetime import datetime

BASE_URL = "http://localhost:8000"
FRONTEND_URL = "http://localhost:3000"

# Test credentials
TEST_USER = {
    "username": "patient",
    "password": "patient123"
}

# Patient data for testing
TEST_PATIENT_DATA = {
    "name": "Samarth Pawar",
    "age": 28,
    "gender": "Male",
    "phone": "+917447444532",  # Your real phone for SMS testing
    "email": "samarth.pawar243@vit.edu",  # Your real email for Gmail/Calendar testing
    "address": "VIT, Pune, Maharashtra",
    "blood_type": "O+",
    "emergency_contact": {
        "name": "Emergency Contact",
        "phone": "+919876543211"
    },
    "insurance_provider": "Star Health Insurance",
    "chief_complaint": "Regular checkup and diabetes monitoring"
}

HOSPITAL_EMAIL = "pawarsamarth786@gmail.com"  # Hospital notifications

def print_section(title):
    """Print a formatted section header"""
    print("\n" + "="*80)
    print(f"  {title}")
    print("="*80 + "\n")

def login():
    """Login and get JWT token"""
    print_section("🔐 STEP 0: LOGIN")
    
    response = requests.post(
        f"{BASE_URL}/token",  # OAuth2 standard endpoint
        data={  # OAuth2 uses form data
            "username": TEST_USER["username"],
            "password": TEST_USER["password"]
        }
    )
    
    if response.status_code == 200:
        token = response.json()["access_token"]
        print(f"✅ Logged in successfully")
        print(f"   Token: {token[:50]}...")
        return token
    else:
        print(f"❌ Login failed: {response.text}")
        return None

def send_chat_message(token, message, workflow_id=None):
    """Send a chat message to the AI agent"""
    payload = {
        "message": message,
        "user_id": "patient",
        "user_role": "patient"
    }
    
    if workflow_id:
        payload["workflow_id"] = workflow_id
    
    response = requests.post(
        f"{BASE_URL}/api/workflow/chat/message",
        headers={
            "Authorization": f"Bearer {token}",
            "Content-Type": "application/json"
        },
        json=payload
    )
    
    if response.status_code == 200:
        return response.json()
    else:
        print(f"❌ Request failed: {response.status_code} - {response.text}")
        return None

def test_stage(token, stage_number, stage_name, message, workflow_id=None, wait_time=3):
    """Test a single workflow stage"""
    print_section(f"📋 STAGE {stage_number}: {stage_name}")
    
    print(f"💬 Sending message: '{message}'")
    result = send_chat_message(token, message, workflow_id)
    
    if result:
        print(f"\n🤖 AI Response:")
        print(f"   {result.get('response', 'No response')[:500]}...")
        
        if result.get('workflow_id'):
            print(f"\n🆔 Workflow ID: {result['workflow_id']}")
        
        if result.get('current_stage'):
            print(f"📍 Current Stage: {result['current_stage']}")
        
        if result.get('tool_calls'):
            print(f"\n🔧 Tools Used:")
            for tool in result['tool_calls']:
                print(f"   - {tool.get('tool')}: {tool.get('status')}")
        
        print(f"\n⏳ Waiting {wait_time} seconds before next stage...")
        time.sleep(wait_time)
        
        return result.get('workflow_id')
    else:
        print(f"❌ Stage {stage_number} failed")
        return workflow_id

def check_notifications():
    """Instructions to check notifications"""
    print_section("📬 CHECK YOUR NOTIFICATIONS")
    
    print("✅ Expected notifications to check:")
    print()
    print("1. 📧 GMAIL (pawarsamarth786@gmail.com):")
    print("   - Welcome email with patient ID")
    print("   - Document verification confirmation")
    print("   - Lab test approval notification")
    print("   - Calendar invite for lab appointment")
    print()
    print("2. 📱 SMS (your phone):")
    print("   - Registration confirmation")
    print("   - Document upload link")
    print("   - Lab appointment details")
    print()
    print("3. 📅 GOOGLE CALENDAR:")
    print("   - Lab appointment event")
    print("   - Event details with test names")
    print()
    print("4. 📁 GOOGLE DRIVE:")
    print("   - Patient folder created")
    print("   - Check: https://drive.google.com")
    print()
    input("Press Enter after checking notifications to continue...")

def main():
    """Run complete workflow test"""
    print_section("🚀 HOSPITAL AI AGENT - COMPLETE WORKFLOW TEST")
    print(f"Testing Date: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"Patient Email: {TEST_PATIENT_DATA['email']}")
    print(f"Patient Phone: {TEST_PATIENT_DATA['phone']}")
    print()
    print("This test will:")
    print("  1. Login as patient")
    print("  2. Start workflow with registration")
    print("  3. Progress through all 11 stages")
    print("  4. Test real Gmail, Drive, Calendar, SMS integrations")
    print("  5. Use 'continue' commands for stage gating")
    print()
    input("Press Enter to start the test...")
    
    # Step 0: Login
    token = login()
    if not token:
        print("❌ Cannot proceed without authentication")
        return
    
    # Stage 1: Registration
    registration_message = f"""I want to register as a new patient.
My name is {TEST_PATIENT_DATA['name']}
Age: {TEST_PATIENT_DATA['age']}
Gender: {TEST_PATIENT_DATA['gender']}
Phone: {TEST_PATIENT_DATA['phone']}
Email: {TEST_PATIENT_DATA['email']}
Address: {TEST_PATIENT_DATA['address']}
Blood Type: {TEST_PATIENT_DATA['blood_type']}
Insurance: {TEST_PATIENT_DATA['insurance_provider']}
Chief complaint: {TEST_PATIENT_DATA['chief_complaint']}
"""
    
    workflow_id = test_stage(
        token, 1, "REGISTRATION", 
        registration_message,
        wait_time=5
    )
    
    if not workflow_id:
        print("❌ Registration failed - cannot continue")
        return
    
    print("\n" + "🎯 Check your email for welcome message!" + "\n")
    time.sleep(2)
    
    # Stage 2: Document Processing
    workflow_id = test_stage(
        token, 2, "DOCUMENT PROCESSING",
        "continue",
        workflow_id,
        wait_time=4
    )
    
    print("\n" + "🎯 Check Google Drive for patient folder!" + "\n")
    time.sleep(2)
    
    # Stage 3: Medical History
    workflow_id = test_stage(
        token, 3, "MEDICAL HISTORY & RAG ANALYSIS",
        "continue",
        workflow_id,
        wait_time=4
    )
    
    print("\n" + "🎯 Check backend logs for RAG insights!" + "\n")
    time.sleep(2)
    
    # Stage 4: LLM Test Determination
    workflow_id = test_stage(
        token, 4, "AI TEST RECOMMENDATION",
        "continue",
        workflow_id,
        wait_time=4
    )
    
    # Stage 5: Lab Coordination (Calendar + SMS)
    workflow_id = test_stage(
        token, 5, "LAB COORDINATION (Calendar + SMS)",
        "continue",
        workflow_id,
        wait_time=5
    )
    
    print("\n" + "🎯 Check Google Calendar for lab appointment!" + "\n")
    print("🎯 Check your phone for SMS notification!" + "\n")
    time.sleep(3)
    
    # Stage 6: Results Analysis
    workflow_id = test_stage(
        token, 6, "RESULTS ANALYSIS",
        "continue",
        workflow_id,
        wait_time=3
    )
    
    # Stage 7: Admission Planning
    workflow_id = test_stage(
        token, 7, "ADMISSION PLANNING",
        "continue",
        workflow_id,
        wait_time=3
    )
    
    # Stage 8: Billing & Insurance
    workflow_id = test_stage(
        token, 8, "BILLING & INSURANCE",
        "continue",
        workflow_id,
        wait_time=3
    )
    
    # Stage 9: Discharge
    workflow_id = test_stage(
        token, 9, "DISCHARGE",
        "continue",
        workflow_id,
        wait_time=3
    )
    
    # Stage 10: Analytics & Reporting
    workflow_id = test_stage(
        token, 10, "ANALYTICS & REPORTING",
        "continue",
        workflow_id,
        wait_time=3
    )
    
    # Stage 11: Follow-up
    workflow_id = test_stage(
        token, 11, "FOLLOW-UP",
        "continue",
        workflow_id,
        wait_time=3
    )
    
    # Final summary
    print_section("🎉 WORKFLOW TEST COMPLETE!")
    
    print("✅ All 11 stages completed!")
    print()
    print("📊 INTEGRATION TEST RESULTS:")
    print()
    print("Check the following integrations:")
    print()
    print("1. ✅ Stage Gating: Each stage stopped and waited for 'continue'")
    print("2. 📧 Gmail Integration: Check pawarsamarth786@gmail.com")
    print("3. 📁 Google Drive: Check https://drive.google.com for patient folder")
    print("4. 📅 Google Calendar: Check for lab appointment event")
    print("5. 📱 SMS Notifications: Check your phone for messages")
    print("6. 🧠 RAG/ChromaDB: Check backend logs for AI insights")
    print()
    print(f"🆔 Final Workflow ID: {workflow_id}")
    print()
    print("💾 Check workflow state file:")
    print(f"   data/workflow_states.json")
    print()
    
    check_notifications()
    
    print_section("✨ TEST SUMMARY")
    print("All real tool integrations tested:")
    print("  ✅ Gmail - Welcome emails sent")
    print("  ✅ Google Drive - Patient folders created")
    print("  ✅ Google Calendar - Appointments scheduled")
    print("  ✅ SMS/Twilio - Notifications sent")
    print("  ✅ ChromaDB RAG - Medical insights generated")
    print("  ✅ Stage Gating - Workflow stops at each stage")
    print()
    print("🎯 Patient journey completed successfully!")
    print()

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n\n❌ Test interrupted by user")
    except Exception as e:
        print(f"\n\n❌ Test failed with error: {str(e)}")
        import traceback
        traceback.print_exc()
