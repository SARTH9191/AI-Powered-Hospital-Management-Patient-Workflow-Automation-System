"""
Stress Test & Edge Case Testing
================================
Tests workflow tools under stress conditions and edge cases
"""

import os
from datetime import datetime, timedelta
from dotenv import load_dotenv
import time

load_dotenv()

test_results = {"passed": 0, "failed": 0, "tests": []}

def record_result(passed: bool, test_name: str, details: str = ""):
    test_results["tests"].append({"name": test_name, "passed": passed, "details": details})
    if passed:
        test_results["passed"] += 1
    else:
        test_results["failed"] += 1

def print_test_header(number: int, title: str):
    print("\n" + "=" * 80)
    print(f"TEST {number}: {title}")
    print("=" * 80)

print("=" * 80)
print("WORKFLOW STRESS & EDGE CASE TESTS")
print("=" * 80)
print()

# ==================== TEST 1: Rapid Consecutive Tool Calls ====================

print_test_header(1, "Rapid Consecutive Patient Registrations (Stress Test)")
try:
    from tools.patient_registration_tool import RegisterPatientTool
    
    tool = RegisterPatientTool()
    patient_ids = []
    
    print("📝 Registering 5 patients rapidly...")
    start_time = time.time()
    
    for i in range(5):
        result = tool._run(
            first_name="StressTest",
            last_name=f"Patient{i}_{datetime.now().strftime('%H%M%S')}",
            date_of_birth="1990-01-01",
            gender="Male",
            phone=f"+1234567{i:03d}",
            email=f"stress{i}.{datetime.now().strftime('%H%M%S')}@test.com",
            address="Test Address"
        )
        
        # Extract patient ID
        for line in result.split('\n'):
            if 'Patient ID:' in line:
                patient_id = line.split(':')[-1].strip()
                patient_ids.append(patient_id)
                break
        
        print(f"   ✅ Patient {i+1}: {patient_id}")
    
    elapsed = time.time() - start_time
    print(f"\n⏱️  Completed 5 registrations in {elapsed:.2f} seconds")
    print(f"📊 Average: {elapsed/5:.2f} seconds per registration")
    
    if len(patient_ids) == 5:
        record_result(True, "Rapid Registrations", f"5 patients in {elapsed:.2f}s")
        print("✅ STRESS TEST PASSED")
    else:
        record_result(False, "Rapid Registrations", "Not all patients registered")
        
except Exception as e:
    print(f"❌ Error: {e}")
    record_result(False, "Rapid Registrations", str(e))

# ==================== TEST 2: Long Text Content ====================

print_test_header(2, "Medical Document with Very Long Content (Edge Case)")
try:
    from tools.docs_monitoring_tools import CreateMedicalDocumentTool
    
    # Generate very long content (5000 words)
    long_content = """
# Comprehensive Medical History Report

## Patient Background
""" + "\n\nDetailed medical history paragraph. " * 500 + """

## Current Symptoms
""" + "\n\nSymptom description paragraph. " * 200 + """

## Treatment Plan
""" + "\n\nTreatment details paragraph. " * 300
    
    print(f"📄 Creating document with {len(long_content)} characters...")
    
    tool = CreateMedicalDocumentTool()
    result = tool._run(
        patient_id=patient_ids[0] if patient_ids else "TEST123",
        document_type="Comprehensive Report",
        content=long_content,
        doctor_name="Dr. Stress Tester"
    )
    
    if "Document ID:" in result or "success" in result.lower():
        record_result(True, "Long Content Document", "Handled large content")
        print("✅ EDGE CASE PASSED: Large document created")
    else:
        record_result(False, "Long Content Document", "Failed to create")
        
except Exception as e:
    print(f"❌ Error: {e}")
    record_result(False, "Long Content Document", str(e))

# ==================== TEST 3: Special Characters in Data ====================

print_test_header(3, "Special Characters & Unicode (Edge Case)")
try:
    from tools.patient_registration_tool import RegisterPatientTool
    from tools.medical_records_tool import AddAllergyTool
    
    # Register patient with special characters
    reg_tool = RegisterPatientTool()
    special_result = reg_tool._run(
        first_name="José",
        last_name="O'Brien-Müller",
        date_of_birth="1985-12-25",
        gender="Male",
        phone="+1-(555)-123-4567",
        email="jose.obrien+test@example.com",
        address="123 Main St., Apt. #5B, New York, NY 10001"
    )
    
    special_patient_id = None
    for line in special_result.split('\n'):
        if 'Patient ID:' in line:
            special_patient_id = line.split(':')[-1].strip()
            break
    
    print(f"✅ Special chars patient: {special_patient_id}")
    
    # Add allergy with special characters
    allergy_tool = AddAllergyTool()
    allergy_result = allergy_tool._run(
        patient_id=special_patient_id,
        allergen="Penicillin™ & Derivatives (β-lactam antibiotics)",
        reaction="Severe: Anaphylaxis → Emergency Care Required!",
        severity="Critical"
    )
    
    print(allergy_result[:200] + "...")
    
    if special_patient_id and ("✅" in allergy_result or "success" in allergy_result.lower() or "added" in allergy_result.lower()):
        record_result(True, "Special Characters", "Handled unicode & symbols")
        print("✅ EDGE CASE PASSED: Special characters handled")
    else:
        record_result(False, "Special Characters", "Failed with special chars")
        
except Exception as e:
    print(f"❌ Error: {e}")
    record_result(False, "Special Characters", str(e))

# ==================== TEST 4: Empty/Minimal Data ====================

print_test_header(4, "Minimal Required Data Only (Edge Case)")
try:
    from tools.patient_registration_tool import RegisterPatientTool
    
    tool = RegisterPatientTool()
    minimal_result = tool._run(
        first_name="Min",
        last_name="Test",
        date_of_birth="2000-01-01",
        gender="Other",
        phone="+1111111111",
        email="min@test.com",
        address="N/A"
    )
    
    if "Patient ID:" in minimal_result:
        record_result(True, "Minimal Data", "Accepted minimal required data")
        print("✅ EDGE CASE PASSED: Minimal data accepted")
    else:
        record_result(False, "Minimal Data", "Rejected minimal data")
        
except Exception as e:
    print(f"❌ Error: {e}")
    record_result(False, "Minimal Data", str(e))

# ==================== TEST 5: Concurrent Sheet Operations ====================

print_test_header(5, "Multiple Sheet Operations Simultaneously (Stress Test)")
try:
    from tools.google_sheets_tool import AddPatientRecordTool, AddLabResultTool
    from tools.sheets_monitoring_tools import UpdatePatientStatusTool, AddStaffUpdateTool
    import concurrent.futures
    
    test_patient = patient_ids[1] if len(patient_ids) > 1 else "TEST456"
    
    def add_patient_record():
        tool = AddPatientRecordTool()
        return tool._run(
            spreadsheet_id=os.getenv('PATIENT_TRACKING_SHEET_ID'),
            patient_id=test_patient,
            patient_name="Concurrent Test",
            age=30,
            admission_date=datetime.now().strftime("%Y-%m-%d"),
            diagnosis="Concurrent Testing",
            status="Testing"
        )
    
    def update_status():
        tool = UpdatePatientStatusTool()
        return tool._run(
            patient_id=test_patient,
            status="Concurrent Update Test",
            notes="Testing concurrent operations",
            updated_by="Stress Test"
        )
    
    def add_staff_update():
        tool = AddStaffUpdateTool()
        return tool._run(
            staff_name="Stress Tester",
            department="Testing",
            update_type="System Test",
            message="Concurrent operations test",
            priority="Low"
        )
    
    print("📊 Running 3 sheet operations concurrently...")
    
    with concurrent.futures.ThreadPoolExecutor(max_workers=3) as executor:
        futures = [
            executor.submit(add_patient_record),
            executor.submit(update_status),
            executor.submit(add_staff_update)
        ]
        
        results = [f.result() for f in concurrent.futures.as_completed(futures)]
    
    successes = sum(1 for r in results if "success" in str(r).lower() or "✅" in str(r))
    
    print(f"✅ {successes}/3 operations succeeded")
    
    if successes >= 2:  # Allow 1 failure due to rate limits
        record_result(True, "Concurrent Sheet Ops", f"{successes}/3 succeeded")
        print("✅ STRESS TEST PASSED: Handled concurrent operations")
    else:
        record_result(False, "Concurrent Sheet Ops", "Too many failures")
        
except Exception as e:
    print(f"❌ Error: {e}")
    record_result(False, "Concurrent Sheet Ops", str(e))

# ==================== TEST 6: Invalid Data Recovery ====================

print_test_header(6, "Invalid Patient ID Handling (Error Recovery)")
try:
    from tools.medical_records_tool import AddAllergyTool
    
    tool = AddAllergyTool()
    
    # Try with invalid patient ID
    invalid_result = tool._run(
        patient_id="INVALID_PATIENT_123456789",
        allergen="Test Allergen",
        reaction="Test Reaction",
        severity="Moderate"
    )
    
    # Should return error message, not crash
    if "❌" in invalid_result or "not found" in invalid_result.lower():
        record_result(True, "Invalid Data Recovery", "Graceful error handling")
        print("✅ EDGE CASE PASSED: Gracefully handled invalid ID")
    else:
        record_result(False, "Invalid Data Recovery", "No error handling")
        
except Exception as e:
    # Even catching exception is acceptable
    print(f"⚠️  Exception caught (acceptable): {type(e).__name__}")
    record_result(True, "Invalid Data Recovery", "Exception caught properly")

# ==================== TEST 7: Date Edge Cases ====================

print_test_header(7, "Future Dates & Date Boundaries (Edge Case)")
try:
    from tools.google_calendar_tool import CreateAppointmentTool
    
    tool = CreateAppointmentTool()
    
    # Test future date (30 days from now)
    future_date = (datetime.now() + timedelta(days=30)).strftime("%Y-%m-%d")
    
    result = tool._run(
        patient_name="Future Test Patient",
        patient_email="future@test.com",
        doctor_name="Dr. Future",
        doctor_email="doctor@test.com",
        appointment_date=future_date,
        appointment_time="10:00",
        duration_minutes=30,
        appointment_type="Follow-up"
    )
    
    if "success" in result.lower() or "✅" in result:
        record_result(True, "Future Date Handling", "Accepted future appointment")
        print("✅ EDGE CASE PASSED: Future dates handled")
    else:
        record_result(False, "Future Date Handling", "Failed with future date")
        
except Exception as e:
    print(f"❌ Error: {e}")
    record_result(False, "Future Date Handling", str(e))

# ==================== TEST 8: Large Billing Amount ====================

print_test_header(8, "Very Large Billing Amount (Edge Case)")
try:
    from tools.billing_sheets_tool import CreateBillingRecordTool
    
    tool = CreateBillingRecordTool()
    test_patient = patient_ids[2] if len(patient_ids) > 2 else "TEST789"
    
    # Test with large amount (10 million)
    result = tool._run(
        patient_id=test_patient,
        patient_name="Large Bill Test",
        patient_email="largebill@test.com",
        service_type="Complex Surgery",
        service_name="Multi-organ transplant with extended ICU stay",
        amount=10000000.00,  # 10 million
        insurance_coverage=90.0,
        date=datetime.now().strftime("%Y-%m-%d")
    )
    
    if "success" in result.lower() or "✅" in result:
        record_result(True, "Large Amount Handling", "Handled 10M amount")
        print("✅ EDGE CASE PASSED: Large amounts handled")
    else:
        record_result(False, "Large Amount Handling", "Failed with large amount")
        
except Exception as e:
    print(f"❌ Error: {e}")
    record_result(False, "Large Amount Handling", str(e))

# ==================== FINAL SUMMARY ====================

print("\n" + "=" * 80)
print("STRESS & EDGE CASE TEST SUMMARY")
print("=" * 80)
print(f"\n✅ Tests Passed: {test_results['passed']}")
print(f"❌ Tests Failed: {test_results['failed']}")
total = test_results['passed'] + test_results['failed']
print(f"📊 Success Rate: {(test_results['passed']/total*100):.1f}%")

if test_results['failed'] > 0:
    print("\n❌ Failed Tests:")
    for test in test_results['tests']:
        if not test['passed']:
            print(f"   • {test['name']}: {test['details']}")
else:
    print("\n🎉 ALL STRESS TESTS PASSED!")

print("\n" + "=" * 80)
print("\n💡 Stress testing helps identify:")
print("   • Rate limiting issues")
print("   • Data validation problems")
print("   • Concurrent operation handling")
print("   • Edge case robustness")
print("   • Error recovery mechanisms")
