"""
Integration Test - Full Workflow Simulation
===========================================
Simulates a complete patient journey through all 12 stages
"""

import os
from datetime import datetime, timedelta
from dotenv import load_dotenv
import json

load_dotenv()

print("=" * 80)
print("FULL WORKFLOW INTEGRATION TEST")
print("Simulating complete patient journey through 12 stages")
print("=" * 80)
print()

# Track workflow state
workflow_state = {
    "patient_id": None,
    "patient_name": None,
    "patient_email": None,
    "folder_id": None,
    "appointment_id": None,
    "document_ids": [],
    "billing_records": [],
    "stage_results": {}
}

def print_stage_header(stage_num: int, title: str):
    print("\n" + "=" * 80)
    print(f"STAGE {stage_num}: {title}")
    print("=" * 80)

# ==================== STAGE 1: Registration ====================

print_stage_header(1, "Patient Registration")
try:
    from tools.patient_registration_tool import RegisterPatientTool
    
    tool = RegisterPatientTool()
    timestamp = datetime.now().strftime('%H%M%S')
    
    result = tool._run(
        first_name="Integration",
        last_name=f"TestPatient{timestamp}",
        date_of_birth="1985-06-15",
        gender="Female",
        phone="+1234567890",
        email=f"integration.{timestamp}@example.com",
        address="456 Integration Test Blvd, Test City"
    )
    
    print(result[:500] + "...")
    
    # Extract patient ID
    for line in result.split('\n'):
        if 'Patient ID:' in line:
            workflow_state["patient_id"] = line.split(':')[-1].strip()
            break
    
    workflow_state["patient_name"] = f"Integration TestPatient{timestamp}"
    workflow_state["patient_email"] = f"integration.{timestamp}@example.com"
    workflow_state["stage_results"]["registration"] = "✅ PASSED"
    
    print(f"\n✅ STAGE 1 COMPLETE: Patient {workflow_state['patient_id']} registered")
    
except Exception as e:
    print(f"❌ STAGE 1 FAILED: {e}")
    workflow_state["stage_results"]["registration"] = f"❌ FAILED: {e}"

# ==================== STAGE 2: Document Upload (Folder Creation) ====================

print_stage_header(2, "Document Upload - Folder Creation")
try:
    from tools.google_drive_tool import CreatePatientFolderTool
    
    tool = CreatePatientFolderTool()
    result = tool._run(
        folder_name=f"Patient_{workflow_state['patient_id']}",
        parent_folder_id=None
    )
    
    print(result[:300] + "...")
    
    # Extract folder ID
    for line in result.split('\n'):
        if 'Folder ID:' in line:
            workflow_state["folder_id"] = line.split(':')[-1].strip()
            break
    
    workflow_state["stage_results"]["document_upload"] = "✅ PASSED"
    print(f"\n✅ STAGE 2 COMPLETE: Folder {workflow_state['folder_id']} created")
    
except Exception as e:
    print(f"❌ STAGE 2 FAILED: {e}")
    workflow_state["stage_results"]["document_upload"] = f"❌ FAILED: {e}"

# ==================== STAGE 3: Medical History Collection ====================

print_stage_header(3, "Medical History Collection")
try:
    from tools.medical_records_tool import AddAllergyTool, AddChronicConditionTool
    from tools.docs_monitoring_tools import CreateMedicalDocumentTool
    from tools.sheets_monitoring_tools import AddDoctorNoteTool
    
    # Add allergies
    allergy_tool = AddAllergyTool()
    allergy1 = allergy_tool._run(
        patient_id=workflow_state["patient_id"],
        allergen="Penicillin",
        reaction="Rash and itching",
        severity="Moderate"
    )
    print("📋 Allergy added: Penicillin")
    
    # Add chronic condition
    chronic_tool = AddChronicConditionTool()
    chronic1 = chronic_tool._run(
        patient_id=workflow_state["patient_id"],
        condition="Hypertension",
        diagnosed_date="2020-01-15",
        treatment_status="Controlled with medication"
    )
    print("📋 Chronic condition added: Hypertension")
    
    # Create medical history document
    doc_tool = CreateMedicalDocumentTool()
    med_history = f"""
# Medical History Report
Patient: {workflow_state["patient_name"]}
ID: {workflow_state["patient_id"]}

## Allergies
- Penicillin (Moderate severity)

## Chronic Conditions
- Hypertension (Controlled)

## Current Medications
- Lisinopril 10mg daily
- Aspirin 81mg daily

Generated: {datetime.now().strftime('%Y-%m-%d %H:%M')}
"""
    
    doc_result = doc_tool._run(
        patient_id=workflow_state["patient_id"],
        document_type="Medical History",
        content=med_history,
        doctor_name="Integration Test System"
    )
    
    import re
    doc_id_match = re.search(r'Document ID:\*\*\s+([a-zA-Z0-9_-]+)', doc_result)
    if doc_id_match:
        workflow_state["document_ids"].append(doc_id_match.group(1))
        print(f"📄 Medical history document created: {doc_id_match.group(1)}")
    
    # Add doctor note
    note_tool = AddDoctorNoteTool()
    note_result = note_tool._run(
        patient_id=workflow_state["patient_id"],
        doctor_name="Dr. Integration Tester",
        note_type="Initial Assessment",
        note_content="Patient presents for routine checkup. Medical history documented. All systems stable.",
        priority="Normal"
    )
    print("📝 Doctor note added")
    
    workflow_state["stage_results"]["medical_history"] = "✅ PASSED"
    print("\n✅ STAGE 3 COMPLETE: Medical history collected")
    
except Exception as e:
    print(f"❌ STAGE 3 FAILED: {e}")
    workflow_state["stage_results"]["medical_history"] = f"❌ FAILED: {e}"

# ==================== STAGE 4: Doctor Approval Simulation ====================

print_stage_header(4, "Doctor Approval (Simulated)")
try:
    from tools.gmail_tool import SendGmailTool
    
    # Send notification email
    gmail_tool = SendGmailTool()
    email_result = gmail_tool._run(
        to=os.getenv('HOSPITAL_EMAIL'),
        subject=f"New Patient Registration - {workflow_state['patient_id']}",
        message=f"""
New patient registered and awaiting doctor approval:

Patient: {workflow_state['patient_name']}
ID: {workflow_state['patient_id']}
Email: {workflow_state['patient_email']}

Medical history has been documented.
Please review and approve for next steps.
"""
    )
    
    print("📧 Approval notification sent")
    workflow_state["stage_results"]["doctor_approval"] = "✅ PASSED"
    print("\n✅ STAGE 4 COMPLETE: Notification sent")
    
except Exception as e:
    print(f"❌ STAGE 4 FAILED: {e}")
    workflow_state["stage_results"]["doctor_approval"] = f"❌ FAILED: {e}"

# ==================== STAGE 5: Lab Test Determination ====================

print_stage_header(5, "Lab Test Determination")
try:
    from tools.google_sheets_tool import AddLabResultTool
    
    lab_tool = AddLabResultTool()
    
    # Add pending lab tests
    tests = ["Complete Blood Count (CBC)", "Lipid Profile", "HbA1c"]
    
    for test in tests:
        lab_result = lab_tool._run(
            spreadsheet_id=os.getenv('LAB_RESULTS_SHEET_ID'),
            patient_name=workflow_state["patient_name"],
            patient_id=workflow_state["patient_id"],
            test_name=test,
            result="PENDING - Sample Collection Scheduled",
            reference_range="To be determined",
            status="SCHEDULED",
            test_date=(datetime.now() + timedelta(days=1)).strftime("%Y-%m-%d")
        )
        print(f"🧪 Scheduled: {test}")
    
    workflow_state["stage_results"]["lab_determination"] = "✅ PASSED"
    print(f"\n✅ STAGE 5 COMPLETE: {len(tests)} lab tests scheduled")
    
except Exception as e:
    print(f"❌ STAGE 5 FAILED: {e}")
    workflow_state["stage_results"]["lab_determination"] = f"❌ FAILED: {e}"

# ==================== STAGE 6: Appointment Scheduling ====================

print_stage_header(6, "Appointment Scheduling")
try:
    from tools.google_calendar_tool import CreateAppointmentTool
    
    appt_tool = CreateAppointmentTool()
    appt_date = (datetime.now() + timedelta(days=2)).strftime("%Y-%m-%d")
    
    appt_result = appt_tool._run(
        patient_name=workflow_state["patient_name"],
        patient_email=workflow_state["patient_email"],
        doctor_name="Dr. Smith",
        doctor_email="doctor@cityhospital.com",
        appointment_date=appt_date,
        appointment_time="14:00",
        duration_minutes=45,
        appointment_type="Consultation"
    )
    
    print(appt_result[:300] + "...")
    
    workflow_state["stage_results"]["appointment"] = "✅ PASSED"
    print(f"\n✅ STAGE 6 COMPLETE: Appointment scheduled for {appt_date}")
    
except Exception as e:
    print(f"❌ STAGE 6 FAILED: {e}")
    workflow_state["stage_results"]["appointment"] = f"❌ FAILED: {e}"

# ==================== STAGE 7: Admission Planning ====================

print_stage_header(7, "Admission Planning")
try:
    from tools.google_sheets_tool import AddPatientRecordTool
    
    # Add to patient tracking
    tracking_tool = AddPatientRecordTool()
    tracking_result = tracking_tool._run(
        spreadsheet_id=os.getenv('PATIENT_TRACKING_SHEET_ID'),
        patient_id=workflow_state["patient_id"],
        patient_name=workflow_state["patient_name"],
        age=39,
        admission_date=datetime.now().strftime("%Y-%m-%d"),
        diagnosis="Routine checkup with lab tests",
        status="Active - Outpatient"
    )
    
    print("📊 Added to patient tracking system")
    
    workflow_state["stage_results"]["admission_planning"] = "✅ PASSED"
    print("\n✅ STAGE 7 COMPLETE: Patient added to tracking")
    
except Exception as e:
    print(f"❌ STAGE 7 FAILED: {e}")
    workflow_state["stage_results"]["admission_planning"] = f"❌ FAILED: {e}"

# ==================== STAGE 8: Billing & Insurance ====================

print_stage_header(8, "Billing & Insurance")
try:
    from tools.billing_sheets_tool import CreateBillingRecordTool
    
    billing_tool = CreateBillingRecordTool()
    
    # Create billing record
    billing_result = billing_tool._run(
        patient_id=workflow_state["patient_id"],
        patient_name=workflow_state["patient_name"],
        patient_email=workflow_state["patient_email"],
        service_type="Consultation",
        service_name="Initial Consultation with Lab Tests",
        amount=5000.00,
        insurance_coverage=80.0,
        date=datetime.now().strftime("%Y-%m-%d")
    )
    
    print(billing_result[:300] + "...")
    
    workflow_state["billing_records"].append("Initial consultation billing")
    workflow_state["stage_results"]["billing"] = "✅ PASSED"
    print("\n✅ STAGE 8 COMPLETE: Billing record created")
    
except Exception as e:
    print(f"❌ STAGE 8 FAILED: {e}")
    workflow_state["stage_results"]["billing"] = f"❌ FAILED: {e}"

# ==================== STAGE 9: Treatment Execution (Simulated) ====================

print_stage_header(9, "Treatment Execution (Simulated)")
try:
    from tools.sheets_monitoring_tools import UpdatePatientStatusTool
    
    status_tool = UpdatePatientStatusTool()
    status_result = status_tool._run(
        patient_id=workflow_state["patient_id"],
        status="Treatment in Progress - Lab samples collected",
        notes="Patient arrived for scheduled lab tests. Samples collected successfully. Results pending.",
        updated_by="Lab Technician"
    )
    
    print("🔄 Patient status updated")
    
    workflow_state["stage_results"]["treatment"] = "✅ PASSED"
    print("\n✅ STAGE 9 COMPLETE: Treatment recorded")
    
except Exception as e:
    print(f"❌ STAGE 9 FAILED: {e}")
    workflow_state["stage_results"]["treatment"] = f"❌ FAILED: {e}"

# ==================== STAGE 10: Lab Results (Simulated) ====================

print_stage_header(10, "Lab Results Entry")
try:
    from tools.google_sheets_tool import AddLabResultTool
    
    lab_tool = AddLabResultTool()
    
    # Update lab results
    results_data = [
        ("Complete Blood Count (CBC)", "Normal - All values within range", "WBC: 4.5-11, RBC: 4.5-5.5"),
        ("Lipid Profile", "Borderline High Cholesterol", "Total: <200, LDL: <100"),
        ("HbA1c", "Normal - 5.4%", "Normal: <5.7%")
    ]
    
    for test_name, result, ref_range in results_data:
        lab_result = lab_tool._run(
            spreadsheet_id=os.getenv('LAB_RESULTS_SHEET_ID'),
            patient_name=workflow_state["patient_name"],
            patient_id=workflow_state["patient_id"],
            test_name=test_name,
            result=result,
            reference_range=ref_range,
            status="COMPLETED",
            test_date=datetime.now().strftime("%Y-%m-%d")
        )
        print(f"✅ {test_name}: {result}")
    
    workflow_state["stage_results"]["lab_results"] = "✅ PASSED"
    print("\n✅ STAGE 10 COMPLETE: Lab results entered")
    
except Exception as e:
    print(f"❌ STAGE 10 FAILED: {e}")
    workflow_state["stage_results"]["lab_results"] = f"❌ FAILED: {e}"

# ==================== STAGE 11: Pharmacy (Simulated) ====================

print_stage_header(11, "Pharmacy & Prescriptions")
try:
    from tools.sheets_monitoring_tools import AddDoctorNoteTool
    
    # Doctor adds prescription note
    note_tool = AddDoctorNoteTool()
    prescription_note = note_tool._run(
        patient_id=workflow_state["patient_id"],
        doctor_name="Dr. Smith",
        note_type="Prescription",
        note_content="""
Prescription based on lab results:
1. Continue Lisinopril 10mg daily (Hypertension management)
2. Continue Aspirin 81mg daily
3. Add Atorvastatin 10mg daily (For borderline high cholesterol)

Follow-up in 3 months for repeat lipid panel.
""",
        priority="Normal"
    )
    
    print("💊 Prescription issued")
    
    workflow_state["stage_results"]["pharmacy"] = "✅ PASSED"
    print("\n✅ STAGE 11 COMPLETE: Prescription documented")
    
except Exception as e:
    print(f"❌ STAGE 11 FAILED: {e}")
    workflow_state["stage_results"]["pharmacy"] = f"❌ FAILED: {e}"

# ==================== STAGE 12: Discharge ====================

print_stage_header(12, "Discharge & Follow-up")
try:
    from tools.sheets_monitoring_tools import UpdatePatientStatusTool, AddStaffUpdateTool
    from tools.gmail_tool import SendGmailTool
    
    # Update final status
    status_tool = UpdatePatientStatusTool()
    final_status = status_tool._run(
        patient_id=workflow_state["patient_id"],
        status="Discharged - Outpatient Care Complete",
        notes="All tests completed. Prescriptions issued. Follow-up scheduled in 3 months.",
        updated_by="Dr. Smith"
    )
    
    # Add staff update
    staff_tool = AddStaffUpdateTool()
    staff_update = staff_tool._run(
        staff_name="Dr. Smith",
        department="Outpatient Care",
        update_type="Patient Discharge",
        message=f"Patient {workflow_state['patient_id']} completed outpatient care successfully. Follow-up required.",
        priority="Normal"
    )
    
    # Send discharge email
    gmail_tool = SendGmailTool()
    discharge_email = gmail_tool._run(
        to=workflow_state["patient_email"],
        subject="Care Complete - Next Steps",
        message=f"""
Dear {workflow_state['patient_name']},

Your recent visit has been completed successfully.

Lab Results Summary:
- CBC: Normal
- Lipid Profile: Borderline high cholesterol
- HbA1c: Normal

New Prescription:
- Atorvastatin 10mg daily has been added to your medications

Follow-up: Please schedule appointment in 3 months

Thank you for choosing our care!
"""
    )
    
    print("📧 Discharge instructions sent")
    
    workflow_state["stage_results"]["discharge"] = "✅ PASSED"
    print("\n✅ STAGE 12 COMPLETE: Patient discharged successfully")
    
except Exception as e:
    print(f"❌ STAGE 12 FAILED: {e}")
    workflow_state["stage_results"]["discharge"] = f"❌ FAILED: {e}"

# ==================== FINAL REPORT ====================

print("\n" + "=" * 80)
print("FULL WORKFLOW INTEGRATION TEST - FINAL REPORT")
print("=" * 80)
print()

print("📊 WORKFLOW STATE:")
print(f"   Patient ID: {workflow_state['patient_id']}")
print(f"   Patient Name: {workflow_state['patient_name']}")
print(f"   Folder ID: {workflow_state['folder_id']}")
print(f"   Documents Created: {len(workflow_state['document_ids'])}")
print(f"   Billing Records: {len(workflow_state['billing_records'])}")
print()

print("📋 STAGE RESULTS:")
stages = [
    "registration", "document_upload", "medical_history", "doctor_approval",
    "lab_determination", "appointment", "admission_planning", "billing",
    "treatment", "lab_results", "pharmacy", "discharge"
]

passed = 0
failed = 0

for i, stage in enumerate(stages, 1):
    result = workflow_state["stage_results"].get(stage, "⚠️ NOT RUN")
    status = "✅" if "PASSED" in result else "❌" if "FAILED" in result else "⚠️"
    print(f"   Stage {i:2d}: {status} {stage.replace('_', ' ').title()}")
    
    if "PASSED" in result:
        passed += 1
    elif "FAILED" in result:
        failed += 1

print()
print(f"✅ Stages Passed: {passed}/{len(stages)}")
print(f"❌ Stages Failed: {failed}/{len(stages)}")
print(f"📊 Success Rate: {(passed/len(stages)*100):.1f}%")

if passed == len(stages):
    print("\n🎉 FULL WORKFLOW TEST PASSED! All 12 stages completed successfully!")
    print("\n✨ Your workflow is ready for production use!")
else:
    print("\n⚠️ Some stages failed. Review errors above.")

print("\n" + "=" * 80)
print("\n💡 This test simulates a complete patient journey from registration to discharge.")
print("   All data created can be found in your Google Sheets and Drive.")
print(f"   Search for Patient ID: {workflow_state['patient_id']}")
