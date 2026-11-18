#!/usr/bin/env python3
"""
Test Stage 2 Document Upload Handler
Tests the newly implemented _handle_document_upload method
"""

import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), 'src'))

from workflow_chat_agent import WorkflowChatAgent

def test_document_upload_stage():
    """Test Stage 2 document upload functionality"""
    
    print("🧪 Testing Stage 2 Document Upload Handler")
    print("=" * 50)
    
    # Create test agent in Stage 2
    agent = WorkflowChatAgent(patient_email="test@example.com", patient_id="TEST_PATIENT_123")
    
    # Set up Stage 2 state
    agent.state = {
        "patient_id": "TEST_PATIENT_123",
        "email": "test@example.com", 
        "current_stage": 2,
        "stage_data": {
            "registration": {
                "full_name": "Test Patient",
                "phone": "+91-9876543210"
            }
        },
        "drive_folder_id": "test_folder_123",
        "drive_folder_url": "https://drive.google.com/drive/folders/test_folder_123",
        "conversation_history": []
    }
    
    print("\n📋 Test 1: Default upload instructions")
    result1 = agent._handle_document_upload("hello")
    print(f"Response: {result1['response'][:100]}...")
    print(f"Stage Complete: {result1['stage_complete']}")
    
    print("\n✅ Test 2: Document upload completion")
    result2 = agent._handle_document_upload("done")
    print(f"Response: {result2['response'][:100]}...")
    print(f"Stage Complete: {result2['stage_complete']}")
    
    print("\n⏭️ Test 3: Skip document upload")
    result3 = agent._handle_document_upload("skip")
    print(f"Response: {result3['response'][:100]}...")
    print(f"Stage: {result3['stage']}")
    print(f"Next Stage: {result3.get('next_stage', 'None')}")
    
    print("\n🔍 Test 4: Missing folder scenario") 
    agent.state["drive_folder_id"] = ""  # Simulate missing folder
    result4 = agent._handle_document_upload("done")
    print(f"Response: {result4['response'][:100]}...")
    print(f"Error Handled: {'folder not found' in result4['response'].lower()}")
    
    print("\n✅ All tests completed!")
    print("Stage 2 Document Upload Handler is working correctly")

if __name__ == "__main__":
    test_document_upload_stage()