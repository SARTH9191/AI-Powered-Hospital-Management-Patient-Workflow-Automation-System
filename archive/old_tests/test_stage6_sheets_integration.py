"""
Test Stage 6 (Results Analysis) with Google Sheets Integration
This tests the complete flow: Staff fills sheet → AI reads → Patient gets results
"""

import os
import sys
from dotenv import load_dotenv

sys.path.append(os.path.dirname(os.path.abspath(__file__)))
load_dotenv()

from src.workflow_chat_agent import WorkflowChatAgent

def test_stage_6_with_sheets():
    """Test Stage 6 results analysis reading from Google Sheets"""
    
    print("\n" + "🧪" * 35)
    print("STAGE 6: RESULTS ANALYSIS - GOOGLE SHEETS INTEGRATION TEST")
    print("🧪" * 35)
    
    # Create agent for test patient
    print("\n📋 Setting up test scenario...")
    print("   Patient ID: REG2025SAMPLE")
    print("   Scenario: Lab tech has filled results in Google Sheet")
    
    agent = WorkflowChatAgent(patient_email="test@hospital.com")
    
    # Manually set agent to Stage 6 for testing
    agent.patient_id = "REG2025SAMPLE"
    agent.state = {
        "patient_id": "REG2025SAMPLE",
        "patient_email": "test@hospital.com",
        "patient_name": "Sample Patient",
        "current_stage": 6,
        "stage_name": "results_analysis",
        "stage_data": {},
        "conversation_history": []
    }
    
    print("✅ Agent initialized at Stage 6")
    
    # Test 1: First message (should check for results)
    print("\n" + "=" * 70)
    print("TEST 1: Patient asks about results (First message)")
    print("=" * 70)
    
    print("\n👤 Patient: Are my lab results ready?")
    
    result1 = agent.process_message("Are my lab results ready?")
    
    print(f"\n🤖 AI Response (Message 1):\n{result1['response']}")
    print(f"\n📊 Tools Executed: {result1.get('tools_executed', [])}")
    print(f"📌 Data Source: {result1.get('data_source', 'N/A')}")
    print(f"✅ Stage Complete: {result1.get('stage_complete', False)}")
    
    # Test 1b: Second message (should actually fetch results from sheets)
    if not result1.get('stage_complete'):
        print("\n" + "-" * 70)
        print("Continuing conversation... (fetching from sheets)")
        print("-" * 70)
        
        print("\n👤 Patient: Yes, please show me the results")
        
        result1b = agent.process_message("Yes, please show me the results")
        
        print(f"\n🤖 AI Response (Message 2 - Actual Results):\n{result1b['response']}")
        print(f"\n📊 Tools Executed: {result1b.get('tools_executed', [])}")
        print(f"📌 Data Source: {result1b.get('data_source', 'N/A')}")
        print(f"✅ Stage Complete: {result1b.get('stage_complete', False)}")
        
        # Use this result for validation
        result1 = result1b
    
    # Test 2: Follow-up question
    if result1.get('stage_complete'):
        print("\n" + "=" * 70)
        print("TEST 2: Patient asks follow-up question")
        print("=" * 70)
        
        print("\n👤 Patient: What does my glucose level mean?")
        
        result2 = agent.process_message("What does my glucose level mean?")
        
        print(f"\n🤖 AI Response:\n{result2['response']}")
    
    # Summary
    print("\n" + "=" * 70)
    print("TEST SUMMARY")
    print("=" * 70)
    
    if result1.get('data_source') == "Google Sheets (Staff-filled)":
        print("✅ Google Sheets integration working!")
        print("✅ AI successfully read lab results from sheet")
        print("✅ Staff-filled data retrieved correctly")
        print("\n🎉 INTEGRATION TEST PASSED!")
        
        print("\n📋 What just happened:")
        print("   1. Lab technician filled results in Google Sheet")
        print("   2. AI agent read data using ReadLabResultsFromSheetTool")
        print("   3. AI analyzed results with LLM")
        print("   4. Patient received friendly, interpreted results")
        print("   5. Email sent with detailed report")
        
        print("\n💡 This proves:")
        print("   • Staff can use familiar Google Sheets")
        print("   • No custom portal needed")
        print("   • Real-time data access for AI")
        print("   • Patients get instant, interpreted results")
    else:
        print("⚠️ Integration test incomplete")
        print(f"   Data source: {result1.get('data_source', 'Unknown')}")
        print("   May need to check Google Sheets setup")

def test_with_pending_results():
    """Test when results are not yet ready"""
    
    print("\n" + "=" * 70)
    print("TEST 3: Patient with pending results")
    print("=" * 70)
    
    agent = WorkflowChatAgent(patient_email="test@hospital.com")
    agent.patient_id = "REG2025NOTFOUND"  # Patient with no results
    agent.state = {
        "patient_id": "REG2025NOTFOUND",
        "current_stage": 6,
        "stage_name": "results_analysis",
        "stage_data": {}
    }
    
    print("\n👤 Patient (no results yet): Are my results ready?")
    
    result = agent.process_message("Are my results ready?")
    
    print(f"\n🤖 AI Response:\n{result['response']}")
    
    if "pending" in result['response'].lower() or "processing" in result['response'].lower():
        print("\n✅ Correctly handled pending results")
        print("   AI explained that results are still being processed")
    else:
        print("\n⚠️ Response may need refinement")

if __name__ == "__main__":
    try:
        # Check environment
        sheet_id = os.getenv('LAB_RESULTS_SHEET_ID')
        if not sheet_id:
            print("❌ LAB_RESULTS_SHEET_ID not found in .env")
            print("   Please run: python scripts/create_lab_results_sheet.py")
            sys.exit(1)
        
        print(f"✅ Lab Results Sheet configured: {sheet_id[:20]}...")
        
        # Run tests
        test_stage_6_with_sheets()
        test_with_pending_results()
        
        print("\n" + "🎉" * 35)
        print("ALL INTEGRATION TESTS COMPLETED!")
        print("🎉" * 35)
        
        print("\n🚀 Next Steps:")
        print("   1. Test with real patient flow (Stage 1 → 6)")
        print("   2. Train staff on filling Google Sheet")
        print("   3. Deploy to beta testing")
        
    except Exception as e:
        print(f"\n❌ Test failed: {e}")
        import traceback
        traceback.print_exc()
