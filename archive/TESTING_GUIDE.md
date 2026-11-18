# 🧪 COMPLETE TESTING GUIDE - AI Agent Hospital System

**Date:** October 19, 2025  
**Purpose:** Step-by-step guide to test the AI workflow integration

---

## 🚀 STEP 1: START THE BACKEND

### **Terminal 1: Python Backend**
```powershell
# Navigate to project root
cd "d:\ai agent by myself\ai agent"

# Activate virtual environment
& "D:/ai agent by myself/ai agent/.venv/Scripts/Activate.ps1"

# Start FastAPI backend
python main.py
```

**Expected Output:**
```
✅ All 113+ Hospital Management Tools Imported Successfully!
INFO:     Started server process [12345]
INFO:     Waiting for application startup.
INFO:     Application startup complete.
INFO:     Uvicorn running on http://127.0.0.1:8000
```

**Backend URLs:**
- API Base: `http://localhost:8000`
- Swagger Docs: `http://localhost:8000/docs`
- Alternative Docs: `http://localhost:8000/redoc`

---

## 🎨 STEP 2: START THE FRONTEND

### **Terminal 2: Next.js Frontend**
```powershell
# Navigate to frontend folder
cd "d:\ai agent by myself\ai agent\frontend"

# Start Next.js dev server
npm run dev
```

**Expected Output:**
```
   ▲ Next.js 15.5.6 (Turbopack)
   - Local:        http://localhost:3000
 ✓ Ready in 29.4s
```

**Frontend URL:** `http://localhost:3000`

---

## 👤 STEP 3: LOGIN AS STAFF

1. Open browser: `http://localhost:3000`
2. Click **"Login"** or navigate to `/login`
3. Use staff credentials:
   - **Username:** `staff`
   - **Password:** `staff123`
4. Click **"Sign In"**
5. You'll be redirected to Staff Dashboard

---

## 🤖 STEP 4: TEST AI WORKFLOW TRIGGER

### **4.1 Navigate to Staff Dashboard**
- URL: `http://localhost:3000/staff/dashboard`
- You should see:
  - ✅ Stats cards (appointments, check-ins, patients)
  - ✅ **"Start AI Workflow"** button (top-right)
  - ✅ **AI Approval Queue** card
  - ✅ **Proactive Agent Monitor** card

### **4.2 Start a New Workflow**
1. Click **"🤖 Start AI Workflow"** button (top-right corner)
2. Dialog opens with patient data form
3. Fill in the form:
   ```
   Basic Information:
   - Full Name: John Doe
   - Age: 45
   - Gender: Male
   - Phone: +1234567890
   - Email: john.doe@example.com

   Medical Information:
   - Symptoms: Chest pain and shortness of breath
   - Existing Conditions: Hypertension
   - Allergies: Penicillin
   - Current Medications: Lisinopril 10mg daily

   Insurance:
   - Provider: Blue Cross Blue Shield
   - ID: BCBS123456

   Emergency Contact:
   - Name: Jane Doe
   - Phone: +1234567891
   ```
4. Review the AI workflow explanation at bottom
5. Click **"Start AI Workflow"**
6. Watch for success toast notification

### **4.3 Monitor Backend Logs**
Switch to **Terminal 1** (backend) and watch for:
```
INFO: Starting workflow for patient: John Doe
INFO: Stage 1 - Registration Agent: Processing patient registration
INFO: Stage 2 - Document Processing Agent: Checking for documents
INFO: Stage 3 - Medical History Agent: Analyzing medical history
INFO: Stage 4 - Determine Tests with LLM: AI analyzing symptoms...
INFO: Stage 5 - Lab Coordination Agent: Scheduling tests...
...
```

---

## 📊 STEP 5: TEST WORKFLOW PROGRESS WIDGET

### **5.1 View Workflow Progress (Staff Side)**
Although not yet added to staff dashboard, you can test by:

1. Get the patient_id from backend logs (e.g., `patient_id: 123`)
2. Open browser console (F12)
3. Test API call:
   ```javascript
   fetch('http://localhost:8000/api/workflow/state/123', {
     headers: { 'Authorization': `Bearer ${localStorage.getItem('token')}` }
   })
   .then(r => r.json())
   .then(data => console.log(data))
   ```

**Expected Response:**
```json
{
  "patient_id": 123,
  "patient_name": "John Doe",
  "current_stage": "Lab Coordination",
  "workflow_status": "active",
  "stages": [
    {
      "stage_name": "Registration",
      "status": "completed",
      "started_at": "2025-10-19T10:00:00",
      "completed_at": "2025-10-19T10:01:00"
    },
    {
      "stage_name": "Document Processing",
      "status": "completed",
      ...
    },
    {
      "stage_name": "Lab Coordination",
      "status": "in_progress",
      "started_at": "2025-10-19T10:05:00"
    },
    ...
  ]
}
```

### **5.2 Add Widget to Patient Dashboard (Quick Test)**
To test the WorkflowProgressWidget on patient side:

1. Navigate to patient dashboard page:
   ```
   File: frontend/src/app/patient/dashboard/page.tsx
   ```
2. Add import at top:
   ```typescript
   import { WorkflowProgressWidget } from '@/components/workflow';
   ```
3. Add widget in the main content area:
   ```typescript
   <WorkflowProgressWidget patientId={1} showDetails={true} />
   ```
4. Save and refresh browser
5. Login as patient (username: `patient`, password: `patient123`)
6. View your workflow progress!

---

## ✅ STEP 6: TEST APPROVAL QUEUE (HITL)

### **6.1 Trigger Approval Request**
The AI will automatically create approval requests when:
- Ordering expensive tests (>$500)
- High-value prescriptions
- Critical treatment decisions
- Insurance claims

**Watch the Approval Queue card on Staff Dashboard:**
- Should show pending approval requests
- Badge shows count of pending items
- Priority badges (Low/Normal/High/Critical)

### **6.2 Approve a Request**
1. Find a pending request in the Approval Queue
2. Read the AI reasoning (shows why AI wants this)
3. Click **"Details"** to see full information
4. Click **"Approve"** to confirm
5. Confirmation dialog opens
6. Click **"Confirm Approval"**
7. Watch backend execute the approved action

### **6.3 Reject a Request**
1. Find a pending request
2. Click **"Reject"**
3. Enter rejection reason: "Cost too high, order alternative test"
4. Click **"Confirm Rejection"**
5. AI workflow will handle the rejection

---

## 🤖 STEP 7: TEST PROACTIVE AGENT

### **7.1 Start the Agent**
1. Find **"Proactive AI Agent"** card on Staff Dashboard
2. Click **"Start Agent"** button (green)
3. Watch status change to **"Running"**
4. Success toast appears

### **7.2 Monitor Agent Activity**
Watch for:
- **Statistics Cards** updating:
  - Total Checks
  - Actions Taken
  - Approvals Requested
  - Alerts Sent
- **Monitoring Tasks** showing active status:
  - Critical lab results (every 30 min)
  - Low inventory alerts (hourly)
  - Appointment reminders (daily)
  - Pattern analysis (daily)
  - Prescription refills (weekly)
  - Approval timeouts (hourly)
- **Recent Alerts** appearing in scrollable list

### **7.3 View Alert Details**
1. Wait for alerts to appear (or trigger manually via backend)
2. Click **"Details"** on any alert
3. Dialog shows:
   - Alert type
   - Severity badge
   - Patient information (if applicable)
   - Full message
   - Timestamp
   - Resolution status

### **7.4 Stop the Agent**
1. Click **"Stop Agent"** button (red)
2. Status changes to **"Stopped"**
3. Monitoring tasks pause

---

## 💬 STEP 8: TEST PATIENT AI CHATBOT

### **8.1 Login as Patient**
1. Logout from staff account
2. Login with patient credentials:
   - **Username:** `patient`
   - **Password:** `patient123`
3. Navigate to Patient Dashboard

### **8.2 Access AI Chatbot**
1. Look for **"AI Assistant"** in patient navigation
2. Or go directly to: `http://localhost:3000/patient/chatbot`

### **8.3 Test Chatbot Capabilities**
The patient AI chatbot uses the same 113 tools but filtered for patient-safe operations:

**Test Queries:**
```
1. "What are my upcoming appointments?"
   → AI uses GetPatientAppointmentsTool
   → Returns list of appointments

2. "Show me my latest lab results"
   → AI uses GetPatientLabHistoryTool
   → Returns recent lab tests with results

3. "What medications am I currently taking?"
   → AI uses GetDispensingHistoryTool
   → Returns active prescriptions

4. "I need to schedule a follow-up appointment"
   → AI uses CheckDoctorAvailabilityTool + ScheduleAppointmentTool
   → Books appointment

5. "What is my current bill balance?"
   → AI uses GetPatientBalanceTool
   → Returns outstanding balance

6. "I have a question about my diagnosis"
   → AI uses GetMedicalHistoryTool + MedicalRAGTool
   → Provides information using RAG

7. "Send me a reminder for my next appointment"
   → AI uses SendNotificationTool
   → Sends SMS/Email reminder
```

### **8.4 Chatbot Features**
- ✅ **Natural language understanding** (powered by Gemini 2.0 Flash)
- ✅ **Tool selection** (AI chooses right tool for query)
- ✅ **Patient-safe filters** (can't access other patients' data)
- ✅ **Medical RAG** (semantic search over medical records)
- ✅ **Multi-channel responses** (can send SMS, email, WhatsApp)
- ✅ **Context awareness** (remembers conversation history)

---

## 🔄 STEP 9: TEST REAL-TIME AUTO-REFRESH

### **9.1 Test Auto-Refresh Intervals**
Open Staff Dashboard and watch components auto-refresh:

| Component | Refresh Interval | What Updates |
|-----------|------------------|--------------|
| **Approval Queue** | 10 seconds | New approval requests appear |
| **Agent Status** | 10 seconds | Agent running status |
| **Agent Stats** | 30 seconds | Statistics counters |
| **Agent Alerts** | 15 seconds | New alerts appear |

### **9.2 Multi-Tab Test**
1. Open Staff Dashboard in **Tab 1**
2. Open Staff Dashboard in **Tab 2**
3. In Tab 1, approve a request
4. Watch Tab 2 auto-refresh and show updated queue
5. Both tabs stay in sync!

---

## 📱 STEP 10: TEST MULTI-CHANNEL NOTIFICATIONS

### **10.1 Test Email Notifications**
When AI workflow reaches certain stages:
- Welcome email on registration
- Lab test details email
- Test results email
- Admission details email
- Discharge summary email
- Follow-up appointment email

**Check Gmail inbox** (if configured) or check backend logs:
```
INFO: Sent email to john.doe@example.com: Welcome to Hospital
INFO: Email sent successfully (Message ID: <123@gmail.com>)
```

### **10.2 Test SMS Notifications**
If Twilio is configured:
- Appointment reminders
- Lab results ready notifications
- Prescription ready alerts

**Check Twilio dashboard** or backend logs:
```
INFO: Sent SMS to +1234567890: Your appointment is tomorrow at 2 PM
INFO: SMS sent successfully (Message SID: SM123abc)
```

### **10.3 Test WhatsApp Notifications**
If Twilio WhatsApp is configured:
- Critical alerts
- Urgent messages

---

## 🐛 STEP 11: TEST ERROR HANDLING

### **11.1 Test Invalid Patient Data**
1. Click "Start AI Workflow"
2. Leave required fields empty
3. Click submit
4. Should show validation error toast

### **11.2 Test Network Error**
1. Stop backend (Ctrl+C in Terminal 1)
2. Try to start workflow in frontend
3. Should show error toast: "Failed to start workflow"
4. Restart backend
5. Try again - should work

### **11.3 Test Approval Timeout**
1. Wait for approval request
2. Don't approve within timeout period
3. Proactive agent should send alert: "Approval timeout"

---

## 📊 STEP 12: TEST ANALYTICS & MONITORING

### **12.1 View Backend Metrics**
1. Open Swagger UI: `http://localhost:8000/docs`
2. Test endpoints:
   - `GET /api/analytics/system-overview` - System metrics
   - `GET /api/analytics/patients` - Patient statistics
   - `GET /api/analytics/revenue` - Revenue analytics
   - `GET /api/agent/stats` - Agent statistics

### **12.2 Monitor WebSocket**
Open browser console (F12) and connect to WebSocket:
```javascript
const ws = new WebSocket('ws://localhost:8000/ws/monitor');
ws.onmessage = (event) => {
  console.log('Real-time update:', JSON.parse(event.data));
};
```

---

## ✅ EXPECTED RESULTS

### **Successful Test Checklist:**
- [x] Backend starts without errors
- [x] Frontend starts without errors
- [x] Can login as staff
- [x] "Start AI Workflow" button visible
- [x] Workflow form opens and submits
- [x] Backend logs show 11 workflow stages executing
- [x] Approval Queue shows pending requests
- [x] Can approve/reject requests
- [x] Proactive Agent can be started/stopped
- [x] Agent alerts appear in real-time
- [x] Patient chatbot responds to queries
- [x] Components auto-refresh correctly
- [x] Error handling works

### **Performance Expectations:**
- Workflow start: < 2 seconds
- Approval process: < 1 second
- Agent start: < 1 second
- Chatbot response: < 3 seconds (LLM call)
- Auto-refresh: No UI lag

---

## 🐞 TROUBLESHOOTING

### **Issue: Frontend won't start**
```powershell
# Clear cache and reinstall
cd "d:\ai agent by myself\ai agent\frontend"
Remove-Item -Recurse -Force .next, node_modules
npm install
npm run dev
```

### **Issue: Backend shows tool import errors**
```powershell
# Reinstall Python dependencies
cd "d:\ai agent by myself\ai agent"
pip install -r requirements.txt
```

### **Issue: Can't see workflow components**
- Clear browser cache (Ctrl+Shift+Delete)
- Hard refresh (Ctrl+Shift+R)
- Check browser console for errors (F12)

### **Issue: API calls fail with 401 Unauthorized**
- Check if token exists: `localStorage.getItem('token')`
- Try logging out and logging back in
- Check backend logs for authentication errors

### **Issue: Workflow doesn't progress**
- Check backend logs for errors
- Verify database connection
- Check if all 113 tools imported successfully
- Look for Python exceptions in terminal

---

## 📝 TEST DATA EXAMPLES

### **Test Patient 1: Routine Checkup**
```
Name: Alice Johnson
Age: 35
Gender: Female
Symptoms: Annual physical checkup
Conditions: None
Allergies: None
```
**Expected:** Fast workflow, no approvals needed

### **Test Patient 2: Emergency Case**
```
Name: Bob Smith
Age: 62
Gender: Male
Symptoms: Severe chest pain, difficulty breathing
Conditions: Diabetes, Heart disease
Allergies: Aspirin
```
**Expected:** Multiple approval requests, fast escalation

### **Test Patient 3: Complex Case**
```
Name: Carol Davis
Age: 48
Gender: Female
Symptoms: Persistent headache, vision problems
Conditions: Hypertension, Migraine history
Allergies: Penicillin, Sulfa drugs
```
**Expected:** AI requests multiple tests, needs approvals

---

## 🎯 SUCCESS METRICS

**You have a working AI agent system when:**
1. ✅ All 113 tools load successfully
2. ✅ Workflows execute all 11 stages
3. ✅ HITL approvals work end-to-end
4. ✅ Proactive agent monitors in background
5. ✅ Patient chatbot answers queries correctly
6. ✅ Real-time updates work smoothly
7. ✅ No console errors or backend crashes

---

## 🚀 NEXT STEPS AFTER TESTING

### **If Everything Works:**
1. Deploy to staging environment
2. Load test with multiple concurrent workflows
3. Train hospital staff on the system
4. Create user documentation
5. Plan production deployment

### **If Issues Found:**
1. Document all bugs in GitHub issues
2. Fix critical issues first (workflow, approvals)
3. Optimize performance bottlenecks
4. Add more error handling
5. Re-test until stable

---

**Happy Testing! 🎉**

If you encounter any issues, check:
1. Backend logs (Terminal 1)
2. Frontend console (F12 in browser)
3. Network tab (F12 → Network)
4. This troubleshooting guide

