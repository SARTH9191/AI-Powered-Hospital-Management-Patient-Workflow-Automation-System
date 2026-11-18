#!/usr/bin/env python3
"""
Test Stage 2 routing fix for document upload phrases
"""

import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), 'src'))

from workflow_chat_agent import WorkflowChatAgent

def test_stage2_routing():
    """Test that Stage 2 document upload phrases are routed correctly"""
    
    print("🧪 Testing Stage 2 Routing Fix")
    print("=" * 50)
    
    # Create agent in Stage 2
    agent = WorkflowChatAgent(patient_email="test@example.com", patient_id="REG2025214740")
    
    # Set Stage 2 state
    agent.state = {
        "patient_id": "REG2025214740",
        "email": "test@example.com",
        "current_stage": 2,
        "conversation_history": [],
        "drive_folder_id": "1I4lAAtrpD6MasIdULCySjr-9S8zzmJqW",
        "drive_folder_url": "https://drive.google.com/drive/folders/1I4lAAtrpD6MasIdULCySjr-9S8zzmJqW"
    }
    
    # Test phrases that should go to Stage 2 handler
    test_phrases = [
        "Ok I have updated the drive can you check it?",
        "Can you check if documents are uploaded?", 
        "I have uploaded the documents",
        "Please check my documents",
        "Documents are ready for verification"
    ]
    
    for phrase in test_phrases:
        print(f"\n📝 Testing: '{phrase}'")
        
        # Test question detection
        is_question = agent._detect_question_intent(phrase)
        print(f"   Question detected: {is_question}")
        
        # Should be False for all Stage 2 document phrases
        if not is_question:
            print(f"   ✅ Correctly routed to Stage 2 handler")
        else:
            print(f"   ❌ Incorrectly routed to Q&A system")
    
    print(f"\n✅ Stage 2 routing test completed!")

if __name__ == "__main__":
    test_stage2_routing()