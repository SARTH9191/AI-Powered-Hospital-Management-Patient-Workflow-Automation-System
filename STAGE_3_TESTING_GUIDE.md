# 🧪 Stage 3 Testing Guide - Medical History Collection

## 🎯 Quick Test from Stage 3

### Prerequisites:
1. ✅ Backend running: `python main.py`
2. ✅ Frontend running: `npm run dev` (in frontend folder)
3. ✅ Login with: `iamsamarth786@gmail.com` or any Gmail

---

## 📋 STAGE 3: MEDICAL HISTORY COLLECTION

### Test Scenario 1: Diabetes Patient with Stomach Issues

**Step 1: Start Medical History**
```
AI: "Let's start with your medical history. Tell me about any existing medical conditions..."
```

**Step 2: Past Medical Conditions**
```
Type: "I have diabetes and high blood pressure"

AI will parse and ask for more details...
```

**Step 3: Current Symptoms**
```
Type: "I have severe stomach pain and vomiting since yesterday. The pain is getting worse."

AI will extract:
- Chief Complaint: Stomach pain and vomiting
- Severity: Severe
- Duration: Since yesterday
```

**Step 4: Allergies**
```
Type: "I'm allergic to penicillin"

AI will record allergy and ask about medications...
```

**Step 5: Current Medications**
```
Type: "I'm taking metformin 500mg twice daily for diabetes and lisinopril 10mg once daily for blood pressure"

AI will extract:
- Metformin 500mg (2x daily) - Diabetes
- Lisinopril 10mg (1x daily) - Hypertension
```

**Step 6: Confirm**
```
Type: "yes" or "confirm" to finalize

AI will:
✅ Create unified workflow document
✅ Update Section 1 with medical history
✅ Query ChromaDB for relevant lab test recommendations
✅ Move to Stage 4 (Lab Test Determination)
```

---

### Test Scenario 2: Chest Pain (Cardiac Concern)

**Complete Medical History:**
```
Patient Input Sequence:

1. "I have no past medical conditions"
2. "I'm experiencing sharp chest pain radiating to my left arm and jaw. Started 2 hours ago. Also feeling shortness of breath and nausea."
3. "No allergies"
4. "I take aspirin 81mg daily for general health"
5. "yes"  (to confirm)
```

**Expected ChromaDB Test Recommendations:**
- Troponin I
- CK-MB
- ECG
- Complete Blood Count (CBC)
- Electrolyte Panel
- Lipid Profile

**Expected Stage 4 Outcome:**
- AI will mark some tests as URGENT (Troponin, CK-MB, ECG)
- Doctor approval will be requested immediately
- Tests will appear in "Doctor Notes" Google Sheet

---

### Test Scenario 3: Routine Checkup (No Major Issues)

**Complete Medical History:**
```
Patient Input Sequence:

1. "No chronic conditions"
2. "I'm here for a routine health checkup. Feeling generally fine but want to make sure everything is okay. Maybe a bit more tired than usual."
3. "No known allergies"
4. "Not taking any medications regularly. Sometimes take vitamin D supplements."
5. "yes"
```

**Expected ChromaDB Test Recommendations:**
- Complete Blood Count (CBC)
- Basic Metabolic Panel (BMP)
- Lipid Profile
- Thyroid Function Tests (TSH, T3, T4)
- Vitamin D levels
- HbA1c (diabetes screening)

**Expected Stage 4 Outcome:**
- All tests marked as ROUTINE priority
- Doctor can approve all at once
- Scheduling allows flexible timing

---

## 🔍 What to Verify

### ✅ Stage 3 Checklist:

1. **AI Parsing Quality**
   - [ ] Correctly extracts medical conditions
   - [ ] Identifies symptoms and severity
   - [ ] Captures allergies properly
   - [ ] Parses medication names, dosages, frequencies

2. **Document Creation**
   - [ ] Unified workflow document created in Google Drive
   - [ ] Section 1 populated with medical history
   - [ ] Conditions shown as readable text (not generic summaries)
   - [ ] Symptoms included in parentheses

3. **ChromaDB Integration**
   - [ ] Terminal shows: `🧠 ChromaDB test recommendations: [results]`
   - [ ] Recommendations are relevant to symptoms
   - [ ] Not just generic tests (CBC, BMP, Lipid)

4. **Google Sheets Updates**
   - [ ] "Patient Status" sheet updated with patient info
   - [ ] "Doctor Notes" sheet shows medical history summary

5. **Stage Transition**
   - [ ] Moves to Stage 4 (Lab Test Determination)
   - [ ] Doctor approval request appears in "Doctor Notes" sheet

---

## 🚀 Expected Stage 4-7 Flow After Stage 3

### Stage 4: Lab Test Determination & Doctor Approval
```
1. AI determines required tests (using ChromaDB + symptoms)
2. Creates Section 2 in document with AI analysis
3. Adds tests to "Doctor Notes" Google Sheet
4. Waits for doctor approval/modification/rejection

Doctor Options:
- APPROVE: Continue to Stage 5 (Lab Scheduling)
- MODIFY: Add/remove specific tests
- REJECT: Skip to Stage 7 (Doctor Consultation directly) ✅ NEW FIX
- CONSULT: Skip to Stage 7 (See patient first) ✅ NEW FIX
```

### Stage 5: Lab Appointment Scheduling
```
1. AI asks: "When would you like to schedule your lab tests?"
2. Patient provides date/time
3. AI creates Google Calendar event
4. Adds row to Lab Queue Sheet with approved tests
5. Moves to Stage 6
```

### Stage 6: Lab Results Analysis
```
1. AI asks patient to type "check" when labs are done
2. Lab tech fills "Lab Results" column in Lab Queue Sheet
3. Patient types "check"
4. AI reads results from sheet
5. Syncs to Document Section 5
6. Patient types "yes" to proceed
7. Moves to Stage 7
```

### Stage 7: Doctor Consultation (Post-Lab)
```
1. AI asks: "When would you like to schedule doctor consultation?"
2. Patient provides date/time
3. AI creates Google Calendar event
4. Updates Section 6 with appointment details and template
5. After appointment, doctor fills Section 6 with:
   - Diagnosis
   - Treatment Decision (Admission YES/NO)
   - Treatment Plan
   - Prescription Requirements
   - Follow-up Schedule
6. Patient types "check"
7. AI reads Section 6 and proceeds based on admission decision
```

---

## 🛠️ Troubleshooting

### Issue: "Patient provided non-specific response" in document
**Fix**: ✅ Already fixed! AI now extracts actual conditions from parsed dictionaries.

### Issue: AI recommends same generic tests always
**Fix**: ✅ Already fixed! ChromaDB now receives actual conditions + symptoms.

### Issue: Test Names empty in Lab Queue Sheet
**Fix**: ✅ Already fixed! Uses `recommended_tests` from correct scope.

### Issue: Stage 6 stuck in loop when typing "yes"
**Fix**: ✅ Already fixed! Now checks for "yes" confirmation and transitions to Stage 7.

### Issue: Stage 7 doesn't schedule appointment
**Fix**: ✅ Already fixed! Now schedules Google Calendar appointment before waiting for doctor notes.

---

## 📊 Success Criteria

### Complete Stage 3-7 Test is Successful When:

1. ✅ Medical history accurately captured and displayed
2. ✅ ChromaDB provides relevant test recommendations
3. ✅ Doctor can approve/modify/reject tests in Google Sheets
4. ✅ Lab appointment scheduled in Google Calendar
5. ✅ Lab Queue Sheet populated with test names
6. ✅ Lab results read from Lab Queue Sheet
7. ✅ Doctor consultation appointment scheduled
8. ✅ Doctor fills Section 6 with treatment plan
9. ✅ Workflow proceeds to Stage 8+ or Stage 10+ based on admission decision

---

## 📝 Sample Test Data

### Patient 1: Diabetes with Acute Issue
```
Name: Samarth Pawar
Email: iamsamarth786@gmail.com
Medical History: "Diabetes mellitus, hypertension"
Symptoms: "Severe stomach pain, vomiting, fever"
Allergies: "Penicillin"
Medications: "Metformin 500mg twice daily, Lisinopril 10mg once daily"
```

### Patient 2: Chest Pain Emergency
```
Name: John Emergency
Email: test@gmail.com
Medical History: "None"
Symptoms: "Severe chest pain radiating to left arm, shortness of breath, nausea, started 2 hours ago"
Allergies: "None"
Medications: "Aspirin 81mg daily"
```

### Patient 3: Routine Checkup
```
Name: Jane Wellness
Email: janewellness@gmail.com
Medical History: "No chronic conditions"
Symptoms: "Routine checkup, feeling tired lately"
Allergies: "None"
Medications: "Vitamin D supplements occasionally"
```

---

## 🎯 Quick Test Commands

```bash
# Terminal 1: Backend
cd "D:\ai agent by myself\ai agent"
python main.py

# Terminal 2: Frontend
cd "D:\ai agent by myself\ai agent\frontend"
npm run dev

# Open Browser: http://localhost:3000
# Login: iamsamarth786@gmail.com (or any Gmail)
# Start: Type medical history as shown above
```

---

## ✅ NEW FIXES IMPLEMENTED

1. ✅ **"No tests required" flow**: If doctor chooses REJECT or CONSULT in Stage 4, workflow jumps directly to Stage 7 (Doctor Consultation)
2. ✅ **Stage 7 appointment scheduling**: Now schedules Google Calendar event before waiting for doctor notes
3. ✅ **Section 6 template**: Clear checkboxes for doctor to fill diagnosis, treatment decision, prescriptions, follow-up
4. ✅ **All `**` markdown removed**: Stage 5+ messages cleaned (AI already strips `**` from LLM responses)

---

**Happy Testing! 🚀**
