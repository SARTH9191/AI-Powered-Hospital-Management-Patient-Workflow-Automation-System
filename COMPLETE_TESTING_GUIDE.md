# 🏥 Complete Hospital AI Agent Testing Guide
**End-to-End Testing: Stage 1 to Stage 11**

---

## 🚀 **SETUP & ACCESS**

### 1. Start the Backend
```bash
# Terminal 1: Start the AI Agent Backend
cd "D:\ai agent by myself\ai agent"
python main.py
# ✅ Server should run on http://localhost:8000
```

### 2. Start the Frontend
```bash
# Terminal 2: Start the React Frontend
cd "D:\ai agent by myself\ai agent\frontend"
npm run dev
# ✅ Frontend should run on http://localhost:3000
```

### 3. Access Points
- **Frontend UI**: http://localhost:3000
- **API Documentation**: http://localhost:8000/docs
- **WebSocket Monitor**: ws://localhost:8000/ws/monitor

---

## 🏗️ **TECHNOLOGY STACK OVERVIEW**

### **Database Architecture**:

#### **1. PostgreSQL (Primary Database)** 🐘
**Location**: `database/` folder
**Usage**: 
- Patient registration records
- Medical history and conditions
- Appointment scheduling
- Billing and payment records
- User authentication and roles
- Workflow state persistence

**Tables**:
```sql
- patients (patient_id, name, email, phone, medical_history)
- appointments (appointment_id, patient_id, doctor_id, date, time)
- medical_records (record_id, patient_id, conditions, allergies)
- billing (bill_id, patient_id, amount, status, payment_method)
- users (user_id, email, role, permissions)
- workflow_states (session_id, patient_id, current_stage, data)
```

#### **2. ChromaDB (Vector Search)** 🔍
**Location**: `data/chroma_db/` 
**Usage**:
- Medical symptom matching
- Disease diagnosis assistance
- Drug interaction checking
- Medical knowledge base search
- Similar case finding

**Example**:
```python
# When patient says: "I have chest pain and shortness of breath"
# ChromaDB searches medical knowledge base:
# Returns: ["Possible cardiac event", "Anxiety attack", "Asthma exacerbation"]
```

#### **3. Redis (Caching & Sessions)** ⚡
**Usage**:
- Session management
- Real-time WebSocket connections
- API response caching
- Temporary OTP storage
- Quick data access

#### **4. Google Workspace (Live Collaboration)** ☁️
**Account**: `pawarsamarth786@gmail.com`
**Tools**:
- **Google Sheets**: Real-time patient monitoring (6 sheets)
- **Google Docs**: Collaborative medical records (6 document types)
- **Google Calendar**: Appointment scheduling
- **Gmail**: Automated notifications
- **Google Drive**: Document storage and sharing

#### **5. Razorpay Integration** 💳
**Current Status**: **DUMMY MODE** for testing
**Suggestion**: 
```javascript
// For now, create a mock payment handler:
const mockPaymentSuccess = () => {
  return {
    payment_id: "pay_mock_" + Date.now(),
    status: "success",
    amount: paymentAmount,
    message: "✅ Payment Successful (DEMO MODE)"
  };
};
```
**Implementation Later**: Real Razorpay integration with actual payment gateway

---

## 👥 **ROLE-BASED TESTING WORKFLOW**

### **AUTHENTICATION FLOW**
- **Any Gmail Account**: Works for patient login (e.g., `test@gmail.com`, `iamsamarth786@gmail.com`)
- **Google OAuth**: Automatic login via Google (recommended)
- **Direct Login**: Email-based login for testing
- **Staff/Doctor (Google Workspace)**: `pawarsamarth786@gmail.com` (Direct Google Sheets/Docs access)

### **TEST CREDENTIALS (Examples)**
- **Your Account**: `iamsamarth786@gmail.com` / Phone: `+91-7447444532`
- **Any Gmail**: `test@gmail.com`, `doctor@gmail.com`, etc.
- **Google Workspace**: `pawarsamarth786@gmail.com` (for sheets/docs monitoring)

### **IMPORTANT NOTE**:
- **✅ ANY Gmail account can login and use the AI agent**
- **Patient interacts via Frontend UI** (http://localhost:3000)
- **Doctor/Staff work directly in Google Workspace** (Sheets, Docs, Calendar)
- **AI Agent monitors Google Workspace changes in real-time** 📊

---

## 🎯 **STAGE-BY-STAGE TESTING PROTOCOL**

### **STAGE 1: PATIENT REGISTRATION** 👤
**Role**: Patient (New Registration)
**Frontend**: http://localhost:3000

**Authentication Options**:
1. **Google OAuth** (Recommended): Click "Login with Google" → Any Gmail account
2. **Direct Login**: Use email directly → Any @gmail.com address

**Test Conversation** (after login):
```
Patient: "Hi, I want to register as a new patient"

Expected AI Response: "Welcome! I'll help you register. Let me gather your information."

Patient Input Required:
✅ Full Name: "Samarth Kiran Pawar" (or any name)
✅ Phone: "+91-7447444532" (or any phone)
✅ Email: Auto-filled from login (e.g., "iamsamarth786@gmail.com")
✅ Date of Birth: "1995-03-12" (or any DOB)
✅ Gender: "Male" (or any gender)
✅ Address: "Your address" (or any address)

AI Should Execute:
- RegisterPatientTool() 
- CreatePatientFolderTool() (Google Drive)
- AddPatientRecordTool() (Google Sheets)
- SendWelcomeEmailTool() (Gmail)
- SendNotificationTool() (SMS/Email confirmation)
```

**Verification Steps**:
- [ ] Patient ID generated
- [ ] Google Drive folder created  
- [ ] Google Sheets record added
- [ ] Welcome email sent
- [ ] SMS confirmation received
- [ ] Workflow state saved

---

### **STAGE 2: OTP VERIFICATION** 📱
**Role**: Same Patient 
**Frontend**: Continue in same chat

**Test Conversation**:
```
AI: "Please verify the OTP sent to your phone: +91-9876543210"

Patient: "My OTP is 123456" (Check your actual SMS at +91-7447444532)

AI Should Execute:
- Verify OTP via Twilio
- Update patient verification status
- Move to Stage 3
```

**Verification Steps**:
- [ ] OTP validation successful
- [ ] Patient marked as verified
- [ ] Stage progression to 3

---

### **STAGE 3: MEDICAL HISTORY** 📋
**Role**: Same Patient
**Frontend**: Continue conversation

**Test Conversation**:
```
AI: "Now let's gather your medical history for better care."

Patient: "I have diabetes and high blood pressure. I'm allergic to penicillin."

AI Should Execute:
- GetMedicalHistoryTool()
- AddAllergyTool() - Penicillin, Severe
- AddChronicConditionTool() - Diabetes, Hypertension
- UpdatePatientStatusTool() (Google Sheets monitoring)
- AddDoctorNoteTool() (Google Sheets bidirectional)
```

**Google Workspace Integration Test**:
```
🔄 OPTION A (Sheets Monitoring): 
- Check "Patient Status" sheet (pawarsamarth786@gmail.com)
- See Samarth's update in real-time
- Doctor notes added to "Doctor Notes" sheet

🔄 OPTION B (Docs Collaboration):
- Medical document created: "Samarth Pawar - Medical History.docx"
- Auto-shared with pawarsamarth786@gmail.com for review
```

**Verification Steps**:
- [ ] Medical conditions recorded
- [ ] Allergies properly flagged
- [ ] Google Sheets updated with patient status
- [ ] Doctor notes visible to medical team
- [ ] Medical document created and shared

---

### **STAGE 4: DOCTOR APPROVAL** 👨‍⚕️
**Role**: Doctor (Direct Google Sheets Access)
**Action**: Open Google Sheets with `pawarsamarth786@gmail.com`

**Staff Input** (Google Sheets - Real-time):
```
🔄 Open "Patient Status" Google Sheet (pawarsamarth786@gmail.com):
- Find row: Samarth Kiran Pawar
- Update "Doctor Approval" column: "APPROVED - Dr. Smith"
- Add note: "Diabetes management plan needed. Refer to endocrinologist."
```

**AI Auto-Detection**:
```
AI automatically detects Google Sheets changes:

AI Should Execute:
- ReadPatientStatusTool() (Monitor sheets changes)
- Check approval status from sheets
- Update patient workflow status automatically
- Progress to Stage 5
```

**Verification Steps**:
- [ ] Doctor approval recorded
- [ ] Patient notified of approval
- [ ] Workflow progresses automatically

---

### **STAGE 5: LAB COORDINATION** 🧪
**Role**: Back to Patient  
**Frontend**: Switch back to patient login

**Test Conversation**:
```
Patient: "When can I get my lab tests done?"

AI: "I'll schedule your lab tests. What date works for you?"

Patient: "Tomorrow morning, November 1st, 2025 at 9 AM"

AI Should Execute:
- ScheduleAppointmentTool() - Lab appointment
- CreateAppointmentTool() (Google Calendar)  
- SendNotificationTool() - Appointment confirmation
- UpdateLabResultTool() (Sheets monitoring)
```

**Google Calendar Integration**:
```
✅ Check Google Calendar: "Hospital Lab Tests"
- Event: "John Doe - Lab Tests"  
- Date: 2025-11-01 09:00
- Location: Hospital Lab
- Attendees: patient email
```

**Verification Steps**:
- [ ] Lab appointment scheduled
- [ ] Google Calendar event created
- [ ] Confirmation email/SMS sent
- [ ] Lab results sheet prepared

---

### **STAGE 6: RESULTS ANALYSIS** 📊
**Role**: Staff (Lab Technician)
**Frontend**: Login as `nurse.jane@hospital.com`

**Staff Input** (Google Sheets - Lab Results):
```
🔄 Open "Lab Results" Google Sheet (pawarsamarth786@gmail.com):
- Find: Samarth Kiran Pawar - 2025-11-01
- Update results:
  * Blood Sugar: 180 mg/dL (HIGH)
  * Blood Pressure: 150/95 (HIGH)  
  * Cholesterol: 220 mg/dL (BORDERLINE)
- Status: "COMPLETED"
```

**AI Monitoring & Analysis**:
```
AI automatically detects lab result updates:

AI Should Execute:
- ReadLabResultsMonitoringTool() (Real-time sheets monitoring)
- UpdateLabResultTool() (Update status)  
- SendGmailTool() (Results to doctor)
- Analyze results for critical values
```

**Doctor Notification**:
```
📧 Gmail sent to pawarsamarth786@gmail.com:
"URGENT: Samarth Pawar lab results show elevated glucose and BP. 
Recommend immediate consultation."
```

**Verification Steps**:
- [ ] Lab results automatically detected
- [ ] Critical values flagged
- [ ] Doctor immediately notified
- [ ] Patient status updated

---

### **STAGE 7: ADMISSION PLANNING** 🏥
**Role**: Doctor reviewing results
**Frontend**: Login as doctor

**Test Conversation**:
```
Doctor: "John's results are concerning. Let's admit him for observation."

AI: "I'll plan the admission. Checking availability..."

AI Should Execute:
- CheckAvailabilityTool() (Hospital beds)
- CreateBillingRecordTool() (Insurance/billing)
- GenerateInvoiceTool() (Cost estimation)
- CreateAppointmentTool() (Admission slot)
- CreateMedicalDocumentTool() (Treatment plan)
```

**Option B - Google Docs Collaboration**:
```
📄 AI Creates: "Samarth Pawar - Treatment Plan.docx"
Contents:
- Patient: Samarth Kiran Pawar
- Admission Date: 2025-11-02
- Primary Concerns: Diabetes, Hypertension
- Treatment Plan: IV fluids, medication adjustment
- Monitoring: Q4H vitals, daily glucose checks

🔄 Document auto-shared with:
- pawarsamarth786@gmail.com (Medical team access)
- Treatment team can edit collaboratively
```

**Verification Steps**:
- [ ] Bed availability checked
- [ ] Insurance verified
- [ ] Cost estimate generated
- [ ] Treatment plan created and shared
- [ ] Admission scheduled

---

### **STAGE 8: TREATMENT & MONITORING** 💊
**Role**: Multiple roles (Patient, Doctor, Staff)

**Patient Experience**:
```
Patient: "How is my treatment going?"

AI Should Execute:
- ReadMedicalDocumentTool() (Latest treatment notes)
- ReadPatientStatusTool() (Current status)
- UpdateMedicalDocumentTool() (Progress notes)
```

**Staff Updates** (Real-time Google Sheets):
```
🔄 Update "Patient Status" sheet (pawarsamarth786@gmail.com):
- Samarth Pawar - Room 204
- Vitals: BP 140/90, Glucose 150 (improving)
- Medications: Metformin 500mg, Lisinopril 10mg
- Status: "STABLE - Responding well"
```

**Doctor Collaboration** (Google Docs):
```
🔄 Dr. Smith updates treatment document:
"Day 2 Progress: Patient responding well to medication.
Glucose levels stabilizing. Plan to discharge tomorrow
if trends continue."
```

**Verification Steps**:
- [ ] Real-time status monitoring
- [ ] Multi-user document collaboration
- [ ] Treatment progress tracked
- [ ] Care team coordination

---

### **STAGE 9: BILLING & DISCHARGE** 💳
**Role**: Admin/Billing staff
**Frontend**: Login as admin

**Test Conversation**:
```
Admin: "Process John Doe's discharge and final billing"

AI Should Execute:
- GenerateInvoiceTool() (Final bill)
- CreateBillingRecordTool() (Payment processing)
- UpdateAppointmentTool() (Discharge time)
- SendNotificationTool() (Discharge instructions)
```

**Billing Integration**:
```
📊 Google Sheets - "Billing Records":
- Patient: John Doe
- Admission: 2025-11-02 to 2025-11-04
- Services: Room (2 days), Lab tests, Medications
- Total: ₹15,000
- Insurance: ₹12,000 
- Patient Pay: ₹3,000
- Status: READY FOR DISCHARGE
```

**Verification Steps**:
- [ ] Final bill generated
- [ ] Insurance processed
- [ ] Payment collected
- [ ] Discharge paperwork ready

---

### **STAGE 10: MEDICATION MANAGEMENT** 💊
**Role**: Pharmacist
**Frontend**: Login as pharmacy staff

**Test Conversation**:
```
Pharmacist: "Preparing discharge medications for John Doe"

AI Should Execute:
- Check medication history
- Verify allergies (Penicillin flagged)
- Generate prescription
- Update medication records
```

**Medication Safety Check**:
```
✅ AI Safety Analysis:
- Patient allergic to Penicillin ❌
- Prescribed Metformin ✅ (Safe)
- Prescribed Lisinopril ✅ (Safe)
- Drug interaction check: CLEAR ✅
```

**Verification Steps**:
- [ ] Allergy checks performed
- [ ] Drug interactions verified
- [ ] Prescription generated safely

---

### **STAGE 11: FOLLOW-UP SCHEDULING** 📅
**Role**: Patient (post-discharge)
**Frontend**: Patient login

**Test Conversation**:
```
Patient: "I need to schedule my follow-up appointment"

AI: "I'll schedule your follow-up. When works best for you?"

Patient: "Next week, November 10th at 2 PM"

AI Should Execute:
- CheckAvailabilityTool() (Doctor schedule)
- CreateAppointmentTool() (Follow-up)  
- SendNotificationTool() (Confirmation)
- Complete workflow cycle
```

**Google Calendar Integration**:
```
📅 Follow-up appointment created:
- Date: 2025-11-10 14:00
- Type: Post-discharge follow-up
- Doctor: Dr. Smith
- Notes: "Diabetes management review"
```

**Verification Steps**:
- [ ] Follow-up scheduled
- [ ] Calendar updated
- [ ] Patient notified
- [ ] Workflow completed successfully

---

## 🔍 **CRITICAL ERROR MONITORING**

### **Watch for These Issues**:

**1. Import Errors**:
```bash
❌ ModuleNotFoundError: No module named 'tools.xyz'
✅ Fix: Update imports in workflow_chat_agent.py
```

**2. Google Workspace Authentication**:
```bash
❌ Error initializing Sheets service: credentials.json
✅ Fix: Ensure client_secret.json and token.pickle exist
```

**3. Database Connection Issues**:
```bash
❌ PostgreSQL connection failed
✅ Fix: Check database credentials in .env
```

**4. Tool Execution Failures**:
```bash
❌ Tool XYZ failed to execute
✅ Fix: Check tool implementation and parameters
```

---

## 📊 **SUCCESS METRICS**

### **Complete Success Criteria**:
- [ ] All 11 stages complete without errors
- [ ] Google Workspace integration working (5 tools)
- [ ] Real-time bidirectional communication
- [ ] Multi-role collaboration
- [ ] Database persistence
- [ ] Notification system functional
- [ ] WebSocket monitoring active

### **Performance Benchmarks**:
- **Stage Transition**: < 2 seconds
- **Tool Execution**: < 5 seconds  
- **Google API Calls**: < 3 seconds
- **Database Queries**: < 1 second
- **WebSocket Updates**: Real-time

---

## 🚨 **DEBUGGING COMMANDS**

### **Check Backend Status**:
```bash
curl http://localhost:8000/health
```

### **Monitor WebSocket**:
```javascript
// Browser console
const ws = new WebSocket('ws://localhost:8000/ws/monitor');
ws.onmessage = (event) => console.log(JSON.parse(event.data));
```

### **Verify Database**:
```bash
# Check PostgreSQL connection
psql -h localhost -U your_user -d hospital_db -c "SELECT COUNT(*) FROM patients;"

# Check specific patient record
psql -h localhost -U your_user -d hospital_db -c "SELECT * FROM patients WHERE email='iamsamarth786@gmail.com';"
```

### **Test Vector Search (ChromaDB)**:
```python
# Test medical knowledge search
from src.vector_search import MedicalVectorSearch
search = MedicalVectorSearch()

# Test symptom matching
result = search.search_symptoms("chest pain shortness of breath")
print("Similar conditions:", result)

# Test drug interaction
interaction = search.check_drug_interaction("metformin", "lisinopril")
print("Drug safety:", interaction)
```

### **Test Razorpay (Dummy Mode)**:
```javascript
// Frontend - Mock payment for testing
const handlePayment = async (amount) => {
  // Simulate payment processing
  const mockResponse = {
    payment_id: `pay_mock_${Date.now()}`,
    status: "success",
    amount: amount,
    currency: "INR",
    method: "card",
    timestamp: new Date().toISOString()
  };
  
  console.log("✅ Payment Successful (DEMO MODE):", mockResponse);
  return mockResponse;
};
```

### **Test Google Workspace**:
```python
# Quick test in Python terminal
from tools.sheets_monitoring_tools import ReadPatientStatusTool
tool = ReadPatientStatusTool()
result = tool._run(patient_id="test123")
print(result)
```

---

## 🎯 **FINAL VALIDATION**

After completing all 11 stages, verify:

1. **Patient Journey Complete**: Registration → Discharge → Follow-up ✅
2. **Multi-Role Collaboration**: Patient, Doctor, Staff, Admin ✅  
3. **Google Workspace Integration**: All 5 tools working ✅
4. **Real-time Updates**: Bidirectional communication ✅
5. **Data Persistence**: All records saved ✅
6. **Notification System**: Email/SMS working ✅

---

## � **HOW TO RESTART/RESET FOR TESTING**

### **Method 1: Frontend Reset** (Easiest)
```javascript
// Open browser console (F12) and run:
localStorage.clear();
sessionStorage.clear();
window.location.reload();
```

### **Method 2: New Session ID**
```bash
# Use different session_id in API calls:
curl "http://localhost:8000/api/ai-chat/greeting?session_id=test456" -H "Authorization: Bearer $token"
```

### **Method 3: New Email Account**
- **Login with different Gmail**: `test123@gmail.com`, `doctor456@gmail.com`, etc.
- **Each email = New patient journey**

### **Method 4: Clear Database** (Complete Reset)
```bash
# Delete patient records (careful!)
rm "data/patients_database.json"
# Server will recreate empty database
```

### **Method 5: API Reset Endpoint** (TODO - We can add this)
```bash
# Future enhancement:
POST /api/patients/reset-workflow
```

---

## �📝 **NEXT STEPS**

Once testing is complete:
1. **Document all bugs found** 📋
2. **Fix critical issues first** 🔧  
3. **Optimize performance** ⚡
4. **Enhance UI/UX** 🎨
5. **Deploy to production** 🚀

---

## 🎯 **PRIORITY TESTING ORDER**

### **Phase 1: Core Functionality** (Test First)
1. ✅ Backend startup (python main.py)
2. ✅ Frontend connection (npm run dev)
3. ✅ Patient registration (Samarth's info)
4. ✅ Basic workflow progression (Stages 1-3)

### **Phase 2: Google Workspace Integration** (Critical)
1. 🔄 Google Sheets real-time updates
2. 🔄 Google Docs collaboration
3. 🔄 Gmail notifications
4. 🔄 Google Calendar appointments

### **Phase 3: Database Integration** (Foundation)
1. 📊 PostgreSQL patient storage
2. 🔍 ChromaDB vector search
3. ⚡ Redis session management

### **Phase 4: Advanced Features** (Later)
1. 💳 Razorpay dummy integration
2. 📱 Twilio SMS (real OTP)
3. 🔔 WebSocket real-time updates

### **Focus Strategy**: 
**Get Stages 1-6 working perfectly before moving to advanced features!**

---

**🎉 Congratulations! You now have a fully tested world-class Hospital AI Agent!**