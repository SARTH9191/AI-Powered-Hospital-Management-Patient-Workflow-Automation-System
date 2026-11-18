
import sys
sys.path.append('src')

from workflow_chat_agent import WorkflowChatAgent
import time

print("="*80)
print("  END-TO-END WORKFLOW TEST")
print("="*80 + "\n")

# Initialize agent for returning user
print("Step 1: Initialize agent for returning user...")
agent = WorkflowChatAgent(patient_email="iamsamarth786@gmail.com")
print(f"✅ Patient ID: {agent.patient_id}")
print(f"✅ Current Stage: {agent.state.get('current_stage')}\n")

# Stage 2: Skip documents
print("Step 2: Skip document upload (returning user)...")
response = agent.process_message("skip documents")
print(f"✅ Response stage: {response.get('stage')}")
print(f"✅ Stage complete: {response.get('stage_complete')}\n")

# Stage 3: Medical history
print("Step 3: Provide medical history...")
medical_history = '''I am experiencing chest pain and shortness of breath.
I have hypertension for 5 years.
I am allergic to penicillin.
I am taking Amlodipine 5mg daily.'''

response = agent.process_message(medical_history)
print(f"Current stage: {response.get('stage')}")

# Continue until confirmation requested
max_retries = 5
for i in range(max_retries):
    if 'proceed' in response.get('response', '').lower() or 'yes/no' in response.get('response', '').lower():
        print("\n📋 Confirmation requested - responding 'yes'...")
        response = agent.process_message("yes")
        break
    else:
        response = agent.process_message("continue")
    time.sleep(1)

# Check if unified sheet was created
sheet_url = agent.state.get('unified_patient_sheet_url') or agent.state.get('doctor_review_sheet_url')
if sheet_url:
    print(f"\n✅ PRIORITY 1 SUCCESS: Unified sheet created!")
    print(f"   Sheet URL: {sheet_url}")
    print(f"   Current stage: {agent.state.get('current_stage')}")
    
    if agent.state.get('current_stage') == 4:
        print(f"\n✅ Successfully advanced to Stage 4!\n")
        
        # Stage 4: Test doctor decision reading
        print("Step 4: Test doctor decision reading...")
        response = agent.process_message("What should I do now?")
        
        if 'check doctor decision' in response.get('response', '').lower():
            print("\n✅ PRIORITY 2 SUCCESS: Stage 4 prompts for 'check doctor decision'!")
            print(f"   Response includes instruction to check doctor decision\n")
            
            # Show manual steps
            print("="*80)
            print("  MANUAL TESTING STEPS")
            print("="*80)
            print(f"\n1. Open the unified sheet:")
            print(f"   {sheet_url}")
            print(f"\n2. Fill in 'STAGE 4: DOCTOR'S INITIAL ASSESSMENT' section:")
            print(f"   - Initial Assessment: Patient shows cardiovascular risk")
            print(f"   - Preliminary Diagnosis: Suspected angina")
            print(f"   - Your Decision: approve_tests")
            print(f"   - Recommended Tests:")
            print(f"     • ECG")
            print(f"     • Echocardiogram")
            print(f"     • Lipid Profile")
            print(f"\n3. Run this command to test Stage 4 decision reading:")
            print(f"   .venv\\Scripts\\python.exe -c \"")
            print(f"import sys; sys.path.append('src')")
            print(f"from workflow_chat_agent import WorkflowChatAgent")
            print(f"agent = WorkflowChatAgent(patient_email='iamsamarth786@gmail.com')")
            print(f"response = agent.process_message('check doctor decision')")
            print(f"print(response.get('response')[:500])")
            print(f"\"")
            print(f"\n✅ PRIORITY 3: ReadDoctorDecisionTool will read from 'Stage 4' section")
            print("="*80)
            
        else:
            print(f"\n⚠️ Unexpected response: {response.get('response', '')[:200]}...")
    else:
        print(f"\n⚠️ Stage {agent.state.get('current_stage')} - expected Stage 4")
else:
    print(f"\n❌ No unified sheet URL found in state")
    print(f"   Keys in state: {list(agent.state.keys())}")

print("\n" + "="*80)
print("  TEST COMPLETE")
print("="*80)
