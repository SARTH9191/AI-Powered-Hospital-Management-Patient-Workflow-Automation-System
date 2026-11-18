# Complete Tool Testing Guide

## Test Files Created

### 1. `test_individual_tools.py` ✅ ALREADY PASSED
Basic tests for the 4 most critical tools:
- CreateMedicalDocumentTool
- ShareMedicalDocumentTool  
- SendNotificationTool
- AddLabResultTool

**Status:** ✅ All 4 tests passed!

---

### 2. `test_all_workflow_tools.py` 🆕 NEW - COMPREHENSIVE
Tests **14 different tools** covering all workflow stages:

#### Stage 1 - Registration
- ✅ RegisterPatientTool
- ✅ CreatePatientFolderTool
- ✅ AddPatientRecordTool

#### Stage 2 - Documents & Email
- ✅ SendGmailTool

#### Stage 3 - Medical Records
- ✅ AddAllergyTool
- ✅ AddChronicConditionTool

#### Stage 5 - Appointments
- ✅ CheckDoctorAvailabilityTool
- ✅ CreateAppointmentTool (Calendar)

#### Stage 7 - Billing & Admission
- ✅ CreateBillingRecordTool
- ✅ GenerateInvoiceTool

#### Stage 8 - Treatment Monitoring
- ✅ UpdatePatientStatusTool
- ✅ AddStaffUpdateTool

#### Stage 3/7/9 - Document Creation
- ✅ CreateMedicalDocumentTool

#### Notifications
- ✅ SendNotificationTool (Custom)

**Total:** 14 tools tested end-to-end

---

### 3. `test_billing_pharmacy_tools.py` 🆕 NEW - BILLING FOCUS
Deep dive into billing and pharmacy functionality:

#### Billing Tests
- ✅ Multiple service billing (4 different services)
- ✅ Comprehensive invoice generation
- ✅ Complex scenarios:
  - Full insurance (90% coverage)
  - No insurance (cash patient)
  - Partial insurance (40% coverage)

#### Pharmacy Tests  
- ✅ Drug interaction checking
- ✅ Medication information lookup
- ✅ Prescription management

**Total:** 6 comprehensive test scenarios

---

## Running the Tests

### Quick Test (Already Done) ✅
```powershell
python test_individual_tools.py
```
**Result:** All 4 basic tools working!

### Comprehensive Test (Run This Next)
```powershell
python test_all_workflow_tools.py
```
**Expected:** Tests 14 different tools across all stages
**Time:** ~1-2 minutes
**Creates:** Test patient, folders, documents, emails, appointments, billing records

### Billing & Pharmacy Deep Test
```powershell
python test_billing_pharmacy_tools.py
```
**Expected:** Tests billing scenarios and pharmacy tools
**Time:** ~30 seconds
**Creates:** Multiple billing records, prescriptions, drug interaction checks

---

## What Gets Created During Tests

### test_all_workflow_tools.py creates:
1. **Patient Record** - Test patient in database
2. **Google Drive Folder** - Patient folder
3. **Google Sheets Entries:**
   - Patient tracking record
   - Lab result entry
   - Billing record
   - Staff update entry
   - Patient status update
4. **Google Docs Document** - Medical consultation notes
5. **Google Calendar Event** - Appointment (7 days from now)
6. **Email** - Test email to your address
7. **Medical Records:**
   - Test allergy entry
   - Test chronic condition entry

### test_billing_pharmacy_tools.py creates:
1. **4 Billing Records:**
   - Consultation with insurance
   - Lab tests with insurance
   - Hospital stay (no insurance)
   - Medications with insurance
2. **1 Invoice** - Comprehensive invoice
3. **Drug Interaction Checks** - For 3 medications
4. **Medication Info Lookups** - For 3 medications
5. **1 Prescription** - Test prescription record
6. **3 Additional Billing Records** - Complex scenarios

---

## Test Artifacts Created

After running tests, you'll have these files:
- `test_patient_id.txt` - Patient ID for test patient
- `test_folder_id.txt` - Google Drive folder ID
- `test_doc_id.txt` - Google Docs document ID

These help connect test data across different tools.

---

## Expected Results

### All Tests Passing Should Show:
```
✅ Tests Passed: 14/14
📊 Success Rate: 100%
```

### What You'll See in Your Google Account:

#### Google Drive
- Test patient folder
- Test document (from test_individual_tools.py)
- Medical consultation notes (from test_all_workflow_tools.py)

#### Google Sheets
- Patient tracking sheet: 1 test patient
- Lab results sheet: 1 test result
- Billing sheet: 8+ billing records
- Patient monitoring sheet: Status update
- Staff updates sheet: 1 staff update

#### Google Calendar
- 1 test appointment (7 days from now)

#### Gmail
- 1 test email in sent folder
- Possibly notifications to patient email (if patient exists in DB)

---

## Cleanup After Testing

### Option 1: Manual Cleanup
1. **Google Drive:** Delete test documents
2. **Google Sheets:** Filter by "TEST-" and delete rows
3. **Google Calendar:** Delete test appointments
4. **Gmail:** Delete test email from sent

### Option 2: Keep Test Data
- Test data is clearly marked with "TEST-" prefix
- Can be used for debugging/development
- Easy to identify and filter

---

## Troubleshooting

### If tests fail:

1. **Check token scopes first:**
   ```powershell
   python check_token_scopes.py
   ```

2. **Verify .env file has correct IDs:**
   - PATIENT_TRACKING_SHEET_ID
   - LAB_RESULTS_MONITORING_SHEET_ID
   - BILLING_SHEET_ID
   - DOCTOR_EMAIL
   - TEST_EMAIL

3. **Check API quotas:**
   - Go to Google Cloud Console
   - Check if you've hit daily limits

4. **Re-authenticate if needed:**
   ```powershell
   # Delete token
   rm docs_token.pickle
   
   # Regenerate
   python generate_docs_token.py
   ```

---

## Test Execution Order

### Recommended order:
```powershell
# 1. First time - verify tokens
python check_token_scopes.py

# 2. Basic test (already done ✅)
python test_individual_tools.py

# 3. Comprehensive workflow test
python test_all_workflow_tools.py

# 4. Billing & pharmacy deep dive
python test_billing_pharmacy_tools.py
```

### Quick re-test after fixes:
```powershell
# Just run comprehensive test
python test_all_workflow_tools.py
```

---

## Success Indicators

### ✅ Everything Working:
- All test files run without errors
- Success rates are 100%
- Can see test data in Google Drive/Sheets/Calendar
- Received test email
- No authentication errors
- No API quota errors

### 🎉 Ready for Production:
Once all tests pass, your workflow is ready to handle:
- Patient registration
- Document management
- Medical records
- Appointments
- Billing & invoicing
- Treatment monitoring
- Notifications
- Pharmacy management

---

## Next Steps After All Tests Pass

1. ✅ Clean up test data (optional)
2. ✅ Run full workflow integration test
3. ✅ Test with real user flow (start to finish)
4. ✅ Deploy to production
5. ✅ Monitor first few real patients closely

---

**Status:** Ready to test!
**Run:** `python test_all_workflow_tools.py`
