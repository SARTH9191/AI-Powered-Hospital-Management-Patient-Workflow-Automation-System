# 🚀 QUICK TESTING GUIDE - Tomorrow's End-to-End Test

**Date:** November 14-15, 2025  
**Status:** Ready for Live Frontend Testing

---

## ⚡ Quick Start (30 seconds)

### 1. Start All Services
```bash
# Terminal 1: Start Backend
cd "d:\ai agent by myself\ai agent"
python main.py

# Terminal 2: Start Frontend
cd "d:\ai agent by myself\ai agent\frontend"
npm run dev

# Terminal 3: Check Redis (should already be running)
redis-cli ping
```

### 2. Open These URLs
- Frontend: http://localhost:3000
- Backend API Docs: http://localhost:8000/docs
- Test Document: https://docs.google.com/document/d/1kAgV4vOZkrrh2FZeKmQ2r8CDp9w2MG6KfZiKuSXw_pY/edit

### 3. Login Credentials
- **Email:** iamsamarth786@gmail.com
- **Phone:** 7447444532
- **Patient ID:** PAT20251113001842

---

## 📋 Testing Workflow (Step by Step)

### Stage 1: Login (2 minutes)
```
1. Go to http://localhost:3000/loginPage
2. Enter: iamsamarth786@gmail.com
3. Enter: 7447444532
4. Click "Login"
✅ Should recognize returning patient
```

### Stage 2: Skip Documents (30 seconds)
```
AI: "Do you want to upload documents?"
You: "skip"
✅ Should advance to Stage 3
```

### Stage 3: Medical History (5 minutes)
```
You: "I have fever, headache, and body pain for 3 days"
AI: "Any chronic conditions?"
You: "I have diabetes"
AI: "Current medications?"
You: "Taking Metformin 500mg"
AI: "Any allergies?"
You: "No allergies"
You: "That's all"

✅ Document should be created
✅ Document link should appear
```

### Stage 4: Doctor Approval (2 minutes - MANUAL)
```
1. Open document link
2. Scroll to SECTION 3: DOCTOR'S DECISION
3. Paste this:

✅ TESTS APPROVED

Recommended Tests:
1. Complete Blood Count (CBC)
2. Blood Glucose (Fasting)
3. Lipid Profile

4. Save document
5. Return to chat
You: "Has the doctor approved?"
✅ AI should confirm approval
```

### Stage 5: Lab Scheduling (3 minutes)
```
AI: "Let's schedule your lab tests!"
You: "Yes, please schedule automatically"

OR

You: "Tomorrow morning at 9 AM"

✅ Calendar event should be created
✅ Check Google Calendar for appointment
✅ Section 4 should be updated in document
```

### Stage 6: Lab Results (3 minutes - MANUAL)
```
1. Open document
2. Scroll to SECTION 5: LAB RESULTS
3. Paste this:

📊 LAB TEST RESULTS
Test Date: November 15, 2025

1. Complete Blood Count (CBC)
   Result: 14.5 g/dL
   Normal Range: 12.0-16.0 g/dL
   Status: ✅ NORMAL

2. Blood Glucose (Fasting)
   Result: 126 mg/dL
   Normal Range: 70-100 mg/dL
   Status: ⚠️ ABNORMAL (Elevated)

3. Lipid Profile
   Result: 195 mg/dL
   Normal Range: <200 mg/dL
   Status: ✅ NORMAL

Summary: 2 Normal | 1 Abnormal

4. Save document
5. Return to chat
You: "Are my lab results ready?"
✅ AI should display results with analysis
```

### Stage 7: Doctor Consultation (2 minutes - MANUAL)
```
1. Open document
2. Scroll to SECTION 6: POST-LAB CONSULTATION
3. Paste this:

👨‍⚕️ DOCTOR'S CONSULTATION
Date: November 16, 2025

DIAGNOSIS:
Pre-diabetic condition detected. Blood glucose elevated.

TREATMENT PLAN:
1. Start Metformin 500mg
2. Dietary modifications required
3. Follow-up in 3 months

NEXT STEPS:
- Review prescription in next section
- Schedule follow-up appointment

4. Save document
5. Return to chat
You: "What did the doctor say?"
✅ AI should show consultation summary
```

### Stage 11: Prescription (2 minutes - MANUAL)
```
1. Open document
2. Scroll to SECTION 7: PRESCRIPTION & FOLLOW-UP
3. Paste this:

💊 PRESCRIPTION

MEDICATIONS:
1. Metformin 500mg
   - Dosage: 1 tablet twice daily
   - Timing: With breakfast and dinner
   - Duration: 3 months

DIETARY INSTRUCTIONS:
• Limit sugar intake
• Increase fiber in diet
• Avoid processed foods

FOLLOW-UP APPOINTMENT:
📅 Schedule after 3 months
📅 Suggested Date: February 16, 2026

SAFETY MEASURES:
⚠️ Monitor blood sugar weekly
⚠️ Report any side effects immediately

4. Save document
5. Return to chat
You: "What is my prescription?"
✅ AI should show prescription
✅ Follow-up appointment should be scheduled
✅ Check Google Calendar for follow-up
```

### Stage 12: Completion (1 minute)
```
You: "Thank you, is my treatment plan complete?"
✅ AI should show journey summary
✅ Section 8 should be updated in document
```

---

## 🎯 Critical Test Points

### Must Verify ✅

1. **Document Creation**
   - [ ] Document created successfully
   - [ ] Document shared with doctor
   - [ ] All 8 sections present
   - [ ] Document link works

2. **Calendar Integration**
   - [ ] Lab appointment created in Google Calendar
   - [ ] Event ID returned and stored
   - [ ] Follow-up appointment created
   - [ ] Email invitations sent

3. **Section Reading**
   - [ ] Section 3 (Doctor Approval) - AI reads correctly
   - [ ] Section 5 (Lab Results) - AI parses 4 tests
   - [ ] Section 6 (Consultation) - AI extracts diagnosis
   - [ ] Section 7 (Prescription) - AI parses medications

4. **Stage Progression**
   - [ ] Stages advance automatically
   - [ ] No infinite loops
   - [ ] State saved correctly
   - [ ] Can resume after refresh

5. **Frontend Display**
   - [ ] Messages display correctly
   - [ ] Document links clickable
   - [ ] Stage indicator shows current stage
   - [ ] Timestamps accurate

---

## 🔧 If Something Breaks

### Quick Fixes

**Problem:** Patient stuck in old stage
```bash
# Reset patient state
python reset_patient_state.py
```

**Problem:** Document not found
```bash
# Check document ID in state
# Look in Redis or check logs
```

**Problem:** Calendar event fails
```bash
# Check calendar_token.pickle exists
# Re-authenticate if needed
python -c "from tools.google_calendar_tool import CreateAppointmentTool; CreateAppointmentTool()"
```

**Problem:** AI not reading sections
```bash
# Check docs_token.pickle
# Verify document permissions
# Try reading section manually:
python -c "from tools.unified_workflow_doc_tool import read_lab_results; print(read_lab_results('DOC_ID'))"
```

**Problem:** Frontend not connecting to backend
```bash
# Check backend is running on port 8000
curl http://localhost:8000/health

# Check frontend environment
cat frontend/.env.local
# Should have: NEXT_PUBLIC_API_URL=http://localhost:8000
```

---

## 📊 Test Results Template

### Copy this to record results:

```
STAGE 1: LOGIN
Time: __ minutes
Status: ✅ / ❌
Issues: ___________________
Notes: ____________________

STAGE 2: DOCUMENTS
Time: __ seconds
Status: ✅ / ❌
Issues: ___________________
Notes: ____________________

STAGE 3: MEDICAL HISTORY
Time: __ minutes
Status: ✅ / ❌
Issues: ___________________
Notes: ____________________

STAGE 4: DOCTOR APPROVAL
Time: __ minutes
Status: ✅ / ❌
Issues: ___________________
Notes: ____________________

STAGE 5: LAB SCHEDULING
Time: __ minutes
Status: ✅ / ❌
Calendar Event Created: ✅ / ❌
Event ID: ________________
Issues: ___________________
Notes: ____________________

STAGE 6: LAB RESULTS
Time: __ minutes
Status: ✅ / ❌
Tests Parsed: __ / 4
Normal Count: Correct ✅ / ❌
Issues: ___________________
Notes: ____________________

STAGE 7: DOCTOR CONSULTATION
Time: __ minutes
Status: ✅ / ❌
Diagnosis Shown: ✅ / ❌
Issues: ___________________
Notes: ____________________

STAGE 11: PRESCRIPTION
Time: __ minutes
Status: ✅ / ❌
Medications Parsed: __ / 1
Follow-up Scheduled: ✅ / ❌
Calendar Event Created: ✅ / ❌
Event ID: ________________
Issues: ___________________
Notes: ____________________

STAGE 12: COMPLETION
Time: __ minutes
Status: ✅ / ❌
Section 8 Updated: ✅ / ❌
Issues: ___________________
Notes: ____________________

TOTAL TIME: __ minutes
OVERALL SUCCESS: ✅ / ❌
MAJOR ISSUES: ___________________
IMPROVEMENTS NEEDED: ___________________
```

---

## 🎨 Frontend Improvements to Test

### During Testing, Note:

1. **UI/UX Issues**
   - Buttons not visible
   - Text hard to read
   - Layout broken on mobile
   - Slow loading

2. **Missing Features**
   - No stage indicator
   - Document link not prominent
   - Calendar not showing
   - No notifications

3. **Confusing Flow**
   - Unclear instructions
   - Too many steps
   - Waiting time unclear
   - No progress feedback

4. **Nice-to-Have**
   - Better animations
   - Sound notifications
   - Dark mode
   - Keyboard shortcuts

---

## 📸 Screenshots to Capture

1. Login page
2. Chat interface
3. Medical history questions
4. Document link display
5. Calendar integration
6. Lab results display
7. Prescription view
8. Completion summary
9. Google Document (all 8 sections)
10. Google Calendar (both appointments)

---

## 🚨 Emergency Contacts

**If stuck:**
1. Check backend logs in terminal
2. Check browser console (F12)
3. Look at network tab for failed API calls
4. Verify document permissions
5. Check Redis for patient state

**Useful Commands:**
```bash
# Check backend health
curl http://localhost:8000/health

# Check patient state in Redis
redis-cli GET "patient_state:iamsamarth786@gmail.com"

# View backend logs
# (Should be visible in terminal where you ran python main.py)

# Check document permissions
# Open document and check "Share" settings
```

---

## ✅ Pre-Test Checklist

Run this before starting:

```bash
# 1. Check credentials
python check_credentials.py

# 2. Reset patient state
python reset_patient_state.py

# 3. Start backend
python main.py &

# 4. Start frontend
cd frontend && npm run dev &

# 5. Open browser
# - http://localhost:3000
# - http://localhost:8000/docs

# 6. Open document
# - https://docs.google.com/document/d/1kAgV4vOZkrrh2FZeKmQ2r8CDp9w2MG6KfZiKuSXw_pY/edit

# 7. Open Google Calendar
# - https://calendar.google.com

# All set! Start testing! 🚀
```

---

## 🎉 Success Metrics

**Test is successful if:**
- ✅ All 8 stages complete without errors
- ✅ Document created with all sections
- ✅ Both calendar events created
- ✅ AI reads all sections correctly
- ✅ Patient receives all information
- ✅ Total time < 30 minutes
- ✅ No manual intervention needed (except doctor updates)

**Test needs improvement if:**
- ⚠️ Any stage fails
- ⚠️ Calendar integration doesn't work
- ⚠️ AI misreads sections
- ⚠️ Frontend is confusing
- ⚠️ Takes too long (>30 minutes)

---

**Ready to test! Good luck! 🚀**

**Estimated total test time:** 20-25 minutes
