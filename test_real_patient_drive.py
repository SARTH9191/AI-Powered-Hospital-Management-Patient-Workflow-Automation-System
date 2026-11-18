#!/usr/bin/env python3
"""
Test real patient scenario with actual Drive folder retrieval
"""

import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), 'src'))

from workflow_chat_agent import WorkflowChatAgent

def test_real_patient_scenario():
    """Test with a real patient ID that should have Drive folder info"""
    
    print("🧪 Testing Real Patient Drive Folder Retrieval")
    print("=" * 50)
    
    # Use the actual patient ID from your registration
    agent = WorkflowChatAgent(patient_email="iamsamarth786@gmail.com", patient_id="REG2025214740")
    
    # Set up Stage 2 state (simulate missing state info)
    agent.state = {
        "patient_id": "REG2025214740",
        "email": "iamsamarth786@gmail.com", 
        "current_stage": 2,
        "stage_data": {
            "registration": {
                "full_name": "Samarth Pawar",
                "phone": "+91-7447444532"
            }
        },
        # Don't set drive_folder_id - force database lookup
        "conversation_history": []
    }
    
    print("\n📋 Testing: Document upload with database fallback")
    result = agent._handle_document_upload("done")
    
    print(f"\n🔍 Result Response (first 200 chars):")
    print(result['response'][:200] + "...")
    print(f"\nStage Complete: {result['stage_complete']}")
    print(f"Stage: {result['stage']}")
    
    # Check if Drive folder info was retrieved
    print(f"\n📁 Drive Folder Info Retrieved:")
    print(f"  - Folder ID: {agent.state.get('drive_folder_id', 'Not found')}")
    print(f"  - Folder URL: {agent.state.get('drive_folder_url', 'Not found')[:50]}...")
    
    if agent.state.get('drive_folder_id'):
        print("✅ SUCCESS: Drive folder info retrieved from database!")
    else:
        print("❌ ISSUE: Drive folder info not found")

if __name__ == "__main__":
    test_real_patient_scenario()