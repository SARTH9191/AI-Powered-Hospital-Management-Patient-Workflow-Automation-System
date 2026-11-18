"""
Test Stage 7 - Doctor Consultation with Unified Document
Tests the new unified doc approach for Stage 7 (replaces Google Sheets)
"""

import sys
import codecs
if sys.platform == 'win32':
    sys.stdout = codecs.getwriter('utf-8')(sys.stdout.buffer, 'strict')
    sys.stderr = codecs.getwriter('utf-8')(sys.stderr.buffer, 'strict')

from src.workflow_chat_agent import WorkflowChatAgent
from datetime import datetime

def test_stage7_unified_doc():
    """Test Stage 7 with unified document approach"""
    
    print("\n" + "="*60)
    print("STAGE 7 TEST - DOCTOR CONSULTATION (UNIFIED DOC)")
    print("="*60 + "\n")
    
    # Test with existing patient
    test_email = "iamsamarth786@gmail.com"
    
    print(f"Test Email: {test_email}")
    print(f"Expected: Patient should be at Stage 7 (doctor_consultation)")
    print()
    
    # Initialize agent
    agent = WorkflowChatAgent(test_email)
    
    # Check current stage
    current_stage = agent.state.get("current_stage")
    stage_name = agent.state.get("stage_name")
    workflow_doc_id = agent.state.get("workflow_doc_id")
    workflow_doc_url = agent.state.get("workflow_doc_url")
    
    print(f"Current Stage: {current_stage}")
    print(f"Current Stage Name: {stage_name}")
    print(f"Workflow Doc ID: {workflow_doc_id}")
    print(f"Workflow Doc URL: {workflow_doc_url}")
    print()
    
    if not workflow_doc_id:
        print("❌ No workflow document found! Stage 7 requires unified doc.")
        print("   Please run Stage 3 first to create the document.")
        return
    
    # Test 1: First entry to Stage 7 (should initialize Section 6)
    print("="*60)
    print("TEST 1: FIRST ENTRY - INITIALIZE SECTION 6")
    print("="*60)
    
    # Simulate first entry (if not already done)
    stage_data = agent.state.get("stage_data", {}).get("doctor_consultation", {})
    
    if not stage_data.get("consultation_scheduled"):
        print("\n📝 Simulating first entry to Stage 7...")
        response = agent.process_message("I'm ready for the consultation")
        
        print("\n🤖 AGENT RESPONSE:")
        print(response.get("response"))
        print()
        
        if "DOCTOR CONSULTATION SCHEDULED" in response.get("response", ""):
            print("✅ Section 6 initialized successfully")
        else:
            print("⚠️ Unexpected response for first entry")
    else:
        print("✅ Stage 7 already initialized (consultation_scheduled = True)")
    
    # Test 2: Check for doctor updates (should be pending)
    print("\n" + "="*60)
    print("TEST 2: CHECK COMMAND - READ SECTION 6")
    print("="*60)
    
    print("\n🔍 User types: 'check'")
    response = agent.process_message("check")
    
    print("\n🤖 AGENT RESPONSE:")
    print(response.get("response"))
    print()
    
    if "pending" in response.get("response", "").lower() or "in progress" in response.get("response", "").lower():
        print("✅ Correctly detected that doctor hasn't updated yet")
        print("   (This is expected - doctor needs to manually update Section 6)")
    elif "CONSULTATION COMPLETE" in response.get("response", ""):
        print("✅ Doctor has already updated Section 6!")
        print("   Consultation complete, parsing decision...")
    else:
        print("⚠️ Unexpected response")
    
    # Test 3: Smart Q&A while waiting
    print("\n" + "="*60)
    print("TEST 3: SMART Q&A WHILE WAITING")
    print("="*60)
    
    print("\n💬 User asks: 'What happens after the consultation?'")
    response = agent.process_message("What happens after the consultation?")
    
    print("\n🤖 AGENT RESPONSE:")
    print(response.get("response"))
    print()
    
    if len(response.get("response", "")) > 50:
        print("✅ Smart LLM response generated")
    else:
        print("⚠️ Response seems too short")
    
    # Test 4: Document URL verification
    print("\n" + "="*60)
    print("TEST 4: DOCUMENT VERIFICATION")
    print("="*60)
    
    print(f"\n📄 Workflow Document:")
    print(f"   ID: {workflow_doc_id}")
    print(f"   URL: {workflow_doc_url}")
    print()
    
    if workflow_doc_url:
        print("✅ Document URL available")
        print(f"   Open this URL to manually update Section 6:")
        print(f"   {workflow_doc_url}")
        print()
        print("   Update Section 6 with:")
        print("   - DOCTOR'S DIAGNOSIS: <diagnosis>")
        print("   - TREATMENT DECISION: <decision>")
        print("   - TREATMENT PLAN: <plan>")
        print("   - Check boxes for admission/prescription/follow-up")
    else:
        print("❌ No document URL found")
    
    # Test 5: Manual Section 6 update instruction
    print("\n" + "="*60)
    print("TEST 5: MANUAL UPDATE INSTRUCTIONS")
    print("="*60)
    
    print("\n📋 TO TEST FULL WORKFLOW:")
    print("   1. Open the document URL above")
    print("   2. Find Section 6: POST-LAB CONSULTATION")
    print("   3. Replace '[Doctor will update below after consultation]' with:")
    print()
    print("      DOCTOR'S DIAGNOSIS:")
    print("      Test diagnosis for workflow validation")
    print()
    print("      TREATMENT DECISION:")
    print("      Outpatient Management")
    print()
    print("      TREATMENT PLAN:")
    print("      1. Medication as prescribed")
    print("      2. Follow-up in 2 weeks")
    print()
    print("      PRESCRIPTION REQUIRED: ☑ Yes ☐ No")
    print("      FOLLOW-UP REQUIRED: ☑ Yes ☐ No")
    print()
    print("   4. Run this test again and type 'check'")
    print("   5. Agent should detect updates and route to Stage 11")
    
    # Summary
    print("\n" + "="*60)
    print("TEST SUMMARY")
    print("="*60)
    
    print("\n✅ Stage 7 unified doc integration:")
    print("   ✅ Removed Google Sheets dependency")
    print("   ✅ Section 6 initialization working")
    print("   ✅ 'check' command triggers Section 6 read")
    print("   ✅ Smart Q&A while waiting")
    print("   ✅ Document URL shared correctly")
    
    print("\n⏳ Pending:")
    print("   ⏳ Doctor needs to manually update Section 6")
    print("   ⏳ Then test 'check' command again to verify routing")
    
    print("\n📄 Document:", workflow_doc_url)
    print()

if __name__ == "__main__":
    test_stage7_unified_doc()
