#!/usr/bin/env python3
"""
Complete Workflow Test with Real Google Workspace Integration
Tests the full Stage 1-3 workflow with actual tool execution
"""

import sys
import os
import asyncio
sys.path.append('.')
sys.path.append('src')

async def test_complete_workflow():
    """Test the complete workflow with real Google Workspace integration"""
    
    print("🧪 COMPLETE WORKFLOW TEST")
    print("=" * 60)
    
    try:
        from src.workflow_chat_agent import WorkflowChatAgent
        
        # Initialize the agent with test patient email
        print("🚀 Initializing Workflow Agent...")
        agent = WorkflowChatAgent(patient_email="test@hospital.com")
        
        # Test 1: Stage 1 - Registration
        print("\n" + "="*60)
        print("🏥 STAGE 1: Patient Registration")
        print("="*60)
        
        registration_input = "Hi, I want to register as a new patient. My name is John Smith, age 35, phone 555-0123, address 123 Main St, Springfield"
        
        response = await agent.process_message(registration_input)
        print(f"✅ Registration Response: {response}")
        
        # Test 2: Stage 2 - Document Upload Check
        print("\n" + "="*60)
        print("📄 STAGE 2: Document Upload Verification")
        print("="*60)
        
        document_input = "I have uploaded my medical documents to the folder"
        
        response = await agent.process_message(document_input)
        print(f"✅ Document Check Response: {response}")
        
        # Test 3: Stage 3 - Medical History Collection
        print("\n" + "="*60)
        print("🏥 STAGE 3: Medical History Collection")
        print("="*60)
        
        medical_input = """I have diabetes, high blood pressure, and I'm allergic to penicillin and shellfish. 
        I take metformin 500mg twice daily and lisinopril 10mg once daily. 
        I had appendectomy in 2015 and broke my arm in 2020."""
        
        response = await agent.process_message(medical_input)
        print(f"✅ Medical History Response: {response}")
        
        # Test 4: General Q&A
        print("\n" + "="*60)
        print("❓ GENERAL Q&A TEST")
        print("="*60)
        
        qa_input = "What are your visiting hours?"
        
        response = await agent.process_message(qa_input)
        print(f"✅ Q&A Response: {response}")
        
        print("\n" + "="*60)
        print("🎉 WORKFLOW TEST COMPLETE!")
        print("="*60)
        
        # Test Google Docs specifically
        print("\n📄 Testing Google Docs Integration...")
        
        from tools.google_docs_tool import GoogleDocsTool
        docs_tool = GoogleDocsTool()
        
        # Create a test medical history document
        test_doc = await docs_tool.create_medical_history_document(
            patient_name="John Smith",
            patient_id="TEST_001",
            conditions=["Type 2 Diabetes Mellitus", "Essential Hypertension"],
            allergies=["Penicillin", "Shellfish"],
            medications=["Metformin 500mg BID", "Lisinopril 10mg QD"],
            procedures=["Appendectomy (2015)", "Forearm Fracture Repair (2020)"]
        )
        
        if test_doc:
            print(f"✅ Google Docs test successful! Document ID: {test_doc['documentId']}")
        else:
            print("❌ Google Docs test failed")
            
    except Exception as e:
        print(f"❌ Test failed: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    asyncio.run(test_complete_workflow())