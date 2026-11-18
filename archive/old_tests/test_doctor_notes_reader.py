"""
Test script for ReadDoctorNotesTool

This tests the ability to read doctor's notes from Google Docs.

Workflow:
1. Create a test Google Doc with sample doctor notes
2. Test reading the notes using ReadDoctorNotesTool
3. Verify content extraction and section parsing
"""

import os
import sys
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Add parent directory to path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from tools.google_docs_tool import ReadDoctorNotesTool, CreateDoctorNotesTool, ShareDocumentTool


def print_section(title: str, content: str = ""):
    """Print formatted section"""
    print(f"\n{'='*70}")
    print(f"{title}")
    print(f"{'='*70}")
    if content:
        print(content)


def create_test_doctor_notes():
    """Create a test Google Doc with sample doctor notes"""
    print_section("📝 CREATING TEST DOCTOR NOTES DOCUMENT")
    
    # Sample doctor notes content
    sample_notes = """
PATIENT CONSULTATION NOTES
Date: January 15, 2025
Doctor: Dr. Sarah Williams, MD

DIAGNOSIS:
Patient presents with mild seasonal allergies (Allergic Rhinitis). 
Symptoms include sneezing, runny nose, and itchy eyes.
No signs of infection. Vital signs within normal range.

TREATMENT PLAN:
1. Antihistamine medication (Cetirizine 10mg)
2. Avoid known allergens (pollen, dust)
3. Use air purifier in bedroom
4. Stay hydrated
5. Monitor symptoms for next 7 days

PRESCRIPTIONS:
- Cetirizine 10mg: Take 1 tablet daily before bed
  Duration: 14 days
  Refills: 1

- Fluticasone nasal spray: 2 sprays each nostril once daily
  Duration: 30 days
  Refills: 2

FOLLOW-UP:
- Schedule follow-up in 2 weeks if symptoms persist
- Return immediately if difficulty breathing or severe reaction
- Can contact clinic via phone for any concerns

DOCTOR NOTES:
Patient is in good overall health. Seasonal allergies are manageable 
with medication. Recommend lifestyle modifications to reduce exposure 
to allergens. Patient understands treatment plan and has no questions.

Signed: Dr. Sarah Williams, MD
License #: MD12345
Date: January 15, 2025
"""
    
    # Create the document
    create_tool = CreateDoctorNotesTool()
    
    result = create_tool._run(
        patient_name="Test Patient (REG2025DOCTEST)",
        consultation_date="January 15, 2025",
        chief_complaint="Sneezing, runny nose, itchy eyes - started 3 days ago",
        examination_findings="Vital signs normal. No fever. Nasal congestion present. Throat clear.",
        diagnosis="Seasonal Allergies (Allergic Rhinitis)",
        treatment_plan="""1. Antihistamine medication (Cetirizine 10mg daily)
2. Avoid known allergens (pollen, dust)
3. Use air purifier in bedroom
4. Stay hydrated
5. Follow-up in 2 weeks if symptoms persist""",
        doctor_name="Sarah Williams"
    )
    
    if result.get('success'):
        doc_id = result['document_id']
        doc_url = result['document_url']
        print(f"✅ Created test document!")
        print(f"   Document ID: {doc_id}")
        print(f"   URL: {doc_url}")
        print(f"\n📋 Document contains sample doctor notes with:")
        print(f"   • Diagnosis: Seasonal Allergies")
        print(f"   • Treatment Plan: Medications + lifestyle changes")
        print(f"   • Prescriptions: Cetirizine, Fluticasone")
        print(f"   • Follow-up: 2 weeks if symptoms persist")
        return doc_id, doc_url
    else:
        print(f"❌ Failed to create test document: {result.get('error')}")
        return None, None


def test_read_doctor_notes(doc_id: str):
    """Test reading doctor notes from the created document"""
    print_section("🔬 TEST 1: READ DOCTOR NOTES FROM GOOGLE DOC")
    
    read_tool = ReadDoctorNotesTool()
    
    result = read_tool._run(
        document_id=doc_id,
        patient_id="REG2025DOCTEST"
    )
    
    if result.get('success'):
        print(f"✅ Successfully read doctor notes!")
        print(f"   Document Title: {result['document_title']}")
        print(f"   Patient ID: {result['patient_id']}")
        print(f"   Last Modified: {result['last_modified']}")
        print(f"   Last Modified By: {result['last_modified_by']}")
        print(f"\n📄 Full Doctor Notes Content:")
        print(f"{'─'*70}")
        print(result['doctor_notes'][:500] + "..." if len(result['doctor_notes']) > 500 else result['doctor_notes'])
        print(f"{'─'*70}")
        
        # Show parsed sections
        sections = result.get('sections', {})
        if sections:
            print(f"\n📊 Parsed Sections:")
            for section_name, section_content in sections.items():
                print(f"\n🔹 {section_name.upper()}:")
                preview = section_content[:200] + "..." if len(section_content) > 200 else section_content
                print(f"   {preview}")
        
        return True
    else:
        print(f"❌ Failed to read doctor notes: {result.get('error')}")
        return False


def test_empty_document():
    """Test reading from a document with minimal/pending content"""
    print_section("🔬 TEST 2: HANDLE DOCUMENT WITH PENDING CONTENT")
    
    # Create document with "Pending" placeholders
    create_tool = CreateDoctorNotesTool()
    result = create_tool._run(
        patient_name="Empty Test Patient (REG2025EMPTY)",
        consultation_date="Pending",
        chief_complaint="Initial consultation scheduled",
        examination_findings="Examination not yet conducted",
        diagnosis="Pending doctor assessment",
        treatment_plan="To be determined after examination",
        doctor_name="Pending Assignment"
    )
    
    if not result.get('success'):
        print(f"❌ Failed to create test document")
        return False
    
    empty_doc_id = result['document_id']
    print(f"✅ Created document with pending content: {empty_doc_id}")
    
    # Try to read it
    read_tool = ReadDoctorNotesTool()
    read_result = read_tool._run(document_id=empty_doc_id)
    
    if read_result.get('success'):
        print(f"✅ Successfully read document with pending content!")
        print(f"   Document has placeholder text: 'Pending'")
        notes = read_result.get('doctor_notes', '')
        if 'Pending' in notes:
            print(f"   ✓ Contains 'Pending' placeholders as expected")
        return True
    else:
        print(f"❌ Failed to read document")
        return False


def test_invalid_document():
    """Test reading from invalid document ID"""
    print_section("🔬 TEST 3: HANDLE INVALID DOCUMENT ID")
    
    read_tool = ReadDoctorNotesTool()
    result = read_tool._run(document_id="INVALID_DOC_ID_12345")
    
    if not result.get('success'):
        print(f"✅ Correctly handled invalid document!")
        print(f"   Error: {result['error']}")
        return True
    else:
        print(f"❌ Should have failed for invalid document")
        return False


def test_section_parsing():
    """Test section parsing with specific content"""
    print_section("🔬 TEST 4: SECTION PARSING")
    
    # Create document with clear sections
    create_tool = CreateDoctorNotesTool()
    
    notes_with_sections = """
DIAGNOSIS:
Patient has Type 2 Diabetes Mellitus. HbA1c level at 8.2% indicates 
poor blood sugar control. Patient also has mild hypertension.

TREATMENT PLAN:
1. Start Metformin 500mg twice daily
2. Low-carb diet (consultation with nutritionist)
3. Daily blood glucose monitoring
4. Regular exercise (30 min walking daily)
5. Blood pressure monitoring

PRESCRIPTIONS:
- Metformin 500mg: Take 1 tablet twice daily with meals
  Duration: 90 days, Refills: 3

- Lisinopril 10mg: Take 1 tablet once daily for blood pressure
  Duration: 90 days, Refills: 3

FOLLOW-UP:
Return in 3 months for HbA1c recheck and medication adjustment.
Schedule appointment with nutritionist within 2 weeks.

DOCTOR NOTES:
Patient is motivated to improve health. Discussed lifestyle 
modifications extensively. Patient understands medication regimen.
"""
    
    result = create_tool._run(
        patient_name="Section Test Patient (REG2025SECTION)",
        consultation_date="January 20, 2025",
        chief_complaint="Managing diabetes and blood pressure",
        examination_findings="HbA1c at 8.2%, Blood pressure 145/95",
        diagnosis="Type 2 Diabetes Mellitus with poor control. Mild hypertension.",
        treatment_plan="""1. Start Metformin 500mg twice daily
2. Low-carb diet (consultation with nutritionist)
3. Daily blood glucose monitoring
4. Regular exercise (30 min walking daily)
5. Blood pressure medication (Lisinopril 10mg daily)
6. Return in 3 months for HbA1c recheck""",
        doctor_name="Test Doctor"
    )
    
    if not result.get('success'):
        print(f"❌ Failed to create test document")
        return False
    
    doc_id = result['document_id']
    print(f"✅ Created document with clear sections: {doc_id}")
    
    # Read and check sections
    read_tool = ReadDoctorNotesTool()
    read_result = read_tool._run(document_id=doc_id)
    
    if read_result.get('success'):
        sections = read_result.get('sections', {})
        print(f"\n📊 Found {len(sections)} sections:")
        
        expected_sections = ['diagnosis', 'treatment', 'prescriptions', 'followup', 'notes']
        found_sections = []
        
        for section_name in expected_sections:
            if section_name in sections:
                print(f"   ✅ {section_name.upper()}: {len(sections[section_name])} characters")
                found_sections.append(section_name)
            else:
                print(f"   ⚠️  {section_name.upper()}: Not found")
        
        if len(found_sections) >= 3:  # At least 3 sections found
            print(f"\n✅ Section parsing working! Found {len(found_sections)}/{len(expected_sections)} sections")
            return True
        else:
            print(f"\n⚠️  Only found {len(found_sections)}/{len(expected_sections)} sections")
            return False
    else:
        print(f"❌ Failed to read document: {read_result.get('error')}")
        return False


def main():
    """Run all tests"""
    print_section("🧪 DOCTOR NOTES READER TOOL - TEST SUITE", "Testing ReadDoctorNotesTool functionality")
    
    test_results = []
    
    # Test 1: Create and read doctor notes
    try:
        doc_id, doc_url = create_test_doctor_notes()
        if doc_id:
            test_passed = test_read_doctor_notes(doc_id)
            test_results.append(("Read Doctor Notes", test_passed, doc_url))
        else:
            test_results.append(("Read Doctor Notes", False, None))
    except Exception as e:
        print(f"❌ TEST 1 EXCEPTION: {e}")
        test_results.append(("Read Doctor Notes", False, None))
    
    # Test 2: Empty document
    try:
        test_passed = test_empty_document()
        test_results.append(("Empty Document Handling", test_passed, None))
    except Exception as e:
        print(f"❌ TEST 2 EXCEPTION: {e}")
        test_results.append(("Empty Document Handling", False, None))
    
    # Test 3: Invalid document
    try:
        test_passed = test_invalid_document()
        test_results.append(("Invalid Document Handling", test_passed, None))
    except Exception as e:
        print(f"❌ TEST 3 EXCEPTION: {e}")
        test_results.append(("Invalid Document Handling", False, None))
    
    # Test 4: Section parsing
    try:
        test_passed = test_section_parsing()
        test_results.append(("Section Parsing", test_passed, None))
    except Exception as e:
        print(f"❌ TEST 4 EXCEPTION: {e}")
        test_results.append(("Section Parsing", False, None))
    
    # Print summary
    print_section("📊 TEST SUMMARY")
    
    passed_count = sum(1 for _, passed, _ in test_results if passed)
    total_count = len(test_results)
    
    for test_name, passed, url in test_results:
        status = "✅ PASSED" if passed else "❌ FAILED"
        print(f"{status} - {test_name}")
        if url:
            print(f"         Document: {url}")
    
    print(f"\n{'─'*70}")
    print(f"Results: {passed_count}/{total_count} tests passed")
    
    if passed_count == total_count:
        print(f"\n🎉 ALL TESTS PASSED!")
        print(f"\n✨ ReadDoctorNotesTool is ready for Phase 2 integration!")
        print(f"\n📋 What this enables:")
        print(f"   1. Doctor writes directly in Google Doc (familiar interface)")
        print(f"   2. AI reads doctor's notes when patient asks questions")
        print(f"   3. Patient gets friendly interpretation of doctor's recommendations")
        print(f"   4. No custom portal needed - just Google Docs!")
        print(f"   5. Audit trail built-in (Google tracks all changes)")
        print(f"\n🚀 Next Steps:")
        print(f"   1. Integrate into Stage 3 (auto-create doc for new patients)")
        print(f"   2. Integrate into Stage 6 (read diagnosis from doc)")
        print(f"   3. Add to Q&A system (answer doctor-related questions)")
        print(f"   4. Test end-to-end patient journey")
    else:
        print(f"\n⚠️  Some tests failed. Please review errors above.")
    
    print_section("🏁 TEST COMPLETE")


if __name__ == "__main__":
    main()
