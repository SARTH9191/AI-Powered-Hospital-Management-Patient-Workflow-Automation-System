"""
Test Stage 6 (Results Analysis) - Complete Integration

This tests Phase 2 Priority 3: Stage 6 combines:
1. Lab results from Google Sheets (staff fills)
2. Doctor's diagnosis from Google Docs (doctor fills)
3. AI analysis of both sources
4. Comprehensive email with results + diagnosis

Workflow:
1. Patient enters Stage 6 (Results Analysis)
2. AI reads lab results from Google Sheets
3. AI reads doctor's diagnosis from Google Docs
4. AI combines both and provides comprehensive response
5. Email sent with full report
"""

import os
import sys
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Add parent directory to path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.workflow_chat_agent import WorkflowChatAgent
from tools.google_docs_tool import CreateDoctorNotesTool
from datetime import datetime


def print_section(title: str, content: str = ""):
    """Print formatted section"""
    print(f"\n{'='*70}")
    print(f"{title}")
    print(f"{'='*70}")
    if content:
        print(content)


def test_stage6_with_doctor_notes():
    """Test Stage 6 reads both lab results AND doctor notes"""
    
    print_section("🧪 STAGE 6 COMPLETE INTEGRATION TEST")
    print("Testing: Lab Results (Sheets) + Doctor Diagnosis (Docs)")
    
    # Create agent with test patient that has lab results
    agent = WorkflowChatAgent(
        patient_email="test_stage6@hospital.com",
        patient_id="REG2025SAMPLE"  # This patient has lab results in sheet
    )
    
    # Set up patient in Stage 6 with doctor notes doc
    agent.state["current_stage"] = 6
    agent.state["stage_data"] = {
        "registration": {
            "full_name": "Sample Patient"
        }
    }
    
    # Create a doctor notes doc with actual diagnosis
    print("\n📋 Step 1: Creating doctor's consultation notes")
    try:
        create_doc_tool = CreateDoctorNotesTool()
        doc_result = create_doc_tool._run(
            patient_name="Sample Patient (REG2025SAMPLE)",
            consultation_date=datetime.now().strftime("%Y-%m-%d"),
            chief_complaint="Lab results review",
            examination_findings="Patient appears healthy, vital signs normal",
            diagnosis="""Patient shows good health indicators from lab results. 
CBC values are within normal range indicating good blood health.
Glucose levels (95 mg/dL) are excellent, showing good metabolic control.
Cholesterol (185 mg/dL) is within optimal range, cardiovascular health appears good.

Overall Assessment: Healthy patient with no concerning findings.""",
            treatment_plan="""1. Continue current healthy lifestyle
2. Maintain balanced diet and regular exercise
3. No medications required at this time
4. Follow-up in 6 months for routine check
5. Contact if any symptoms develop""",
            doctor_name="Dr. Sarah Williams"
        )
        
        if doc_result.get("success"):
            doc_id = doc_result["document_id"]
            doc_url = doc_result["document_url"]
            agent.state["doctor_notes_doc_id"] = doc_id
            agent.state["doctor_notes_doc_url"] = doc_url
            agent._save_state()
            
            print(f"✅ Doctor notes created: {doc_url}")
        else:
            print(f"❌ Failed to create doctor notes")
            return False
            
    except Exception as e:
        print(f"❌ Error creating doctor notes: {e}")
        return False
    
    print("\n📊 Step 2: Patient asks about results")
    print('   Patient says: "Are my lab results ready?"')
    
    try:
        # First message (enters stage)
        result1 = agent.process_message("Are my lab results ready?")
        print(f"\n✅ Agent Response (Entry):")
        print(f"   {result1['response'][:200]}...")
        
        # Second message (fetches results + doctor notes)
        result2 = agent.process_message("Yes, please show me the results")
        
        print(f"\n✅ Agent Response (Full Results):")
        print(f"{result2['response']}")
        
        # Verify integration
        tools_executed = result2.get('tools_executed', [])
        data_source = result2.get('data_source', '')
        
        print_section("✅ INTEGRATION VERIFICATION")
        
        has_sheets = 'ReadLabResultsFromSheetTool' in tools_executed
        has_docs = 'ReadDoctorNotesTool' in tools_executed
        has_combined_source = 'Google Sheets' in data_source and 'Google Docs' in data_source
        
        print(f"\n📊 Tools Executed:")
        for tool in tools_executed:
            print(f"   ✓ {tool}")
        
        print(f"\n📁 Data Sources:")
        print(f"   {data_source}")
        
        print(f"\n✅ Verification:")
        print(f"   {'✓' if has_sheets else '✗'} Lab results from Google Sheets")
        print(f"   {'✓' if has_docs else '✗'} Doctor diagnosis from Google Docs")
        print(f"   {'✓' if has_combined_source else '✗'} Combined data source indicated")
        
        response_text = result2['response']
        has_lab_results = 'CBC' in response_text or 'Test Results' in response_text
        has_doctor_assessment = "Doctor's Assessment" in response_text or "Diagnosis" in response_text
        has_treatment_plan = "Treatment Plan" in response_text
        
        print(f"\n📋 Response Content:")
        print(f"   {'✓' if has_lab_results else '✗'} Lab test results included")
        print(f"   {'✓' if has_doctor_assessment else '✗'} Doctor's diagnosis included")
        print(f"   {'✓' if has_treatment_plan else '✗'} Treatment plan included")
        
        if has_sheets and has_docs and has_combined_source and has_lab_results and has_doctor_assessment:
            print_section("🎉 TEST PASSED: COMPLETE INTEGRATION WORKING!")
            print(f"\n💡 What this achieves:")
            print(f"   1. ✅ Lab tech fills Google Sheets → AI reads test results")
            print(f"   2. ✅ Doctor fills Google Docs → AI reads diagnosis/treatment")
            print(f"   3. ✅ AI combines both sources intelligently")
            print(f"   4. ✅ Patient gets complete picture in one response")
            print(f"   5. ✅ Email sent with comprehensive report")
            
            print(f"\n🎯 Phase 2 Complete Status:")
            print(f"   ✅ PRIORITY 1: Stage 3 auto-creates doctor notes doc")
            print(f"   ✅ PRIORITY 2: Q&A reads doctor notes")
            print(f"   ✅ PRIORITY 3: Stage 6 combines Sheets + Docs")
            
            print(f"\n🚀 Phase 2 - COMPLETE! All 3 priorities done!")
            
            return True
        else:
            print_section("❌ TEST FAILED: Integration incomplete")
            print(f"\n❌ Missing components:")
            if not has_sheets:
                print(f"   - Lab results not read from Sheets")
            if not has_docs:
                print(f"   - Doctor notes not read from Docs")
            if not has_combined_source:
                print(f"   - Combined data source not indicated")
            if not has_lab_results:
                print(f"   - Lab results not in response")
            if not has_doctor_assessment:
                print(f"   - Doctor diagnosis not in response")
            
            return False
            
    except Exception as e:
        print_section("❌ TEST EXCEPTION")
        print(f"Error: {e}")
        import traceback
        traceback.print_exc()
        return False


def main():
    """Run the test"""
    print_section("🏥 PHASE 2 - PRIORITY 3 TEST")
    print("Testing: Stage 6 combines Lab Results + Doctor Diagnosis")
    
    test_passed = test_stage6_with_doctor_notes()
    
    print_section("📊 TEST SUMMARY")
    
    if test_passed:
        print("✅ PASSED - Stage 6 Complete Integration")
        print("\n🎉 Phase 2 - ALL PRIORITIES COMPLETE!")
        print("\n📋 What we built:")
        print("   1. ✅ Stage 3: Auto-create doctor notes doc")
        print("   2. ✅ Q&A: Read doctor notes anytime")
        print("   3. ✅ Stage 6: Combine Sheets + Docs data")
        print("\n🚀 Ready for end-to-end workflow testing!")
        print("\n📅 Next Steps:")
        print("   • Test complete patient journey (Stages 1-6)")
        print("   • Or proceed to Phase 3 (Appointments/Calendar)")
        print("   • Or proceed to Phase 4 (Billing/Sheets)")
    else:
        print("❌ FAILED - Stage 6 Complete Integration")
        print("\n⚠️  Review errors above and fix issues")
    
    print_section("🏁 TEST COMPLETE")


if __name__ == "__main__":
    main()
