"""
Quick validation test for unified document reading
Tests that AI can properly read from all sections
"""

import os
os.environ['TESTING'] = 'true'

from tools.unified_workflow_doc_tool import (
    read_doctor_decision,
    read_doctor_consultation,
    read_lab_results,
    read_prescription_details
)

def test_section_reading():
    """Test reading all sections from the unified document"""
    
    # Use the existing patient's document
    doc_id = "1kAgV4vOZkrrh2FZeKmQ2r8CDp9w2MG6KfZiKuSXw_pY"
    
    print("\n" + "="*80)
    print("  📄 UNIFIED DOCUMENT READING VALIDATION")
    print("="*80 + "\n")
    
    print(f"Testing document: {doc_id}\n")
    
    # Test Section 3: Doctor's Decision
    print("="*80)
    print("TEST 1: Reading Section 3 (Doctor's Decision)")
    print("="*80)
    try:
        result = read_doctor_decision(doc_id)
        
        if result.get('pending'):
            print("❌ FAIL: Section 3 is pending (should be complete)")
        elif result.get('success'):
            print("✅ PASS: Section 3 read successfully")
            print(f"\n   Decision: {result.get('decision', 'N/A')}")
            print(f"   Approved: {result.get('approved', False)}")
            tests = result.get('recommended_tests', [])
            print(f"   Tests: {len(tests)} tests")
            for test in tests[:3]:
                print(f"      • {test}")
        else:
            print(f"❌ FAIL: {result.get('error', 'Unknown error')}")
    except Exception as e:
        print(f"❌ FAIL: Exception - {str(e)}")
    
    print("\n")
    
    # Test Section 5: Lab Results
    print("="*80)
    print("TEST 2: Reading Section 5 (Lab Results)")
    print("="*80)
    try:
        result = read_lab_results(doc_id)
        
        if result.get('pending'):
            print("❌ FAIL: Section 5 is pending (should have results)")
        elif result.get('success'):
            print("✅ PASS: Section 5 read successfully")
            print(f"\n   Total Tests: {result.get('total_tests', 0)}")
            print(f"   Normal: {result.get('normal_count', 0)}")
            print(f"   Abnormal: {result.get('abnormal_count', 0)}")
            
            tests = result.get('tests', [])
            print(f"\n   Parsed Tests:")
            for test in tests:
                print(f"      {test.get('status_icon', '?')} {test.get('test_name', 'Unknown')}")
                print(f"         Result: {test.get('result', 'N/A')}")
                print(f"         Status: {test.get('status', 'N/A')}")
            
            if result.get('ai_analysis'):
                print(f"\n   AI Analysis: {result.get('ai_analysis')[:100]}...")
        else:
            print(f"❌ FAIL: {result.get('error', 'Unknown error')}")
    except Exception as e:
        print(f"❌ FAIL: Exception - {str(e)}")
    
    print("\n")
    
    # Test Section 6: Doctor Consultation
    print("="*80)
    print("TEST 3: Reading Section 6 (Post-Lab Consultation)")
    print("="*80)
    try:
        result = read_doctor_consultation(doc_id)
        
        if result.get('pending'):
            print("⏳ PENDING: Section 6 not yet updated by doctor (expected)")
            print("   This is normal - doctor hasn't added post-lab consultation yet")
        elif result.get('success'):
            print("✅ PASS: Section 6 read successfully")
            print(f"\n   Diagnosis: {result.get('diagnosis', 'N/A')[:100]}...")
            print(f"   Treatment: {result.get('treatment_plan', 'N/A')[:100]}...")
        else:
            print(f"❌ FAIL: {result.get('error', 'Unknown error')}")
    except Exception as e:
        print(f"❌ FAIL: Exception - {str(e)}")
    
    print("\n")
    
    # Test Section 7: Prescription
    print("="*80)
    print("TEST 4: Reading Section 7 (Prescription)")
    print("="*80)
    try:
        result = read_prescription_details(doc_id)
        
        if result.get('pending'):
            print("❌ FAIL: Section 7 is pending (should have prescription)")
        elif result.get('success'):
            print("✅ PASS: Section 7 read successfully")
            
            medications = result.get('medications', [])
            print(f"\n   Medications: {len(medications)}")
            for med in medications:
                print(f"      💊 {med.get('name', 'Unknown')}")
                print(f"         Dosage: {med.get('dosage', 'N/A')}")
                print(f"         Timing: {med.get('timing', 'N/A')}")
                print(f"         Duration: {med.get('duration', 'N/A')}")
            
            safety = result.get('safety_measures', [])
            if safety:
                print(f"\n   Safety Measures: {len(safety)}")
                for measure in safety[:2]:
                    print(f"      ⚠️ {measure}")
            
            dietary = result.get('dietary_instructions', [])
            if dietary:
                print(f"\n   Dietary Instructions: {len(dietary)}")
                for instruction in dietary[:2]:
                    print(f"      🍽️ {instruction}")
            
            follow_up = result.get('follow_up_date')
            if follow_up:
                print(f"\n   Follow-up Date: {follow_up}")
                print(f"   Tests Required: {', '.join(result.get('follow_up_tests', []))}")
                print(f"   Location: {result.get('follow_up_location', 'N/A')}")
        else:
            print(f"❌ FAIL: {result.get('error', 'Unknown error')}")
    except Exception as e:
        print(f"❌ FAIL: Exception - {str(e)}")
    
    print("\n" + "="*80)
    print("  VALIDATION COMPLETE")
    print("="*80 + "\n")


if __name__ == "__main__":
    test_section_reading()
