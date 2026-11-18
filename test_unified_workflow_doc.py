"""
Test Unified Workflow Document Tool
Tests creating, reading, and updating a single Google Doc for entire workflow
"""

import sys
import codecs
if sys.platform == 'win32':
    sys.stdout = codecs.getwriter('utf-8')(sys.stdout.buffer, 'strict')
    sys.stderr = codecs.getwriter('utf-8')(sys.stderr.buffer, 'strict')

from tools.unified_workflow_doc_tool import (
    UnifiedPatientDocumentTool,
    create_workflow_doc,
    read_doctor_decision,
    update_doc_section
)
import time


def print_section(title):
    print(f"\n{'='*80}")
    print(f"  {title}")
    print(f"{'='*80}\n")


def test_create_workflow_doc():
    """Test creating the unified workflow document"""
    
    print_section("TEST 1: Create Workflow Document")
    
    # Test data
    patient_id = "TEST_PAT_001"
    patient_name = "Samarth Pawar"
    patient_email = "iamsamarth786@gmail.com"
    
    medical_history = """
I am experiencing chest pain and shortness of breath for the past 2 weeks.
I have a history of hypertension (high blood pressure) for 5 years.
My blood pressure is usually around 145/95 mmHg.
I have high cholesterol - last checked was 240 mg/dL.
I have a family history of heart disease - my father had a heart attack at age 55.
I am currently taking Amlodipine 5mg for blood pressure.
I have no known drug allergies.
I occasionally experience dizziness and fatigue.
I don't smoke but I used to smoke for 10 years (quit 3 years ago).
I drink alcohol occasionally (1-2 times per week).
"""
    
    ai_analysis = """
Based on the patient's medical history, there are several concerning factors:

1. CARDIOVASCULAR RISK FACTORS:
   - Uncontrolled hypertension (145/95 mmHg despite medication)
   - Hypercholesterolemia (240 mg/dL)
   - Strong family history of premature CAD
   - Former smoker (10 pack-years)
   - New onset chest pain and dyspnea

2. CURRENT SYMPTOMS:
   - Chest pain (2 weeks duration)
   - Shortness of breath
   - Dizziness and fatigue
   
3. RISK ASSESSMENT:
   - HIGH RISK for acute coronary syndrome
   - Requires urgent cardiac evaluation
   
4. RECOMMENDATIONS:
   - Immediate cardiac workup needed
   - Consider adjustment of antihypertensive medication
   - Lipid management required
"""
    
    recommended_tests = [
        "ECG (Electrocardiogram)",
        "Echocardiogram",
        "Lipid Profile (Complete)",
        "Complete Blood Count (CBC)",
        "Thyroid Function Tests (TSH, T3, T4)",
        "Chest X-Ray",
        "Stress Test (if ECG normal)"
    ]
    
    print("Creating workflow document...")
    print(f"Patient: {patient_name}")
    print(f"Email: {patient_email}")
    print()
    
    result = create_workflow_doc(
        patient_id=patient_id,
        patient_name=patient_name,
        patient_email=patient_email,
        medical_history=medical_history,
        ai_analysis=ai_analysis,
        recommended_tests=recommended_tests
    )
    
    if result.get('success'):
        print("✅ Document created successfully!")
        print(f"   Doc ID: {result['doc_id']}")
        print(f"   Doc URL: {result['doc_url']}")
        print(f"   Shared with: {result['shared_with']}")
        print()
        print("📋 Document Contents:")
        print("   • Section 1: Medical History")
        print("   • Section 2: AI Analysis")
        print("   • Section 3: Doctor's Decision (Pending)")
        print("   • Section 4: Lab Test Scheduling")
        print("   • Section 5: Lab Results")
        print("   • Section 6: Post-Lab Consultation")
        print("   • Section 7: Prescription & Follow-up")
        print("   • Section 8: Workflow Completion")
        print()
        return result['doc_id'], result['doc_url']
    else:
        print(f"❌ Failed to create document: {result.get('error')}")
        return None, None


def test_read_doctor_decision(doc_id: str, doc_url: str):
    """Test reading doctor's decision"""
    
    print_section("TEST 2: Read Doctor's Decision")
    
    print(f"Document URL: {doc_url}")
    print()
    print("⚠️ MANUAL STEP REQUIRED:")
    print("   1. Open the document URL above")
    print("   2. Go to Section 3: DOCTOR'S DECISION")
    print("   3. Update the following fields:")
    print("      - Doctor's Decision: APPROVE")
    print("      - Approved Tests: (list the tests to approve)")
    print("      - Doctor's Assessment: (your medical opinion)")
    print("      - Updated by: Dr. [Your Name]")
    print("   4. Save the document")
    print()
    
    input("Press ENTER after you've updated the doctor's decision in the document...")
    print()
    
    print("Reading doctor's decision from document...")
    result = read_doctor_decision(doc_id)
    
    if result.get('success'):
        print("✅ Doctor's decision read successfully!")
        print()
        print(f"   Decision: {result['decision']}")
        print(f"   Approved Tests: {len(result['approved_tests'])} tests")
        for test in result['approved_tests']:
            print(f"      • {test}")
        print(f"   Doctor's Assessment: {result['doctor_assessment'][:100]}...")
        print()
        return True
    elif result.get('pending'):
        print("⏳ Doctor has not yet updated their decision")
        print("   Please update Section 3 in the document and try again")
        return False
    else:
        print(f"❌ Failed to read decision: {result.get('error')}")
        return False


def test_update_section(doc_id: str):
    """Test updating a section"""
    
    print_section("TEST 3: Update Document Section")
    
    print("Updating Section 4: Lab Test Scheduling...")
    
    lab_schedule_content = """
Lab Tests Scheduled:
  • ECG - Monday, Nov 18, 2024 at 10:00 AM
  • Echocardiogram - Monday, Nov 18, 2024 at 11:30 AM
  • Lipid Profile - Monday, Nov 18, 2024 at 9:00 AM (fasting required)
  • CBC - Monday, Nov 18, 2024 at 9:00 AM
  • Chest X-Ray - Monday, Nov 18, 2024 at 2:00 PM

Calendar Appointment Created:
  • Google Calendar Event ID: test_event_12345
  • Reminder sent to patient

Patient Instructions:
  • Fast for 12 hours before lipid profile test
  • Arrive 15 minutes early for registration
  • Bring ID and insurance card
  • Total estimated time: 3-4 hours
"""
    
    result = update_doc_section(
        doc_id=doc_id,
        section_name="4: LAB TEST SCHEDULING",
        content=lab_schedule_content,
        updated_by="AI Agent"
    )
    
    if result.get('success'):
        print("✅ Section updated successfully!")
        print("   Updated: Section 4 - Lab Test Scheduling")
        print()
        return True
    else:
        print(f"❌ Failed to update section: {result.get('error')}")
        return False


def main():
    """Run all tests"""
    
    print("\n" + "="*80)
    print("  UNIFIED WORKFLOW DOCUMENT TOOL - TEST SUITE")
    print("  Single Google Doc for Entire Patient Workflow")
    print("="*80)
    
    try:
        # Test 1: Create document
        doc_id, doc_url = test_create_workflow_doc()
        
        if not doc_id:
            print("\n❌ Test suite failed: Could not create document")
            return False
        
        # Test 2: Read doctor's decision
        decision_read = test_read_doctor_decision(doc_id, doc_url)
        
        # Test 3: Update section
        if decision_read:
            section_updated = test_update_section(doc_id)
        else:
            print("\n⚠️ Skipping section update test (doctor decision not read)")
            section_updated = False
        
        # Summary
        print_section("TEST SUMMARY")
        
        print("Test Results:")
        print(f"   {'✅' if doc_id else '❌'} Create Workflow Document")
        print(f"   {'✅' if decision_read else '❌'} Read Doctor's Decision")
        print(f"   {'✅' if section_updated else '❌'} Update Document Section")
        print()
        
        if doc_id:
            print(f"📄 Test Document: {doc_url}")
            print()
        
        if doc_id and decision_read and section_updated:
            print("🎉 **ALL TESTS PASSED!**")
            print()
            print("The unified workflow document tool is working correctly:")
            print("   ✅ Creates single doc for entire workflow")
            print("   ✅ Shares with doctor (pawarsamarth786@gmail.com)")
            print("   ✅ AI Agent can read doctor's updates")
            print("   ✅ AI Agent can update sections")
            print()
            return True
        else:
            print("⚠️ Some tests incomplete or failed")
            print("   Please review the errors above")
            return False
            
    except Exception as e:
        print(f"\n❌ Test error: {str(e)}")
        import traceback
        traceback.print_exc()
        return False


if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
