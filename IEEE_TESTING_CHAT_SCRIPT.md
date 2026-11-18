# IEEE Paper Testing - Complete Chat Script

## 📋 Quick Reference: What to Type at Each Stage

This is your **copy-paste reference** for the end-to-end test. Follow this sequence exactly for consistent screenshots.

---

## 🎬 STAGE 1-2: Registration & Email Verification

### Message 1: Registration Start
```
Hi, I want to register
```
**Screenshot 1**: Chat interface showing registration intent

---

### Message 2: Provide Patient Details
When AI asks for details, provide:
```
Name: John Michael Smith
Email: john.smith.research@gmail.com
Phone: +1-555-0123
Date of Birth: 1990-05-15
Gender: Male
Age: 34
```
**Screenshot 2**: AI extracting structured patient information

---

### Message 3: OTP Verification
Check your email, copy the 6-digit OTP, then type:
```
[YOUR-OTP-CODE]
```
Example: `847592`

**Screenshot 3**: Gmail inbox showing OTP email  
**Screenshot 4**: OTP verification success with patient ID

---

## 📁 STAGE 2: Document Upload

### Message 4: Upload Intent
When AI asks about documents, type:
```
I have 3 documents to upload
```
**Screenshot 5**: Document upload request

---

### Actions (Not Chat):
1. Upload 2-3 sample PDF files via the interface
2. Open Google Drive → Navigate to `AI_Healthcare_Patients/REG2025XXXXX/`

**Screenshot 6**: Google Drive folder structure with subfolders  
**Screenshot 7**: Chat showing upload confirmation with Drive URLs

---

## 🩺 STAGE 3: Medical History Collection

### Message 5: Past Medical Conditions
When AI asks: *"Do you have any past medical conditions or chronic diseases?"*

Type:
```
No, I don't have any past medical conditions, but my father was diagnosed with diabetes at age 45, so I'm concerned about family history.
```
**Screenshot 8**: Past medical conditions question

---

### Message 6: Allergies
When AI asks: *"Do you have any known allergies?"*

Type:
```
No known allergies to medications or food.
```
**Screenshot 9**: Allergy information collection

---

### Message 7: Current Medications
When AI asks: *"Are you currently taking any medications?"*

Type:
```
No, I'm not currently taking any medications.
```
**Screenshot 10**: Current medications inquiry

---

### Message 8: Chief Complaint
When AI asks: *"What brings you to the hospital today? What are your main concerns or symptoms?"*

Type:
```
I've been experiencing frequent urination, excessive thirst, and fatigue for the past 2 months. I'm also feeling numbness in my feet sometimes. My diet has been high in carbs and I haven't been exercising regularly. Given my family history of diabetes, I'm worried this might be diabetes.
```
**Screenshot 11**: Chief complaint with detailed symptoms

---

### Actions (Not Chat):
1. Wait for AI to create workflow document
2. Open Google Docs link provided in chat
3. View Sections 1-3 populated

**Screenshot 12**: Workflow document with patient info and medical history  
**Screenshot 13**: Section 3 showing ChromaDB analysis and recommended tests

---

## 🔬 STAGE 4-5: Test Approval & Lab Scheduling

### Message 9: Test Approval
When AI asks to approve tests, type:
```
Yes, approve all tests
```
**Screenshot 14**: Test confirmation dialog

---

### Message 10: Appointment Scheduling
When AI asks for appointment time, type:
```
Tomorrow at 9 AM
```
**Screenshot 15**: Appointment scheduling with NLP parsing

---

### Actions (Not Chat):
1. Open Google Calendar: https://calendar.google.com
2. Navigate to December 5, 2025
3. Open the lab appointment event

**Screenshot 16**: Google Calendar event with patient details and tests

---

### Actions (Open Lab Queue Sheet):
1. Get Lab Queue Sheet URL from system logs or chat
2. Open sheet and view the new patient row

**Screenshot 17**: Lab Queue Google Sheet showing PENDING status

---

## 🧪 STAGE 6: Lab Results

### Actions (Lab Technician Role):
1. Open Lab Queue Sheet
2. Find the patient row
3. Update:
   - **Status**: PENDING → COMPLETED
   - **Lab Results**: `Fasting Glucose: 126 mg/dL (Elevated), HbA1c: 6.8% (Prediabetic range), Lipid Panel: Normal`
   - **Date Completed**: 2025-12-05

**Screenshot 18**: Lab technician updating results in sheet

---

### Message 11: Check Lab Results
Type:
```
check my lab results
```
**Screenshot 19**: Patient checking results - AI retrieves from sheet

---

### Actions (Not Chat):
1. Open workflow document
2. Scroll to Section 5: Lab Results

**Screenshot 20**: Section 5 showing lab results auto-updated from sheet

---

## 👨‍⚕️ STAGE 7: Doctor Consultation

### Actions (Doctor Role):
1. Open workflow document
2. Scroll to Section 6: POST-LAB DOCTOR CONSULTATION
3. Screenshot the **EMPTY template** first

**Screenshot 21**: Doctor consultation template (before filling)

---

### Actions (Doctor Fills Section 6):
Edit Section 6 in Google Docs:

```
👨‍⚕️ DIAGNOSIS:
Type 2 Diabetes Mellitus - Early stage, currently in prediabetic range based on HbA1c 6.8%. 
Immediate lifestyle modification required along with medication.

✅ DECISION:
☒ NO ADMISSION - Outpatient treatment
☐ HOSPITAL ADMISSION REQUIRED

REASON: Patient's condition is manageable with oral medication and lifestyle changes. 
No immediate complications requiring hospitalization.
```

**Screenshot 22**: Doctor's diagnosis filled in (real content)

---

### Message 12: Check Consultation Status
Type:
```
check my consultation status
```
**Screenshot 23**: AI detects real diagnosis, advances workflow

---

## 💊 STAGE 11: Prescription & Follow-up

### Actions (Doctor Role):
1. Workflow document → Section 7: PRESCRIPTION & FOLLOW-UP
2. Screenshot the **EMPTY template** first

**Screenshot 24**: Prescription template (before filling)

---

### Actions (Doctor Fills Section 7):
Edit Section 7 in Google Docs:

```
💊 MEDICATIONS PRESCRIBED:
1. Metformin 500mg - Take twice daily with meals
2. Lifestyle modifications: Low-carb diet, 30min daily exercise

📅 FOLLOW-UP APPOINTMENT
• Date: 2025-12-19 (2 weeks from today)
• Purpose: Recheck fasting glucose and HbA1c
• Instructions: Continue medication, maintain food diary
```

**Screenshot 25**: Doctor's prescription filled in

---

### Actions (Not Chat):
1. Open Google Calendar
2. Navigate to December 19, 2025
3. View follow-up appointment event

**Screenshot 26**: Follow-up appointment in Google Calendar

---

## ✅ STAGE 12: Workflow Completion

### Message 13: Check Status
Type:
```
What's my status?
```
**Screenshot 27**: Completion notification with journey summary

---

### Actions (Not Chat):
1. Open workflow document
2. Scroll through all 7 sections

**Screenshot 28**: Complete workflow document (all sections filled)

---

## 🔄 BONUS: State Persistence

### Actions:
1. Logout from chat
2. Close browser
3. Wait 2-3 minutes
4. Login again with same email

### Message 14: Login Again
```
[Login with john.smith.research@gmail.com]
```

**Screenshot 29**: State restored - workflow resumes at last stage

---

## 🗄️ BONUS: Database Views

### Actions (PostgreSQL):
1. Open pgAdmin or database viewer
2. Show tables: `patients`, `workflow_states`, `otp_verifications`

**Screenshot 30**: PostgreSQL database schema

---

### Actions (Redis):
1. Open Redis CLI or GUI (e.g., RedisInsight)
2. Search for keys: `workflow:REG*`
3. Show cached workflow state

**Screenshot 31**: Redis cache with workflow state and TTL

---

### Actions (Backend Logs):
1. View terminal running `python main.py`
2. Show tool execution logs during workflow

**Screenshot 32**: Tool execution logging in backend console

---

## 📊 Total Screenshots: 32

### Screenshot Checklist:
- [ ] 1. Registration start
- [ ] 2. Patient details collection
- [ ] 3. Email OTP received
- [ ] 4. OTP verification success
- [ ] 5. Document upload request
- [ ] 6. Google Drive folder structure
- [ ] 7. Upload confirmation
- [ ] 8. Past medical conditions
- [ ] 9. Allergies
- [ ] 10. Current medications
- [ ] 11. Chief complaint (detailed symptoms)
- [ ] 12. Workflow document created
- [ ] 13. ChromaDB analysis results
- [ ] 14. Test confirmation
- [ ] 15. Appointment scheduling
- [ ] 16. Google Calendar event
- [ ] 17. Lab Queue sheet (pending)
- [ ] 18. Lab results entered (technician)
- [ ] 19. Patient checks results
- [ ] 20. Lab results in workflow doc
- [ ] 21. Doctor consultation template (empty)
- [ ] 22. Doctor diagnosis (filled)
- [ ] 23. Template validation working
- [ ] 24. Prescription template (empty)
- [ ] 25. Prescription filled
- [ ] 26. Follow-up calendar event
- [ ] 27. Completion notification
- [ ] 28. Complete workflow document
- [ ] 29. State persistence (logout/login)
- [ ] 30. PostgreSQL database
- [ ] 31. Redis cache
- [ ] 32. Backend tool logs

---

## ⏱️ Estimated Time: 90 minutes

**Tips:**
- Keep this file open in a second monitor or split screen
- Copy-paste messages exactly as shown
- Take screenshots immediately after each action
- Use consistent browser window size
- Save screenshots with numbered filenames

**Good luck with your IEEE paper! 🚀**
