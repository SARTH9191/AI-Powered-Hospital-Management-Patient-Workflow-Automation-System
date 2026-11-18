"""
Reset patient state to start fresh workflow test
"""

import os
import sys

# Add src to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

from workflow_chat_agent import WorkflowChatAgent

def main():
    patient_email = "iamsamarth786@gmail.com"
    patient_id = "PAT20251113001842"
    
    print(f"\n🔄 Resetting state for patient: {patient_email}")
    print(f"📋 Patient ID: {patient_id}\n")
    
    agent = WorkflowChatAgent(
        patient_email=patient_email,
        patient_id=patient_id
    )
    
    # Reset to Stage 2 (start)
    agent.state = {
        'current_stage': 'start',
        'stage': 2,
        'stage_data': {},
        'conversation_history': []
    }
    agent._save_state()
    
    print("✅ State reset to Stage 2 (start)")
    print(f"✅ Current stage: {agent.state.get('current_stage')}")
    print(f"✅ Stage number: {agent.state.get('stage')}\n")
    
    print("🚀 Ready to run test_complete_end_to_end_workflow.py!\n")

if __name__ == "__main__":
    main()
