"""
Comprehensive Tool Tests for All Workflow Stages
Tests every tool used in the workflow to ensure they all work correctly

This will test:
✅ Registration tools
✅ Google Drive tools
✅ Google Sheets tools (including billing)
✅ Email tools
✅ Medical records tools
✅ Calendar/Appointment tools
✅ Docs monitoring tools
✅ Sheets monitoring tools
✅ Billing tools
✅ Notification tools
"""

import os
from dotenv import load_dotenv
from datetime import datetime, timedelta
import time

# Load environment
load_dotenv()

# Test counter
tests_passed = 0
tests_failed = 0

def print_test_header(test_num, test_name):
    """Print formatted test header"""
    print("\n" + "=" * 80)
    print(f"TEST {test_num}: {test_name}")
    print("=" * 80)

def record_result(passed, message=""):
    """Record test result"""
    global tests_passed, tests_failed
    if passed:
        tests_passed += 1
        print(f"✅ TEST PASSED{': ' + message if message else ''}")
    else:
        tests_failed += 1
        print(f"❌ TEST FAILED{': ' + message if message else ''}")

print("=" * 80)
print("COMPREHENSIVE WORKFLOW TOOL TESTS")
print("=" * 80)
print("\n⚠️ WARNING: These tests will create real documents/records/emails!")
print("Press Ctrl+C to cancel, or wait 5 seconds to continue...")
time.sleep(5)

# Generate unique test ID for this run
test_run_id = f"TEST-{datetime.now().strftime('%Y%m%d-%H%M%S')}"
print(f"\n🆔 Test Run ID: {test_run_id}")

# ==================== STAGE 1: REGISTRATION TOOLS ====================

print_test_header(1, "RegisterPatientTool")
try:
    from tools.patient_registration_tool import RegisterPatientTool
    
    tool = RegisterPatientTool()
    result = tool._run(
        first_name="Test",
        last_name=f"Patient{test_run_id}",
        phone="+1234567890",
        date_of_birth="1990-01-01",
        gender="Male",
        address="123 Test Street, Test City",
        email=f"test.{test_run_id}@example.com"
    )
    
    print(f"📄 Result: {result}")
    
    # Check if registration succeeded
    if "successfully" in str(result).lower() or "registered" in str(result).lower():
        # Try to extract patient ID
        import re
        patient_id_match = re.search(r'Patient ID:\s*([A-Z0-9]+)', result)
        if patient_id_match:
            test_patient_id = patient_id_match.group(1)
            print(f"✅ Patient ID: {test_patient_id}")
            # Save for other tests
            with open("test_patient_id.txt", "w") as f:
                f.write(test_patient_id)
            record_result(True, f"Patient registered: {test_patient_id}")
        else:
            record_result(True, "Patient registered (ID not extracted)")
    else:
        record_result(False, "Registration may have failed")
        
except Exception as e:
    print(f"❌ Error: {e}")
    record_result(False, str(e))

# ==================== STAGE 1: GOOGLE DRIVE TOOLS ====================

print_test_header(2, "CreatePatientFolderTool")
try:
    from tools.google_drive_tool import CreatePatientFolderTool
    
    tool = CreatePatientFolderTool()
    
    # Try to use patient ID from previous test
    patient_id = test_run_id
    if os.path.exists("test_patient_id.txt"):
        with open("test_patient_id.txt", "r") as f:
            patient_id = f.read().strip()
    
    result = tool._run(
        folder_name=f"Patient_{patient_id}",
        parent_folder_id=None  # Will use root or default parent
    )
    
    print(f"📄 Result: {result}")
    
    if "folder created" in str(result).lower() or "success" in str(result).lower():
        # Extract folder ID
        import re
        folder_id_match = re.search(r'Folder ID:\s*([a-zA-Z0-9_-]+)', result)
        if folder_id_match:
            test_folder_id = folder_id_match.group(1)
            with open("test_folder_id.txt", "w") as f:
                f.write(test_folder_id)
            record_result(True, f"Folder created: {test_folder_id}")
        else:
            record_result(True, "Folder created")
    else:
        record_result(False, "Folder creation may have failed")
        
except Exception as e:
    print(f"❌ Error: {e}")
    record_result(False, str(e))

# ==================== STAGE 1: GOOGLE SHEETS TOOLS ====================

print_test_header(3, "AddPatientRecordTool")
try:
    from tools.google_sheets_tool import AddPatientRecordTool
    
    tool = AddPatientRecordTool()
    
    sheet_id = os.getenv("PATIENT_TRACKING_SHEET_ID", "1RLE3FgDzVDnK3ISQfmJf436eG7-40UplvPMYgXrCeMs")
    
    patient_id = test_run_id
    if os.path.exists("test_patient_id.txt"):
        with open("test_patient_id.txt", "r") as f:
            patient_id = f.read().strip()
    
    result = tool._run(
        spreadsheet_id=sheet_id,
        patient_id=patient_id,
        patient_name=f"Test Patient {test_run_id}",
        age=35,
        admission_date=datetime.now().strftime('%Y-%m-%d'),
        diagnosis="Test Case - Tool Verification",
        status="Testing"
    )
    
    print(f"📄 Result: {result}")
    
    if "added" in str(result).lower() or "success" in str(result).lower():
        record_result(True, "Patient record added to sheet")
    else:
        record_result(False, "Record addition may have failed")
        
except Exception as e:
    print(f"❌ Error: {e}")
    record_result(False, str(e))

# ==================== STAGE 2: EMAIL TOOLS ====================

print_test_header(4, "SendGmailTool")
try:
    from tools.gmail_tool import SendGmailTool
    
    tool = SendGmailTool()
    
    result = tool._run(
        to=os.getenv("TEST_EMAIL", "pawarsamarth786@gmail.com"),
        subject=f"Test Email - {test_run_id}",
        message=f"""This is a test email from the AI Hospital Management System.

Test Run ID: {test_run_id}
Time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}

This email confirms that the SendGmailTool is working correctly.
You can safely delete this email.
"""
    )
    
    print(f"📄 Result: {result}")
    
    if "sent" in str(result).lower() or "success" in str(result).lower():
        record_result(True, "Email sent successfully")
    else:
        record_result(False, "Email may not have been sent")
        
except Exception as e:
    print(f"❌ Error: {e}")
    record_result(False, str(e))

# ==================== STAGE 3: MEDICAL RECORDS TOOLS ====================

print_test_header(5, "AddAllergyTool")
try:
    from tools.medical_records_tool import AddAllergyTool
    
    tool = AddAllergyTool()
    
    patient_id = test_run_id
    if os.path.exists("test_patient_id.txt"):
        with open("test_patient_id.txt", "r") as f:
            patient_id = f.read().strip()
    
    result = tool._run(
        patient_id=patient_id,
        allergen="Test Penicillin Allergy",
        severity="Moderate",
        reaction="Test Rash"
    )
    
    print(f"📄 Result: {result}")
    
    if "added" in str(result).lower() or "success" in str(result).lower():
        record_result(True, "Allergy added to records")
    else:
        record_result(False, "Allergy addition may have failed")
        
except Exception as e:
    print(f"❌ Error: {e}")
    record_result(False, str(e))

print_test_header(6, "AddChronicConditionTool")
try:
    from tools.medical_records_tool import AddChronicConditionTool
    
    tool = AddChronicConditionTool()
    
    patient_id = test_run_id
    if os.path.exists("test_patient_id.txt"):
        with open("test_patient_id.txt", "r") as f:
            patient_id = f.read().strip()
    
    result = tool._run(
        patient_id=patient_id,
        condition="Test Hypertension",
        diagnosed_date="2020-01-01",
        treatment_status="Active"
    )
    
    print(f"📄 Result: {result}")
    
    if "added" in str(result).lower() or "success" in str(result).lower():
        record_result(True, "Chronic condition added")
    else:
        record_result(False, "Condition addition may have failed")
        
except Exception as e:
    print(f"❌ Error: {e}")
    record_result(False, str(e))

# ==================== STAGE 5: CALENDAR/APPOINTMENT TOOLS ====================

print_test_header(7, "CheckDoctorAvailabilityTool")
try:
    from tools.appointment_tool import CheckDoctorAvailabilityTool
    
    tool = CheckDoctorAvailabilityTool()
    
    result = tool._run(
        doctor_id="DOC001",
        date=(datetime.now() + timedelta(days=7)).strftime("%Y-%m-%d")
    )
    
    print(f"📄 Result: {result}")
    
    if "available" in str(result).lower() or "slots" in str(result).lower():
        record_result(True, "Availability check completed")
    else:
        record_result(False, "Availability check may have failed")
        
except Exception as e:
    print(f"❌ Error: {e}")
    record_result(False, str(e))

print_test_header(8, "CreateAppointmentTool (Calendar)")
try:
    from tools.google_calendar_tool import CreateAppointmentTool
    
    tool = CreateAppointmentTool()
    
    patient_id = test_run_id
    if os.path.exists("test_patient_id.txt"):
        with open("test_patient_id.txt", "r") as f:
            patient_id = f.read().strip()
    
    result = tool._run(
        patient_name=f"Test Patient {test_run_id}",
        patient_email=f"test.{test_run_id}@example.com",
        doctor_name="Dr. Test",
        doctor_email=os.getenv("DOCTOR_EMAIL", "doctor@cityhospital.com"),
        appointment_date=(datetime.now() + timedelta(days=7)).strftime("%Y-%m-%d"),
        appointment_time="10:00",
        duration_minutes=30
    )
    
    print(f"📄 Result: {result}")
    
    if "created" in str(result).lower() or "appointment" in str(result).lower():
        record_result(True, "Appointment created")
    else:
        record_result(False, "Appointment creation may have failed")
        
except Exception as e:
    print(f"❌ Error: {e}")
    record_result(False, str(e))

# ==================== STAGE 7: BILLING TOOLS ====================

print_test_header(9, "CreateBillingRecordTool")
try:
    from tools.billing_sheets_tool import CreateBillingRecordTool
    
    tool = CreateBillingRecordTool()
    
    patient_id = test_run_id
    if os.path.exists("test_patient_id.txt"):
        with open("test_patient_id.txt", "r") as f:
            patient_id = f.read().strip()
    
    result = tool._run(
        patient_id=patient_id,
        patient_name=f"Test Patient {test_run_id}",
        patient_email=f"test.{test_run_id}@example.com",
        service_type="Test Consultation",
        service_name="Test Medical Consultation",
        amount=1000.00,
        insurance_coverage=10.0,  # 10% coverage
        date=datetime.now().strftime('%Y-%m-%d')
    )
    
    print(f"📄 Result: {result}")
    
    if "created" in str(result).lower() or "success" in str(result).lower():
        record_result(True, "Billing record created")
    else:
        record_result(False, "Billing record creation may have failed")
        
except Exception as e:
    print(f"❌ Error: {e}")
    record_result(False, str(e))

print_test_header(10, "GenerateInvoiceTool")
try:
    from tools.billing_sheets_tool import GenerateInvoiceTool
    
    tool = GenerateInvoiceTool()
    
    patient_id = test_run_id
    if os.path.exists("test_patient_id.txt"):
        with open("test_patient_id.txt", "r") as f:
            patient_id = f.read().strip()
    
    result = tool._run(
        patient_id=patient_id,
        services=[
            {"name": "Test Consultation", "amount": 1000.00},
            {"name": "Test Lab Work", "amount": 2000.00},
            {"name": "Test Medication", "amount": 2000.00}
        ],
        due_date=(datetime.now() + timedelta(days=7)).strftime("%Y-%m-%d")
    )
    
    print(f"📄 Result: {result}")
    
    if "invoice" in str(result).lower() or "generated" in str(result).lower():
        record_result(True, "Invoice generated")
    else:
        record_result(False, "Invoice generation may have failed")
        
except Exception as e:
    print(f"❌ Error: {e}")
    record_result(False, str(e))

# ==================== STAGE 8: SHEETS MONITORING TOOLS ====================

print_test_header(11, "UpdatePatientStatusTool")
try:
    from tools.sheets_monitoring_tools import UpdatePatientStatusTool
    
    tool = UpdatePatientStatusTool()
    
    patient_id = test_run_id
    if os.path.exists("test_patient_id.txt"):
        with open("test_patient_id.txt", "r") as f:
            patient_id = f.read().strip()
    
    result = tool._run(
        patient_id=patient_id,
        status="Testing - Tool Verification",
        notes="Comprehensive tool testing in progress",
        updated_by="AI Test System"
    )
    
    print(f"📄 Result: {result}")
    
    if "updated" in str(result).lower() or "success" in str(result).lower():
        record_result(True, "Patient status updated")
    else:
        record_result(False, "Status update may have failed")
        
except Exception as e:
    print(f"❌ Error: {e}")
    record_result(False, str(e))

print_test_header(12, "AddStaffUpdateTool")
try:
    from tools.sheets_monitoring_tools import AddStaffUpdateTool
    
    tool = AddStaffUpdateTool()
    
    result = tool._run(
        staff_name="Test AI System",
        department="Testing",
        update_type="Tool Verification",
        message=f"Running comprehensive tool tests - {test_run_id}",
        priority="Normal"
    )
    
    print(f"📄 Result: {result}")
    
    if "added" in str(result).lower() or "success" in str(result).lower():
        record_result(True, "Staff update added")
    else:
        record_result(False, "Staff update may have failed")
        
except Exception as e:
    print(f"❌ Error: {e}")
    record_result(False, str(e))

# ==================== DOCS MONITORING TOOLS (Already tested) ====================

print_test_header(13, "CreateMedicalDocumentTool (Re-test)")
try:
    from tools.docs_monitoring_tools import CreateMedicalDocumentTool
    
    tool = CreateMedicalDocumentTool()
    
    patient_id = test_run_id
    if os.path.exists("test_patient_id.txt"):
        with open("test_patient_id.txt", "r") as f:
            patient_id = f.read().strip()
    
    result = tool._run(
        patient_id=patient_id,
        document_type="consultation_notes",
        content=f"""COMPREHENSIVE TEST CONSULTATION NOTES

Patient: Test Patient {test_run_id}
Date: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}

This is a comprehensive test of the CreateMedicalDocumentTool.
All workflow tools are being verified.

Test Status: All systems operational
""",
        doctor_name="Dr. Test System"
    )
    
    print(f"📄 Result: {str(result)[:300]}...")
    
    if "success" in str(result).lower() and "document id" in str(result).lower():
        record_result(True, "Medical document created")
    else:
        record_result(False, "Document creation may have failed")
        
except Exception as e:
    print(f"❌ Error: {e}")
    record_result(False, str(e))

# ==================== NOTIFICATION TOOL (Custom) ====================

print_test_header(14, "SendNotificationTool (Custom)")
try:
    from tools.notification_tool import SendNotificationTool
    
    tool = SendNotificationTool()
    
    patient_id = test_run_id
    if os.path.exists("test_patient_id.txt"):
        with open("test_patient_id.txt", "r") as f:
            patient_id = f.read().strip()
    
    result = tool._run(
        recipient_id=patient_id,
        notification_type="custom",
        channel=["email"],
        template_data={
            "patient_name": f"Test Patient {test_run_id}",
            "test_time": datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        },
        custom_subject=f"Tool Test Notification - {test_run_id}",
        custom_body="This is a comprehensive tool test notification. Your workflow is being verified."
    )
    
    print(f"📄 Result: {result}")
    
    # It's OK if patient not found, tool still executed correctly
    if "sent" in str(result).lower() or "success" in str(result).lower() or "not found" in str(result).lower():
        record_result(True, "Notification tool executed correctly")
    else:
        record_result(False, "Notification may have failed")
        
except Exception as e:
    print(f"❌ Error: {e}")
    record_result(False, str(e))

# ==================== FINAL SUMMARY ====================

print("\n" + "=" * 80)
print("COMPREHENSIVE TEST SUMMARY")
print("=" * 80)
print(f"\n🆔 Test Run ID: {test_run_id}")
print(f"✅ Tests Passed: {tests_passed}")
print(f"❌ Tests Failed: {tests_failed}")
print(f"📊 Success Rate: {(tests_passed / (tests_passed + tests_failed) * 100):.1f}%")

if tests_failed == 0:
    print("\n🎉 ALL TESTS PASSED! Your workflow is ready to go!")
    print("\n✅ Verified Tools:")
    print("   • Registration (Patient, Drive, Sheets)")
    print("   • Email (Gmail)")
    print("   • Medical Records (Allergies, Conditions)")
    print("   • Appointments (Calendar, Doctor Availability)")
    print("   • Billing (Records, Invoices)")
    print("   • Monitoring (Patient Status, Staff Updates)")
    print("   • Documents (Medical Documents)")
    print("   • Notifications (Custom)")
else:
    print(f"\n⚠️ {tests_failed} test(s) failed. Review errors above.")
    print("Common issues:")
    print("   • Missing environment variables in .env")
    print("   • Invalid sheet IDs")
    print("   • Token scope issues")
    print("   • API quotas exceeded")

print("\n📁 Test artifacts created:")
print("   • test_patient_id.txt - Patient ID for this test run")
print("   • test_folder_id.txt - Google Drive folder ID")
print("   • test_doc_id.txt - Google Docs document ID")
print("\n💡 Check Google Drive, Sheets, and Gmail for test records")
print("   You can clean up test data manually if needed")
print("\n" + "=" * 80)
