"""
Debug 500 Error in Workflow
Checks what happens after Gmail initialization in Stage 2
"""

import sys
import traceback
from src.workflow_chat_agent import WorkflowChatAgent

print("=" * 80)
print("DEBUGGING 500 ERROR")
print("=" * 80)
print()

# Create agent
agent = WorkflowChatAgent(
    patient_email="iamsamarth786@gmail.com"
)

# Simulate Stage 1 completion (registration)
agent.patient_id = "REG2025533820"
agent.patient_name = "Samarth Pawar"
agent.state["current_stage"] = 2  # Move to stage 2
agent.state["stage_data"]["registration"] = {
    "first_name": "Samarth",
    "last_name": "Pawar",
    "full_name": "Samarth Pawar",
    "patient_id": "REG2025533820",
    "email": "iamsamarth786@gmail.com"
}

print("✅ Agent initialized")
print(f"   Patient ID: {agent.patient_id}")
print(f"   Current Stage: {agent.state['current_stage']}")
print()

# Try to process a message that would trigger Stage 2
test_messages = [
    "yes",  # Confirmation
    "continue",
    "ok proceed"
]

for msg in test_messages:
    print(f"Testing message: '{msg}'")
    print("-" * 80)
    
    try:
        result = agent.process_message(msg)
        print(f"✅ SUCCESS")
        print(f"   Response length: {len(result.get('response', ''))}")
        print(f"   Stage: {result.get('stage')}")
        print(f"   Stage complete: {result.get('stage_complete')}")
        print(f"   Tools executed: {result.get('tools_executed', [])}")
        print()
        
        # If successful, break
        break
        
    except Exception as e:
        print(f"❌ ERROR: {type(e).__name__}: {str(e)}")
        print()
        print("Full traceback:")
        traceback.print_exc()
        print()
        print("=" * 80)
        print()
        
        # Check what's in the response before error
        print("🔍 Checking agent state:")
        print(f"   Current stage: {agent.state.get('current_stage')}")
        print(f"   Stage data keys: {list(agent.state.get('stage_data', {}).keys())}")
        print()

print("=" * 80)
print("DEBUG COMPLETE")
print("=" * 80)
