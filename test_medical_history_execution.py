#!/usr/bin/env python3
"""
Test Medical History Action Execution
"""

import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), 'src'))

from workflow_chat_agent import WorkflowChatAgent

def test_medical_history_execution():
    """Test the actual medical history action execution"""
    
    print("🧪 Testing Medical History Action Execution")
    print("=" * 50)
    
    # Create agent with real patient data
    agent = WorkflowChatAgent(patient_email="iamsamarth786@gmail.com", patient_id="REG2025214740")
    
    # Set up Stage 3 completion state with new structured data
    agent.state = {
        "patient_id": "REG2025214740",
        "email": "iamsamarth786@gmail.com",
        "current_stage": 3,
        "awaiting_confirmation": True,
        "pending_actions": [
            "add_to_tracking_system",
            "create_medical_document", 
            "share_with_medical_team",
            "save_medical_history"
        ],
        "stage_data": {
            "registration": {
                "full_name": "Samarth Pawar",
                "phone": "+91-7447444532",
                "date_of_birth": "2006-08-07",
                "gender": "Male"
            },
            "medical_history": {
                "past_conditions": {
                    "conditions": [],
                    "professional_summary": "No significant past medical history reported",
                    "risk_factors": [],
                    "follow_up_needed": False
                },
                "allergies": {
                    "allergies": [],
                    "professional_summary": "No known drug, food, or environmental allergies reported",
                    "clinical_notes": "Patient reports current symptoms: I have stomach pain and headache",
                    "symptoms_documented": ["Abdominal pain", "Headache"]
                },
                "current_medications": {
                    "medications": [],
                    "professional_summary": "Patient is not currently taking any medications",
                    "clinical_notes": "No current pharmacotherapy reported"
                },
                "chief_complaint": "Regular visit."
            }
        },
        "conversation_history": []
    }
    
    print("📋 Agent state configured with structured medical data")
    print(f"📋 Patient: {agent.state['stage_data']['registration']['full_name']}")
    print(f"📋 Pending actions: {len(agent.state['pending_actions'])}")
    
    # Execute the medical history actions
    print("\n🚀 Executing medical history actions...")
    try:
        results = agent._execute_medical_history_actions()
        
        print(f"\n✅ Execution completed!")
        print(f"📋 Results ({len(results)} items):")
        for i, result in enumerate(results, 1):
            print(f"   {i}. {result}")
            
    except Exception as e:
        print(f"❌ Execution failed: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    test_medical_history_execution()