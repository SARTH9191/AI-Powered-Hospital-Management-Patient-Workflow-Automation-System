# Manual Test Cases - Drive Folder Structure Implementation

## Test Environment Setup

1. Start Backend: `python main.py`
2. Start Frontend: `cd frontend && npm run dev`
3. Open browser: `http://localhost:3000`

---

## Test Case 1: Stage 1 - Registration & Folder Creation

**Goal**: Verify 5 folders are created automatically

### Steps:
1. Open application in browser
2. Click "Register" or go to registration page
3. Fill in registration form:
   - Full Name: Test Patient
   - Email: testpatient@example.com
   - Phone: 9876543210
   - Date of Birth: 1990-01-01
   - Gender: Male
   - Address: Test Address
   - City: Mumbai
   - State: Maharashtra
   - Pincode: 400001
4. Submit registration

### Expected Result:
- ✅ Registration successful message
- ✅ Patient ID generated (e.g., PAT20250115...)
- ✅ Check Google Drive - new folder created: `Patient_Test_Patient_PAT...`
- ✅ Inside folder, verify 5 subfolders exist:
  - 1_Medical_History
  - 2_Essential_Documents
  - 3_Lab_Reports
  - 4_Prescriptions
  - 5_Consultation_Notes

### If Failed:
- Check backend logs for Drive API errors
- Verify `drive_token.pickle` exists
- Check `.env` has correct credentials

---

## Test Case 2: Stage 2 - Essential Documents Upload (ID Proof Mandatory)

**Goal**: Verify patient is prompted for essential documents and cannot proceed without ID proof

### Steps:
1. After registration, patient should be at Stage 2
2. Read the AI message - should show:
   - Link to main folder
   - Link to **2_Essential_Documents** folder
   - List of organized folders
   - Explanation of what to upload

### Expected Message Contains:
- ✅ "📁 Your Main Upload Folder: [Click here]"
- ✅ "📄 Essential Documents Folder (Recommended): [link]"
- ✅ Text mentions: Aadhaar, PAN, Insurance, ID Proof
- ✅ "💡 Organized Folders Created for You:"
- ✅ Shows all 5 folders

### Test 2A: Try to skip without documents
1. Type: "skip"

**Expected Result:**
- ❌ Should be rejected
- ✅ Message: "🚫 Document Upload is Mandatory"
- ✅ Explains why documents are required

### Test 2B: Upload documents WITHOUT ID proof
1. Open the patient's Google Drive folder
2. Upload a random image to `3_Lab_Reports` folder (wrong folder)
3. Return to chat
4. Type: "done"

**Expected Result:**
- ❌ Should be rejected
- ✅ Message: "⚠️ Missing Mandatory Documents"
- ✅ Message shows documents found but no ID proof
- ✅ Cannot proceed to Stage 3

### Test 2C: Upload ID proof correctly
1. Open the patient's Google Drive folder
2. Go to `2_Essential_Documents` folder
3. Upload ANY document (image/PDF) - this simulates Aadhaar/PAN
4. Return to chat
5. Type: "done"

**Expected Result:**
- ✅ Message: "✅ Documents Successfully Detected!"
- ✅ Shows: "ID Proof Verified: 1 ID document(s) found"
- ✅ Asks: "Proceed with document verification? (yes/no)"

### Test 2D: Confirm and proceed
1. Type: "yes"

**Expected Result:**
- ✅ Advances to Stage 3
- ✅ Message: "Next Step: Stage 3 - Medical History"

---

## Test Case 3: Stage 3 - Medical History (Optional Upload)

**Goal**: Verify medical history folder link is shown

### Steps:
1. After Stage 2 confirmation, should be at Stage 3
2. Read the AI message

### Expected Message Contains:
- ✅ "📁 Optional: If you have previous medical documents..."
- ✅ Link to `1_Medical_History` folder
- ✅ Text: "Previous test results, discharge summaries, medical reports"

### Test 3A: Answer medical history questions
1. Answer: "No past medical conditions"
2. Answer: "No allergies"
3. Answer: "No current medications"
4. Answer: "I have fever and headache"

**Expected Result:**
- ✅ AI asks each question sequentially
- ✅ After all answers, shows comprehensive clinical summary
- ✅ Asks: "Proceed? (yes/no)"

### Test 3B: Confirm
1. Type: "yes"

**Expected Result:**
- ✅ Creates unified workflow document
- ✅ Advances to Stage 4

---

## Test Case 4: Stage 4 - Doctor Approval (Skip for now)

**Goal**: Just verify stage exists

### Steps:
1. Doctor needs to approve tests in Google Doc Section 3
2. For testing, type: "check" multiple times or wait

**Expected Result:**
- ⏳ Shows waiting message
- ✅ Provides document link

**Note**: Manual testing of doctor approval requires opening the Google Doc and filling Section 3. Skip this for automation.

---

## Test Case 5: Stage 5 - Lab Appointment & Lab Reports Folder

**Goal**: Verify lab reports folder link is shown in appointment confirmation

### Steps:
1. After doctor approval (or skip Stage 4), should be at Stage 5
2. AI suggests lab appointment date/time
3. Type: "yes" or confirm the appointment

### Expected Message Contains:
- ✅ "✅ LAB APPOINTMENT CONFIRMED!"
- ✅ Shows appointment details
- ✅ "📂 LAB REPORTS FOLDER: [Click here]"
- ✅ Text: "Lab technicians will upload your test results here"

**Expected Result:**
- ✅ Appointment created in Google Calendar
- ✅ Row added to Lab Queue Sheet
- ✅ Asks: "Ready to proceed? (yes/no)"

### Confirm:
1. Type: "yes"

**Expected Result:**
- ✅ Advances to Stage 6

---

## Test Case 6: Stage 6 - Lab Results (Skip for now)

**Goal**: Verify stage waits for lab results

### Steps:
1. Should be at Stage 6
2. Type: "check"

**Expected Result:**
- ⏳ Message: "Waiting for Lab Results"
- ✅ Provides document link (Section 5)

**Note**: Requires lab tech to fill Lab Queue Sheet or Doc Section 5. Skip for automation.

---

## Test Case 7: Stage 7-10 - Doctor Consultation (Skip for now)

**Note**: These stages require doctor interaction. Skip for automation.

---

## Test Case 8: Stage 11 - Prescription PDF Generation (MOST IMPORTANT)

**Goal**: Verify AI auto-generates prescription PDF and uploads to 4_Prescriptions folder

### Prerequisites:
1. Must reach Stage 11 (or manually set patient to Stage 11 for testing)
2. Doctor must fill Google Doc Section 7 with prescription

### Manual Setup for Testing:
1. Find the patient's workflow document in Google Drive
2. Open the document
3. Scroll to "Section 7: PRESCRIPTION & FOLLOW-UP"
4. Add sample prescription text:
```
Medicine: Paracetamol 500mg
Dosage: 1 tablet
Frequency: 3 times daily
Duration: 5 days
Instructions: Take after meals

Medicine: Cough Syrup
Dosage: 10ml
Frequency: Twice daily
Duration: 7 days
Instructions: Take at bedtime
```
5. Save the document

### Test Steps:
1. In chat, type: "check" (to trigger prescription reading)

### Expected Result:
- ✅ AI reads prescription from Section 7
- ✅ Message: "✅ PRESCRIPTION AND FOLLOW-UP PLAN"
- ✅ Shows list of medications with details
- ✅ **CRITICAL**: Shows "📄 PRESCRIPTION PDF (Auto-generated)"
- ✅ **CRITICAL**: Provides download link to PDF
- ✅ Text: "Location: 4_Prescriptions folder in your Google Drive"

### Verify PDF Generation:
1. Click the download link in chat
2. PDF should open/download
3. Verify PDF contains:
   - ✅ Hospital header
   - ✅ Patient name and ID
   - ✅ Date
   - ✅ Medication list with dosages
   - ✅ Instructions
   - ✅ Professional formatting

### Verify PDF in Drive:
1. Open patient's Google Drive folder
2. Open `4_Prescriptions` folder
3. Verify PDF file exists: `Prescription_PAT..._.pdf`

**If Failed:**
- Check backend logs for "PDF generation" errors
- Verify reportlab is installed: `pip list | grep reportlab`
- Check if Section 7 has content
- Verify `4_Prescriptions` folder ID is in state

---

## Test Case 9: Stage 12 - Completion

**Goal**: Verify workflow completes successfully

### Steps:
1. From Stage 11, type: "complete"

**Expected Result:**
- ✅ Completion message
- ✅ Summary of journey
- ✅ All documents accessible in Google Drive

---

## Quick Verification Checklist

After completing all tests, verify in Google Drive:

**Patient Folder Structure:**
```
Patient_Test_Patient_PAT.../
├─ 1_Medical_History/              [Empty or has optional docs]
├─ 2_Essential_Documents/          [✅ Has ID proof document]
├─ 3_Lab_Reports/                  [Empty in manual test]
├─ 4_Prescriptions/                [✅ Has auto-generated PDF]
└─ 5_Consultation_Notes/           [Empty in manual test]
```

---

## Common Issues & Solutions

### Issue 1: Folders not created
- **Solution**: Check Drive API authentication, verify `drive_token.pickle`

### Issue 2: "Cannot proceed without ID proof" even after upload
- **Solution**: Ensure document is in `2_Essential_Documents` folder, not main folder

### Issue 3: Prescription PDF not generated
- **Solution**: 
  - Verify Section 7 has prescription text
  - Check `reportlab` installed: `pip install reportlab==4.0.7`
  - Check backend logs for errors

### Issue 4: Folder links not showing in chat
- **Solution**: 
  - Check if `state['drive_subfolders']` is populated
  - Restart patient from Stage 1 (new registration)

### Issue 5: PDF link broken
- **Solution**: Check Google Drive permissions, verify file uploaded successfully

---

## Success Criteria

✅ **All tests pass if:**
1. 5 folders created on registration
2. Stage 2 shows Essential_Documents link and enforces ID proof
3. Stage 3 shows Medical_History link
4. Stage 5 shows Lab_Reports link
5. Stage 11 auto-generates PDF and shows download link
6. PDF exists in 4_Prescriptions folder with correct content

---

**End of Test Cases**
