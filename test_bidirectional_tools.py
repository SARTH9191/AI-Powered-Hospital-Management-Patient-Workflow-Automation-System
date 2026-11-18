"""
Bidirectional Tool Testing
==========================
Tests tools that both WRITE and READ data to verify full workflow
"""

import os
from datetime import datetime, timedelta
from dotenv import load_dotenv

load_dotenv()

# Test results tracking
test_results = {"passed": 0, "failed": 0, "tests": []}

def record_result(passed: bool, test_name: str, details: str = ""):
    """Record test result"""
    test_results["tests"].append({
        "name": test_name,
        "passed": passed,
        "details": details
    })
    if passed:
        test_results["passed"] += 1
    else:
        test_results["failed"] += 1

def print_test_header(number: int, title: str):
    """Print formatted test header"""
    print("\n" + "=" * 80)
    print(f"TEST {number}: {title}")
    print("=" * 80)

def print_summary():
    """Print final test summary"""
    total = test_results["passed"] + test_results["failed"]
    success_rate = (test_results["passed"] / total * 100) if total > 0 else 0
    
    print("\n" + "=" * 80)
    print("BIDIRECTIONAL TOOL TEST SUMMARY")
    print("=" * 80)
    print(f"\n✅ Tests Passed: {test_results['passed']}")
    print(f"❌ Tests Failed: {test_results['failed']}")
    print(f"📊 Success Rate: {success_rate:.1f}%")
    print()
    
    if test_results["failed"] > 0:
        print("❌ Failed Tests:")
        for test in test_results["tests"]:
            if not test["passed"]:
                print(f"   • {test['name']}: {test['details']}")
    else:
        print("🎉 ALL BIDIRECTIONAL TESTS PASSED!")
    
    print("\n" + "=" * 80)

# Generate unique test ID
TEST_RUN_ID = f"BIDIR-{datetime.now().strftime('%Y%m%d-%H%M%S')}"

print("=" * 80)
print("BIDIRECTIONAL TOOL TESTS")
print("Testing tools that write data AND read it back")
print("=" * 80)
print(f"\n🆔 Test Run ID: {TEST_RUN_ID}\n")

# ==================== TEST 1: Register Patient → Read Patient Record ====================

print_test_header(1, "RegisterPatientTool → AddPatientRecordTool → Read Back")
patient_id = None  # Initialize patient_id for later tests
try:
    from tools.patient_registration_tool import RegisterPatientTool
    from tools.google_sheets_tool import AddPatientRecordTool
    from tools.database_tool import ReadRecordTool
    
    # Step 1: Register patient
    print("📝 Step 1: Registering new patient...")
    register_tool = RegisterPatientTool()
    register_result = register_tool._run(
        first_name="Bidirectional",
        last_name=f"Test{TEST_RUN_ID}",
        date_of_birth="1995-05-15",
        gender="Female",
        phone="+1234567890",
        email=f"bidir.{TEST_RUN_ID}@example.com",
        address="456 Test Avenue"
    )
    
    # Extract patient ID
    for line in register_result.split('\n'):
        if 'Patient ID:' in line:
            patient_id = line.split(':')[-1].strip()
            break
    
    if not patient_id:
        raise Exception("Could not extract patient ID from registration")
    
    print(f"✅ Patient registered: {patient_id}")
    print()
    
    # Step 2: Add to monitoring sheet
    print("📊 Step 2: Adding patient to monitoring sheet...")
    add_record_tool = AddPatientRecordTool()
    add_result = add_record_tool._run(
        spreadsheet_id=os.getenv('PATIENT_TRACKING_SHEET_ID'),
        patient_id=patient_id,
        patient_name=f"Bidirectional Test{TEST_RUN_ID}",
        age=30,
        admission_date=datetime.now().strftime("%Y-%m-%d"),
        diagnosis="Test - Bidirectional Verification",
        status="Active Testing"
    )
    print(add_result[:200] + "...")
    print()
    
    # Step 3: Read back from database
    print("🔍 Step 3: Reading patient record from database...")
    read_tool = ReadRecordTool()
    read_result = read_tool._run(table_name="patients", record_id=patient_id)
    print(read_result[:300] + "...")
    
    # Verify data matches
    if patient_id in str(read_result) and ("Bidirectional" in str(read_result) or "success" in str(read_result).lower()):
        record_result(True, "Patient Registration → Sheet → Read Back", "Data verified")
        print("\n✅ BIDIRECTIONAL TEST PASSED: Data written and read successfully!")
    else:
        record_result(False, "Patient Registration → Sheet → Read Back", "Data mismatch")
        print("\n❌ TEST FAILED: Data not found or mismatch")
        
except Exception as e:
    print(f"❌ Error: {e}")
    record_result(False, "Patient Registration → Sheet → Read Back", str(e))
    # Set dummy patient_id if test 1 fails so other tests can attempt to run
    if not patient_id:
        patient_id = "TEST_PATIENT_FALLBACK"

# ==================== TEST 2: Create Billing → Read Billing Info ====================

print_test_header(2, "CreateBillingRecordTool → ReadBillingInfoTool")
try:
    if not patient_id or patient_id == "TEST_PATIENT_FALLBACK":
        raise Exception("Patient ID not available from test 1")
    
    from tools.billing_sheets_tool import CreateBillingRecordTool, ReadBillingInfoTool
    
    # Step 1: Create billing record
    print("💰 Step 1: Creating billing record...")
    create_billing_tool = CreateBillingRecordTool()
    billing_result = create_billing_tool._run(
        patient_id=patient_id,
        patient_name=f"Bidirectional Test{TEST_RUN_ID}",
        patient_email=f"bidir.{TEST_RUN_ID}@example.com",
        service_type="Consultation",
        service_name="Initial Assessment - Bidirectional Test",
        amount=250.00,
        insurance_coverage=70.0,
        date=datetime.now().strftime("%Y-%m-%d")
    )
    print(billing_result[:300] + "...")
    
    # Extract billing record ID
    billing_id = None
    for line in billing_result.split('\n'):
        if 'Record ID:' in line:
            billing_id = line.split(':')[-1].strip()
            break
    
    print(f"\n✅ Billing record created: {billing_id}")
    print()
    
    # Step 2: Read billing info back
    print("🔍 Step 2: Reading billing information...")
    read_billing_tool = ReadBillingInfoTool()
    billing_info = read_billing_tool._run(
        patient_id=patient_id,
        include_pending=True,
        include_paid=True
    )
    print(billing_info[:400] + "...")
    
    # Verify billing data
    if (billing_id and billing_id in str(billing_info)) or "Initial Assessment" in str(billing_info):
        record_result(True, "Create Billing → Read Billing", "Billing data verified")
        print("\n✅ BIDIRECTIONAL TEST PASSED: Billing written and read successfully!")
    else:
        record_result(False, "Create Billing → Read Billing", "Billing data not found")
        print("\n❌ TEST FAILED: Billing data not found")
        
except Exception as e:
    print(f"❌ Error: {e}")
    record_result(False, "Create Billing → Read Billing", str(e))

# ==================== TEST 3: Add Allergy → Read Patient Medical Record ====================

print_test_header(3, "AddAllergyTool → Read Back from Database")
try:
    if not patient_id or patient_id == "TEST_PATIENT_FALLBACK":
        raise Exception("Patient ID not available from test 1")
    
    from tools.medical_records_tool import AddAllergyTool
    import json
    
    # Step 1: Add allergy
    print("⚠️  Step 1: Adding allergy to patient record...")
    allergy_tool = AddAllergyTool()
    allergy_result = allergy_tool._run(
        patient_id=patient_id,
        allergen="Bidirectional Test Allergen",
        reaction="Test Reaction - Verification",
        severity="High"
    )
    print(allergy_result[:300] + "...")
    print()
    
    # Step 2: Read from database file
    print("🔍 Step 2: Reading patient allergies from database...")
    patients_db_path = os.path.join('data', 'patients_database.json')
    
    with open(patients_db_path, 'r') as f:
        patients_db = json.load(f)
    
    # Handle both list and dict formats
    if isinstance(patients_db, list):
        patient_record = next((p for p in patients_db if p.get('patient_id') == patient_id), None)
    elif isinstance(patients_db, dict):
        patient_record = patients_db.get(patient_id)
    else:
        patient_record = None
    
    if patient_record and 'allergies' in patient_record:
        allergies = patient_record['allergies']
        print(f"📋 Found {len(allergies)} allergy(ies)")
        
        # Check if our test allergy is there
        test_allergy = next((a for a in allergies if 'Bidirectional Test' in a.get('allergen', '')), None)
        
        if test_allergy:
            print(f"✅ Test allergy found: {test_allergy['allergen']}")
            print(f"   Severity: {test_allergy['severity']}")
            print(f"   Reaction: {test_allergy['reaction']}")
            record_result(True, "Add Allergy → Read Back", "Allergy verified in database")
            print("\n✅ BIDIRECTIONAL TEST PASSED: Allergy written and read successfully!")
        else:
            record_result(False, "Add Allergy → Read Back", "Test allergy not found")
            print("\n❌ TEST FAILED: Test allergy not found in database")
    else:
        record_result(False, "Add Allergy → Read Back", "Patient record or allergies field missing")
        print("\n❌ TEST FAILED: Patient record not found")
        
except Exception as e:
    print(f"❌ Error: {e}")
    record_result(False, "Add Allergy → Read Back", str(e))

# ==================== TEST 4: Update Patient Status → Read Status Back ====================

print_test_header(4, "UpdatePatientStatusTool → Read Status from Sheet")
try:
    if not patient_id or patient_id == "TEST_PATIENT_FALLBACK":
        raise Exception("Patient ID not available from test 1")
    
    from tools.sheets_monitoring_tools import UpdatePatientStatusTool
    from googleapiclient.discovery import build
    import pickle
    
    # Step 1: Update patient status
    print("🔄 Step 1: Updating patient status...")
    update_tool = UpdatePatientStatusTool()
    update_result = update_tool._run(
        patient_id=patient_id,
        status="Bidirectional Test - Status Verification",
        notes=f"Testing bidirectional data flow - {TEST_RUN_ID}",
        updated_by="Bidirectional Test System"
    )
    print(update_result[:300] + "...")
    print()
    
    # Step 2: Read status from sheet directly
    print("🔍 Step 2: Reading patient status from Google Sheets...")
    
    # Initialize sheets service
    token_path = 'sheets_token.pickle'
    with open(token_path, 'rb') as token:
        creds = pickle.load(token)
    
    service = build('sheets', 'v4', credentials=creds)
    sheet_id = os.getenv('PATIENT_STATUS_SHEET_ID')
    
    # Read all status updates
    result = service.spreadsheets().values().get(
        spreadsheetId=sheet_id,
        range='Sheet1!A:F'
    ).execute()
    
    rows = result.get('values', [])
    
    # Find our test patient's status
    found = False
    for row in rows:
        if len(row) > 0 and patient_id in str(row):
            print(f"📋 Found status update: {row}")
            if "Bidirectional Test" in str(row):
                found = True
                record_result(True, "Update Status → Read Status", "Status verified in sheet")
                print("\n✅ BIDIRECTIONAL TEST PASSED: Status updated and verified!")
                break
    
    if not found:
        record_result(False, "Update Status → Read Status", "Status not found in sheet")
        print("\n❌ TEST FAILED: Status update not found in sheet")
        
except Exception as e:
    print(f"❌ Error: {e}")
    record_result(False, "Update Status → Read Status", str(e))

# ==================== TEST 5: Create Medical Document → Share → Verify Permissions ====================

print_test_header(5, "CreateMedicalDocumentTool → ShareDocumentTool → Verify Access")
try:
    if not patient_id or patient_id == "TEST_PATIENT_FALLBACK":
        raise Exception("Patient ID not available from test 1")
    
    from tools.docs_monitoring_tools import CreateMedicalDocumentTool, ShareMedicalDocumentTool
    from googleapiclient.discovery import build
    import pickle
    import re
    
    # Step 1: Create medical document
    print("📄 Step 1: Creating medical document...")
    create_doc_tool = CreateMedicalDocumentTool()
    doc_result = create_doc_tool._run(
        patient_id=patient_id,
        document_type="Test Report",
        content=f"# Bidirectional Test Document\n\nTest ID: {TEST_RUN_ID}\n\nThis document tests bidirectional tool flow.",
        doctor_name="Dr. Bidirectional Tester"
    )
    
    # Extract document ID
    doc_id_match = re.search(r'Document ID:\*\*\s+([a-zA-Z0-9_-]+)', doc_result)
    doc_id = doc_id_match.group(1) if doc_id_match else None
    
    print(f"✅ Document created: {doc_id}")
    print()
    
    if not doc_id:
        print("❌ Could not extract document ID")
        record_result(False, "Create Doc → Share → Verify", "Document ID extraction failed")
    else:
        # Step 2: Share document
        print("🔗 Step 2: Sharing document with test email...")
        share_tool = ShareMedicalDocumentTool()
        share_result = share_tool._run(
            document_id=doc_id,
            email=f"bidir.{TEST_RUN_ID}@example.com",
            role="reader"
        )
        print(share_result[:300] + "...")
        print()
        
        # Step 3: Verify permissions
        print("🔍 Step 3: Verifying document permissions...")
        
        # Initialize Drive service
        token_path = 'drive_token.pickle'
        with open(token_path, 'rb') as token:
            creds = pickle.load(token)
        
        drive_service = build('drive', 'v3', credentials=creds)
        
        # Get document permissions
        permissions = drive_service.permissions().list(
            fileId=doc_id,
            fields='permissions(emailAddress,role)'
        ).execute()
        
        # Check if test email has access
        test_email = f"bidir.{TEST_RUN_ID}@example.com"
        found_permission = False
        
        for perm in permissions.get('permissions', []):
            if perm.get('emailAddress') == test_email:
                print(f"✅ Permission found: {test_email} - Role: {perm.get('role')}")
                found_permission = True
                break
        
        if found_permission:
            record_result(True, "Create Doc → Share → Verify", "Document shared and verified")
            print("\n✅ BIDIRECTIONAL TEST PASSED: Document created, shared, and verified!")
        else:
            record_result(False, "Create Doc → Share → Verify", "Permission not found")
            print("\n❌ TEST FAILED: Permission not found on document")
        
except Exception as e:
    print(f"❌ Error: {e}")
    record_result(False, "Create Doc → Share → Verify", str(e))

# ==================== TEST 6: Add Lab Result → Read Lab Results ====================

print_test_header(6, "AddLabResultTool → Read Lab Results from Sheet")
try:
    if not patient_id or patient_id == "TEST_PATIENT_FALLBACK":
        raise Exception("Patient ID not available from test 1")
    
    from tools.google_sheets_tool import AddLabResultTool
    from googleapiclient.discovery import build
    import pickle
    
    # Step 1: Add lab result
    print("🧪 Step 1: Adding lab result...")
    lab_tool = AddLabResultTool()
    lab_result = lab_tool._run(
        spreadsheet_id=os.getenv('LAB_RESULTS_SHEET_ID'),
        patient_name=f"Bidirectional Test{TEST_RUN_ID}",
        patient_id=patient_id,
        test_name="Bidirectional Test - CBC",
        result="Normal - Bidirectional Verification",
        reference_range="Test Range",
        status="Completed",
        test_date=datetime.now().strftime("%Y-%m-%d")
    )
    print(lab_result[:300] + "...")
    print()
    
    # Step 2: Read from sheet
    print("🔍 Step 2: Reading lab results from Google Sheets...")
    
    token_path = 'sheets_token.pickle'
    with open(token_path, 'rb') as token:
        creds = pickle.load(token)
    
    service = build('sheets', 'v4', credentials=creds)
    sheet_id = os.getenv('LAB_RESULTS_SHEET_ID')
    
    # Try to detect sheet name dynamically
    spreadsheet = service.spreadsheets().get(spreadsheetId=sheet_id).execute()
    sheets = spreadsheet.get('sheets', [])
    
    # Look for lab results sheet
    sheet_name = None
    for sheet in sheets:
        title = sheet['properties']['title'].lower()
        if 'lab' in title or 'test' in title or 'result' in title:
            sheet_name = sheet['properties']['title']
            break
    
    if not sheet_name and sheets:
        sheet_name = sheets[0]['properties']['title']
    
    # Read data
    result = service.spreadsheets().values().get(
        spreadsheetId=sheet_id,
        range=f'{sheet_name}!A:H'
    ).execute()
    
    rows = result.get('values', [])
    
    # Find our test result
    found = False
    for row in rows:
        if len(row) > 0 and patient_id in str(row) and "Bidirectional Test - CBC" in str(row):
            print(f"📋 Found lab result: {row[:4]}...")
            found = True
            record_result(True, "Add Lab Result → Read Back", "Lab result verified in sheet")
            print("\n✅ BIDIRECTIONAL TEST PASSED: Lab result added and verified!")
            break
    
    if not found:
        record_result(False, "Add Lab Result → Read Back", "Lab result not found")
        print("\n⚠️  TEST WARNING: Lab result not found (may take a moment to appear)")
        
except Exception as e:
    print(f"❌ Error: {e}")
    record_result(False, "Add Lab Result → Read Back", str(e))

# ==================== TEST 7: Add Doctor Note → Read Doctor Notes ====================

print_test_header(7, "AddDoctorNoteTool → ReadDoctorNotesTool")
try:
    from tools.sheets_monitoring_tools import AddDoctorNoteTool, ReadDoctorNotesTool
    
    if not patient_id:
        raise ValueError("Patient ID not available from previous tests")
    
    # Step 1: Add doctor note
    print("📝 Step 1: Adding doctor note...")
    add_note_tool = AddDoctorNoteTool()
    note_result = add_note_tool._run(
        patient_id=patient_id,
        doctor_name="Dr. Bidirectional Tester",
        note_type="Assessment",
        note_content=f"Bidirectional test note - {TEST_RUN_ID}. Patient showing excellent progress in test verification workflow. All systems functioning correctly.",
        priority="Normal"
    )
    print(note_result[:300] + "...")
    print()
    
    # Step 2: Read doctor notes back
    print("🔍 Step 2: Reading doctor notes from Google Sheets...")
    read_notes_tool = ReadDoctorNotesTool()
    notes_info = read_notes_tool._run(
        patient_id=patient_id,
        limit=10
    )
    print(notes_info[:400] + "...")
    
    # Also try reading directly from sheet to verify
    import pickle
    from googleapiclient.discovery import build
    
    token_path = 'sheets_token.pickle'
    with open(token_path, 'rb') as token:
        creds = pickle.load(token)
    
    service = build('sheets', 'v4', credentials=creds)
    sheet_id = os.getenv('DOCTOR_NOTES_SHEET_ID')
    
    # Read all notes
    result = service.spreadsheets().values().get(
        spreadsheetId=sheet_id,
        range='Sheet1!A:F'
    ).execute()
    
    rows = result.get('values', [])
    note_found = False
    
    # Search for our test note
    for row in rows:
        if len(row) > 0 and patient_id in str(row) and TEST_RUN_ID in str(row):
            print(f"\n✅ Direct sheet verification: Found test note in row: {row[:3]}...")
            note_found = True
            break
    
    # Verify note exists (either from tool or direct read)
    if ("Bidirectional test note" in notes_info or TEST_RUN_ID in notes_info) or note_found:
        record_result(True, "Add Doctor Note → Read Notes", "Doctor note verified")
        print("\n✅ BIDIRECTIONAL TEST PASSED: Doctor note written and read successfully!")
    else:
        record_result(False, "Add Doctor Note → Read Notes", "Doctor note not found")
        print("\n❌ TEST FAILED: Doctor note not found in sheet")
        
except Exception as e:
    print(f"❌ Error: {e}")
    record_result(False, "Add Doctor Note → Read Notes", str(e))

# Print final summary
print_summary()

print("\n💡 TIP: Check your Google Sheets and Drive to see all test data created!")
if patient_id and patient_id != "TEST_PATIENT_FALLBACK":
    print(f"🔍 Search for: {TEST_RUN_ID} or {patient_id}")
else:
    print(f"🔍 Search for: {TEST_RUN_ID}")
