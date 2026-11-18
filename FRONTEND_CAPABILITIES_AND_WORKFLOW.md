# 🏥 AI Medical Agent - Frontend Capabilities & Complete Workflow Guide

**Version:** Phase 2 Complete (Unified Document System)  
**Date:** November 14, 2025  
**Status:** ✅ Ready for End-to-End Testing

---

## 📋 Table of Contents

1. [System Overview](#system-overview)
2. [Complete Workflow Stages](#complete-workflow-stages)
3. [Frontend Capabilities](#frontend-capabilities)
4. [API Integration Points](#api-integration-points)
5. [Testing Checklist](#testing-checklist)
6. [Known Features](#known-features)
7. [Credentials & Setup](#credentials--setup)

---

## 🎯 System Overview

### Architecture

```
┌─────────────────┐
│  Frontend       │
│  (Next.js)      │
└────────┬────────┘
         │ HTTP/REST
         ▼
┌─────────────────┐
│  Backend API    │
│  (FastAPI)      │
└────────┬────────┘
         │
    ┌────┴────┬──────────┬──────────┬──────────┐
    ▼         ▼          ▼          ▼          ▼
┌────────┐ ┌──────┐ ┌────────┐ ┌────────┐ ┌──────┐
│ Google │ │Google│ │ Google │ │ LangChain│ │Redis│
│  Docs  │ │ Cal  │ │ Sheets │ │   LLM   │ │Cache│
└────────┘ └──────┘ └────────┘ └────────┘ └──────┘
```

### Key Components

- **Frontend**: Next.js + React + TypeScript
- **Backend**: Python FastAPI + LangChain
- **AI Engine**: Google Gemini Pro 1.5
- **Document System**: Single Unified Google Doc (8 Sections)
- **Calendar**: Google Calendar API
- **Storage**: Redis Cache + PostgreSQL

---

## 🔄 Complete Workflow Stages

### **Stage 1: ✨ Registration** (NEW/RETURNING USER)

**Purpose:** Identify patient and create/retrieve profile

**Frontend Features:**
- Login page with email/phone authentication
- Auto-detection of existing patients
- Smart patient search by name/phone/email
- Registration form for new patients

**User Experience:**
```
User: "Hello, I need medical help"
AI: "Welcome! Are you a new or returning patient?"

[NEW PATIENT]
→ Collects: Name, Phone, Email, DOB, Gender, Address
→ Creates patient record
→ Assigns Patient ID (e.g., PAT20251113001842)

[RETURNING PATIENT]
→ Asks for: Name or Phone
→ Searches database
→ Loads existing profile
→ Shows previous medical history
```

**Backend API:**
- `POST /api/agent/chat/message` - Process registration messages
- `GET /api/patients/{patient_id}` - Retrieve patient details
- `POST /api/patients/search` - Search existing patients

**Success Criteria:**
- ✅ Patient identified/created
- ✅ Patient ID assigned
- ✅ Profile stored in database

**Next Stage:** Stage 2 (Document Upload) or Stage 3 (Medical History)

---

### **Stage 2: 📄 Document Upload** (OPTIONAL - SKIPPABLE)

**Purpose:** Upload existing medical records, reports, prescriptions

**Frontend Features:**
- Drag & drop file upload
- Preview uploaded documents
- Support for: PDF, JPG, PNG, DOC, DOCX
- **SKIP OPTION** for returning patients

**User Experience:**
```
AI: "Do you have any medical documents to upload?"

[OPTION 1: Upload]
→ Patient uploads files
→ Files stored in Google Drive
→ Links added to patient record

[OPTION 2: Skip]
→ "skip" or "no documents"
→ Immediately advance to Stage 3
→ Mark stage as "skipped"
```

**Backend API:**
- `POST /api/agent/upload/document` - Upload documents
- `GET /api/agent/documents/{patient_id}` - List uploaded documents

**Success Criteria:**
- ✅ Documents uploaded/skipped
- ✅ Files linked to patient record
- ✅ Stage marked complete

**Next Stage:** Stage 3 (Medical History)

---

### **Stage 3: 🩺 Medical History + AI Analysis** (CRITICAL)

**Purpose:** Collect symptoms and medical history → Create Unified Google Doc

**Frontend Features:**
- Interactive symptom checker
- Medical history questionnaire
- Auto-save responses
- Previous history pre-fill (returning patients)

**User Experience:**
```
AI: "Please tell me about your current symptoms."
User: "I have fever, headache, and body pain for 3 days"

AI: "Any chronic conditions?"
User: "I have diabetes"

AI: "Current medications?"
User: "Taking Metformin 500mg"

AI: "Any allergies?"
User: "No allergies"

User: "That's all"

AI: ✅ Creating your medical workflow document...
```

**What Happens Behind the Scenes:**

1. **Data Collection:**
   - Symptoms
   - Duration
   - Severity
   - Chronic conditions
   - Current medications
   - Allergies
   - Family history

2. **AI Analysis:**
   - Symptoms analysis
   - Risk assessment
   - Preliminary diagnosis suggestions
   - Recommended tests

3. **Document Creation:**
   - Creates single unified Google Doc
   - Shares with doctor email
   - Updates 8 sections:

```
📄 UNIFIED WORKFLOW DOCUMENT STRUCTURE:

SECTION 1: PATIENT INFORMATION (AI Writes)
   - Name, Age, Contact
   - Visit Date
   - Chief Complaint

SECTION 2: MEDICAL HISTORY & AI ANALYSIS (AI Writes)
   - Symptoms
   - Chronic Conditions
   - Medications
   - AI Preliminary Assessment

SECTION 3: DOCTOR'S DECISION (Doctor Updates) ⬅ APPROVAL GATE
   - Tests Approved: Yes/No
   - Recommended Tests List
   - Special Instructions

SECTION 4: LAB TEST SCHEDULING (AI Writes)
   - Scheduled Tests
   - Appointment Date/Time
   - Location
   - Calendar Event ID

SECTION 5: LAB RESULTS (Lab Staff Updates)
   - Test Results
   - Normal/Abnormal Status
   - AI Analysis of Results

SECTION 6: POST-LAB CONSULTATION (Doctor Updates) ⬅ APPROVAL GATE
   - Diagnosis
   - Treatment Plan
   - Next Steps

SECTION 7: PRESCRIPTION & FOLLOW-UP (Doctor Updates)
   - Medications
   - Dosage & Duration
   - Dietary Instructions
   - Follow-up Date

SECTION 8: WORKFLOW COMPLETION SUMMARY (AI Writes)
   - Journey Timeline
   - Final Diagnosis
   - Complete Treatment Plan
```

**Backend API:**
- `POST /api/workflow/chat/message` - Process medical history
- `POST /api/workflow/documents/create` - Create unified doc
- `GET /api/workflow/documents/{doc_id}` - Get document

**Success Criteria:**
- ✅ Medical history collected
- ✅ AI analysis complete
- ✅ Unified document created
- ✅ Document shared with doctor
- ✅ Sections 1 & 2 populated

**Next Stage:** Stage 4 (Doctor Approval)

---

### **Stage 4: 👨‍⚕️ Doctor Approval & Test Determination** (APPROVAL GATE)

**Purpose:** Doctor reviews AI analysis and approves lab tests in document

**Frontend Features:**
- **Doctor Dashboard:**
  - Pending approvals list
  - Document viewer
  - Quick approval buttons
  - Test selection checkboxes

- **Patient View:**
  - "Waiting for doctor" status
  - Real-time approval notifications
  - Document link to check progress

**User Experience:**
```
AI: "Your medical history has been submitted to the doctor!"
    📄 Document: [Google Doc Link]
    📍 Check Section 3 for doctor's decision

    Please wait while the doctor reviews...

[MANUAL STEP - DOCTOR]
→ Opens document
→ Reviews Section 1 & 2
→ Updates SECTION 3:
   ✅ TESTS APPROVED
   Recommended Tests:
   1. Complete Blood Count (CBC)
   2. Blood Glucose (Fasting)
   3. Lipid Profile

[AI DETECTS UPDATE]
User: "Has the doctor approved?"
AI: ✅ Doctor has approved the following tests:
    • Complete Blood Count (CBC)
    • Blood Glucose (Fasting)
    • Lipid Profile
    
    Ready to schedule lab appointment!
```

**Backend API:**
- `GET /api/workflow/documents/{doc_id}/section/3` - Read Section 3
- `POST /api/workflow/documents/{doc_id}/section/3` - Update Section 3 (Doctor)
- `POST /api/workflow/check-approval` - Check approval status

**Success Criteria:**
- ✅ Doctor reviewed Section 1 & 2
- ✅ Tests approved in Section 3
- ✅ AI reads and confirms approval
- ✅ Patient notified

**Next Stage:** Stage 5 (Lab Scheduling)

---

### **Stage 5: 🧪 Lab Coordination & Scheduling**

**Purpose:** Schedule lab tests appointment → Update Section 4

**Frontend Features:**
- Calendar widget for date selection
- Available time slots
- Lab location map
- Appointment confirmation

**User Experience:**
```
AI: "Let's schedule your lab tests!"

[OPTION 1: Automatic]
AI: "I can schedule for tomorrow at 9 AM?"
User: "Yes, please"
→ AI creates calendar event automatically

[OPTION 2: Manual]
User: "I want to choose date"
AI: "When would you prefer?"
User: "Next Tuesday at 10 AM"
→ AI creates calendar event with selected time
```

**What Happens:**

1. **Calendar Event Creation:**
   - Creates Google Calendar appointment
   - Adds patient email
   - Sets location (City Hospital Lab)
   - Adds test details in description
   - Returns `calendar_event_id`

2. **Document Update (Section 4):**
   ```
   SCHEDULED TESTS:
   • Complete Blood Count (CBC)
   • Blood Glucose (Fasting)
   • Lipid Profile
   
   APPOINTMENT DETAILS:
   📅 Date: November 15, 2025
   ⏰ Time: 9:00 AM
   📍 Location: City Hospital Lab Services
   🕐 Duration: 45 minutes
   
   CALENDAR LINK:
   📅 Google Calendar Event Created
   Event ID: abc123xyz456
   ```

**Backend API:**
- `POST /api/calendar/create-appointment` - Create calendar event
- `PUT /api/workflow/documents/{doc_id}/section/4` - Update Section 4
- `GET /api/calendar/available-slots` - Get available times

**Success Criteria:**
- ✅ Appointment scheduled
- ✅ Calendar event created
- ✅ Section 4 updated with details
- ✅ Patient receives confirmation

**Next Stage:** Stage 6 (Lab Results)

---

### **Stage 6: 📊 Lab Results Analysis** (UNIFIED DOC - PHASE 2)

**Purpose:** Lab staff adds results to Section 5 → AI reads and displays

**🔥 CRITICAL CHANGE (Phase 2):**
- ❌ OLD: Read from Google Sheets
- ✅ NEW: Read from Section 5 of Unified Document

**Frontend Features:**
- "Check Results" button
- Real-time result notifications
- Visual result display (charts)
- Normal/Abnormal indicators

**User Experience:**
```
[AFTER LAB VISIT]
User: "Are my lab results ready?"

[RESULTS NOT YET ADDED]
AI: ⏳ Waiting for Lab Results
    The medical staff is working on your lab tests.
    📄 Document: [Link]
    📍 Section to check: Section 5 (LAB RESULTS)
    Type "check" to see if results are complete.

[LAB STAFF UPDATES SECTION 5]
→ Opens unified document
→ Finds SECTION 5: LAB RESULTS
→ Adds test results:

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

[AI READS SECTION 5]
User: "Check results"
AI: ✅ YOUR LAB RESULTS ARE READY!

📊 YOUR LAB TEST RESULTS:

✅ Complete Blood Count (CBC)
   • Result: 14.5 g/dL
   • Normal Range: 12.0-16.0 g/dL
   • Status: NORMAL

⚠️ Blood Glucose (Fasting)
   • Result: 126 mg/dL
   • Normal Range: 70-100 mg/dL
   • Status: ABNORMAL (Elevated)

✅ Lipid Profile
   • Result: 195 mg/dL
   • Normal Range: <200 mg/dL
   • Status: NORMAL

🤖 AI ANALYSIS:
Your blood glucose is elevated, indicating pre-diabetic condition.
This requires medical attention and lifestyle modifications.
```

**Backend API:**
- `GET /api/workflow/documents/{doc_id}/section/5` - Read Section 5
- `POST /api/workflow/check-lab-results` - Check if results ready
- `GET /api/workflow/lab-results/{patient_id}` - Get formatted results

**Success Criteria:**
- ✅ Lab results added to Section 5
- ✅ AI successfully reads results
- ✅ Results displayed to patient
- ✅ Normal/Abnormal counts correct

**Next Stage:** Stage 7 (Doctor Consultation)

---

### **Stage 7: 🏥 Doctor Consultation** (APPROVAL GATE)

**Purpose:** Doctor reviews results → Updates Section 6 with diagnosis

**Frontend Features:**
- **Doctor Dashboard:**
  - Lab results viewer
  - Consultation notes editor
  - Treatment plan builder
  - Section 6 direct editor

- **Patient View:**
  - "Waiting for consultation" status
  - Notification when ready
  - Consultation summary viewer

**User Experience:**
```
AI: "Your lab results are ready!"
    Please wait for doctor's consultation...
    📄 Check Section 6 for doctor's consultation notes

[MANUAL STEP - DOCTOR]
→ Reviews lab results in Section 5
→ Updates SECTION 6: POST-LAB CONSULTATION

👨‍⚕️ DOCTOR'S CONSULTATION
Date: November 16, 2025

DIAGNOSIS:
Pre-diabetic condition detected. Blood glucose elevated.

TREATMENT PLAN:
1. Start Metformin 500mg (if not already on it)
2. Dietary modifications required
3. Follow-up in 3 months

NEXT STEPS:
- Review prescription in next section
- Schedule follow-up appointment

[AI READS SECTION 6]
User: "What did the doctor say?"
AI: 👨‍⚕️ DOCTOR'S CONSULTATION COMPLETE!

📋 DIAGNOSIS:
Pre-diabetic condition detected. Blood glucose elevated.

💊 TREATMENT PLAN:
1. Start Metformin 500mg
2. Dietary modifications required
3. Follow-up in 3 months

📄 Full details: [Document Link]
```

**Backend API:**
- `GET /api/workflow/documents/{doc_id}/section/6` - Read Section 6
- `POST /api/workflow/documents/{doc_id}/section/6` - Update Section 6 (Doctor)
- `POST /api/workflow/check-consultation` - Check consultation status

**Success Criteria:**
- ✅ Doctor reviewed results
- ✅ Diagnosis added to Section 6
- ✅ Treatment plan documented
- ✅ Patient notified

**Next Stage:** Stage 11 (Prescription & Follow-up)

---

### **Stage 11: 💊 Prescription & Follow-up Care**

**Purpose:** Doctor adds prescription → AI reads Section 7 → Schedule follow-up

**Frontend Features:**
- Prescription viewer
- Medication list
- Dosage instructions
- Follow-up calendar integration

**User Experience:**
```
[DOCTOR UPDATES SECTION 7]
→ Opens unified document
→ Updates SECTION 7: PRESCRIPTION & FOLLOW-UP

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

[AI READS SECTION 7]
User: "What is my prescription?"
AI: 💊 YOUR PRESCRIPTION IS READY!

MEDICATIONS:
1. Metformin 500mg
   • Dosage: 1 tablet twice daily
   • Timing: With breakfast and dinner
   • Duration: 3 months

DIETARY INSTRUCTIONS:
🍽️ Limit sugar intake
🍽️ Increase fiber in diet
🍽️ Avoid processed foods

📅 SCHEDULING FOLLOW-UP APPOINTMENT...
→ Creates calendar event for February 16, 2026
✅ Follow-up appointment scheduled!
   Calendar Event ID: xyz789abc123

📄 Full prescription: [Document Link]
```

**What Happens:**

1. **AI Reads Section 7:**
   - Parses medications with dosage
   - Extracts dietary instructions
   - Identifies follow-up date

2. **Calendar Integration:**
   - Automatically creates follow-up appointment
   - Adds to patient's calendar
   - Stores `calendar_event_id`

**Backend API:**
- `GET /api/workflow/documents/{doc_id}/section/7` - Read Section 7
- `POST /api/workflow/documents/{doc_id}/section/7` - Update Section 7 (Doctor)
- `POST /api/calendar/create-followup` - Create follow-up appointment

**Success Criteria:**
- ✅ Prescription added to Section 7
- ✅ AI successfully reads prescription
- ✅ Follow-up date parsed
- ✅ Calendar event created
- ✅ Patient receives prescription

**Next Stage:** Stage 12 (Completion)

---

### **Stage 12: 🎉 Workflow Completion**

**Purpose:** Finalize journey → Update Section 8 with summary → Send notifications

**Frontend Features:**
- Journey timeline visualization
- Download complete medical record
- Print summary
- Share document link

**User Experience:**
```
User: "Thank you, is my treatment plan complete?"

AI: 🎉 HEALTHCARE JOURNEY COMPLETE!

✅ YOUR COMPLETE JOURNEY:

📋 STAGE SUMMARY:
1. ✅ Registration - November 13, 2025
2. ✅ Document Upload - Skipped
3. ✅ Medical History - November 13, 2025
4. ✅ Doctor Approval - November 14, 2025
5. ✅ Lab Scheduling - November 14, 2025
6. ✅ Lab Results - November 15, 2025
7. ✅ Doctor Consultation - November 16, 2025
11. ✅ Prescription - November 16, 2025
12. ✅ Completion - November 16, 2025

📊 FINAL DIAGNOSIS:
Pre-diabetic condition detected

💊 ACTIVE PRESCRIPTIONS:
• Metformin 500mg - 3 months

📅 UPCOMING APPOINTMENTS:
• Follow-up Consultation - February 16, 2026

📄 COMPLETE MEDICAL RECORD:
[Google Doc Link]

🔔 NOTIFICATIONS SENT:
• Email summary sent
• SMS confirmation sent
• Calendar invites sent

Thank you for trusting us with your healthcare! 💙
```

**What Happens:**

1. **Section 8 Update:**
   ```
   🎉 WORKFLOW COMPLETION SUMMARY
   
   JOURNEY TIMELINE:
   Stage 1: Registration - Nov 13, 2025
   Stage 3: Medical History - Nov 13, 2025
   Stage 4: Doctor Approval - Nov 14, 2025
   Stage 5: Lab Scheduling - Nov 14, 2025
   Stage 6: Lab Results - Nov 15, 2025
   Stage 7: Consultation - Nov 16, 2025
   Stage 11: Prescription - Nov 16, 2025
   Stage 12: Completion - Nov 16, 2025
   
   FINAL DIAGNOSIS:
   Pre-diabetic condition detected
   
   COMPLETE TREATMENT PLAN:
   • Metformin 500mg - twice daily for 3 months
   • Dietary modifications
   • Follow-up in 3 months
   
   PATIENT SATISFACTION:
   Please rate your experience (1-5 stars)
   ```

2. **Notifications:**
   - Email with document link
   - SMS confirmation
   - WhatsApp message (if configured)

**Backend API:**
- `PUT /api/workflow/documents/{doc_id}/section/8` - Update Section 8
- `POST /api/workflow/complete` - Mark workflow complete
- `POST /api/notifications/send-completion` - Send notifications

**Success Criteria:**
- ✅ Section 8 updated with summary
- ✅ All notifications sent
- ✅ Workflow marked complete
- ✅ Patient receives final summary

**Workflow End** ✅

---

## 🌐 Frontend Capabilities

### Current Frontend Features

#### 1. **Patient Dashboard** (`/patient/dashboard`)
- Overview of current stage
- Quick action buttons
- Upcoming appointments
- Recent activities
- Health metrics

#### 2. **Chatbot Interface** (`/patient/chatbot`)
- Real-time chat with AI agent
- Message history
- Quick action buttons:
  - Book Appointment
  - Refill Medication
  - Check Lab Results
  - Report Symptoms
- Typing indicators
- Auto-scroll messages
- Timestamp display

#### 3. **Appointments** (`/patient/appointments`)
- View all appointments
- Upcoming/Past tabs
- Calendar integration
- Appointment details
- Cancel/Reschedule options

#### 4. **Lab Results** (`/patient/labs`)
- View all lab reports
- Download PDF reports
- Normal/Abnormal indicators
- Trend charts
- Historical comparison

#### 5. **Medications** (`/patient/medications`)
- Active prescriptions
- Dosage schedules
- Refill requests
- Side effects reporting
- Medication reminders

#### 6. **Medical Records** (`/patient/records`)
- View all documents
- Download records
- Upload new documents
- Document viewer

#### 7. **Billing** (`/patient/billing`)
- View invoices
- Payment history
- Download receipts
- Payment gateway integration

#### 8. **Authentication** (`/loginPage`)
- Email/Phone login
- OTP verification
- New user registration
- Password reset

### Required Frontend Enhancements for Testing

#### **Priority 1: Critical for Testing**

1. **Document Viewer Integration** ✨ NEW
   ```tsx
   // Show unified document link prominently
   <DocumentViewer 
     docId={workflowDocId}
     docUrl={workflowDocUrl}
     currentSection={currentSection}
     allowEdit={userRole === 'doctor'}
   />
   ```

2. **Stage Progress Indicator** ✨ NEW
   ```tsx
   <StageProgress 
     currentStage={stage}
     completedStages={[1,2,3,4,5]}
     stages={[
       {id: 1, name: "Registration", icon: "✨"},
       {id: 2, name: "Documents", icon: "📄"},
       {id: 3, name: "Medical History", icon: "🩺"},
       // ... all 12 stages
     ]}
   />
   ```

3. **Calendar Integration** ✨ CRITICAL
   ```tsx
   <CalendarWidget 
     onDateSelect={handleDateSelect}
     availableSlots={availableSlots}
     appointmentType="lab" | "followup"
   />
   ```

4. **Real-time Section Updates** ✨ NEW
   ```tsx
   // Poll for section updates every 30 seconds
   useInterval(() => {
     checkSectionUpdates(docId, [3, 5, 6, 7]);
   }, 30000);
   ```

5. **Doctor Dashboard View** ✨ CRITICAL
   ```tsx
   // Separate dashboard for doctors
   <DoctorDashboard>
     <PendingApprovals /> {/* Stage 4 - Section 3 */}
     <LabResultsReview /> {/* Stage 6 - Section 5 */}
     <ConsultationNotes /> {/* Stage 7 - Section 6 */}
     <Prescriptions /> {/* Stage 11 - Section 7 */}
   </DoctorDashboard>
   ```

#### **Priority 2: Nice to Have**

1. **Notification System**
   - Toast notifications for stage completion
   - Browser push notifications
   - Email/SMS integration

2. **File Upload Progress**
   - Upload progress bar
   - Multiple file upload
   - Drag & drop zone

3. **Health Data Visualization**
   - Lab result charts
   - Trend analysis
   - Historical comparison

4. **Mobile Responsive**
   - Mobile-first design
   - Touch-optimized
   - Offline support

---

## 🔌 API Integration Points

### Base URL
```
http://localhost:8000
```

### Authentication
```typescript
headers: {
  'Authorization': `Bearer ${access_token}`,
  'Content-Type': 'application/json'
}
```

### Key Endpoints

#### **Workflow Chat API**
```typescript
// Send message to AI agent
POST /api/workflow/chat/message
Body: {
  message: string,
  user_id: string,
  user_role: "patient" | "doctor",
  workflow_id?: string
}
Response: {
  response: string,
  stage: number,
  stage_complete: boolean,
  next_stage?: number,
  workflow_doc_id?: string,
  workflow_doc_url?: string
}

// Get chat history
GET /api/agent/chat/history/{patient_id}
Response: {
  messages: Message[],
  current_stage: number
}
```

#### **Document API**
```typescript
// Get document section
GET /api/workflow/documents/{doc_id}/section/{section_number}
Response: {
  success: boolean,
  section_number: number,
  content: string,
  last_updated: string
}

// Update document section (Doctor only)
PUT /api/workflow/documents/{doc_id}/section/{section_number}
Body: {
  content: string,
  updated_by: string
}
```

#### **Calendar API**
```typescript
// Create appointment
POST /api/calendar/create-appointment
Body: {
  patient_id: string,
  appointment_type: "lab" | "consultation" | "followup",
  date: string,
  time: string,
  duration: number,
  tests?: string[]
}
Response: {
  success: boolean,
  calendar_event_id: string,
  event_link: string
}

// Get available slots
GET /api/calendar/available-slots?date={YYYY-MM-DD}&type={lab|consultation}
Response: {
  available_times: string[]
}
```

#### **Patient API**
```typescript
// Get patient details
GET /api/patients/{patient_id}
Response: {
  patient_id: string,
  name: string,
  email: string,
  phone: string,
  current_stage: number,
  workflow_doc_id?: string
}

// Search patients
POST /api/patients/search
Body: {
  query: string
}
Response: {
  patients: Patient[]
}
```

---

## ✅ Testing Checklist

### Pre-Testing Setup

- [ ] Backend server running (`http://localhost:8000`)
- [ ] Frontend server running (`http://localhost:3000`)
- [ ] Redis cache running
- [ ] PostgreSQL database connected
- [ ] Google Calendar API enabled
- [ ] Google Docs API enabled
- [ ] Credentials configured:
  - [ ] `client_secret.json` in `credentials/`
  - [ ] `calendar_token.pickle` in root
  - [ ] `docs_token.pickle` in `credentials/`

### Test Patient Setup

**Test Patient:**
- Email: `iamsamarth786@gmail.com`
- Phone: `7447444532`
- Patient ID: `PAT20251113001842`
- Document ID: `1kAgV4vOZkrrh2FZeKmQ2r8CDp9w2MG6KfZiKuSXw_pY`

### Complete End-to-End Test Flow

#### **Stage 1: Registration** ✅
- [ ] Login page loads
- [ ] Enter email and phone
- [ ] Click "Login"
- [ ] AI recognizes returning patient
- [ ] Loads existing profile
- [ ] Shows current stage

#### **Stage 2: Document Upload** ✅
- [ ] Skip option visible
- [ ] Click "Skip" or type "skip"
- [ ] Stage marked complete
- [ ] Advances to Stage 3

#### **Stage 3: Medical History** ✅
- [ ] AI asks for symptoms
- [ ] Enter: "I have fever, headache, and body pain for 3 days"
- [ ] AI asks follow-up questions
- [ ] Answer all questions
- [ ] Type "done" or "that's all"
- [ ] AI creates unified document
- [ ] Document link displayed
- [ ] Document shared with doctor email

#### **Stage 4: Doctor Approval** ✅
- [ ] AI shows "Waiting for doctor" message
- [ ] Document link clickable
- [ ] **[MANUAL]** Open document
- [ ] **[MANUAL]** Find Section 3
- [ ] **[MANUAL]** Add doctor's approval:
  ```
  ✅ TESTS APPROVED
  
  Recommended Tests:
  1. Complete Blood Count (CBC)
  2. Blood Glucose (Fasting)
  3. Lipid Profile
  ```
- [ ] **[MANUAL]** Save document
- [ ] Return to chat
- [ ] Type "Has the doctor approved?"
- [ ] AI confirms approval
- [ ] Tests list displayed

#### **Stage 5: Lab Scheduling** ✅
- [ ] AI offers to schedule appointment
- [ ] Calendar widget appears
- [ ] Select date and time
- [ ] Click "Confirm"
- [ ] Calendar event created
- [ ] Appointment details displayed
- [ ] Email confirmation received
- [ ] **[CHECK]** Section 4 updated in document

#### **Stage 6: Lab Results** ✅
- [ ] Type "Are my results ready?"
- [ ] AI shows "Waiting for lab results"
- [ ] **[MANUAL]** Open document
- [ ] **[MANUAL]** Find Section 5
- [ ] **[MANUAL]** Add lab results:
  ```
  📊 LAB TEST RESULTS
  Test Date: [Today's date]
  
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
  ```
- [ ] **[MANUAL]** Save document
- [ ] Return to chat
- [ ] Type "check"
- [ ] AI displays lab results
- [ ] Normal/Abnormal indicators shown
- [ ] AI provides analysis

#### **Stage 7: Doctor Consultation** ✅
- [ ] AI shows "Waiting for consultation"
- [ ] **[MANUAL]** Open document
- [ ] **[MANUAL]** Find Section 6
- [ ] **[MANUAL]** Add consultation notes:
  ```
  👨‍⚕️ DOCTOR'S CONSULTATION
  Date: [Today's date]
  
  DIAGNOSIS:
  Pre-diabetic condition detected. Blood glucose elevated.
  
  TREATMENT PLAN:
  1. Start Metformin 500mg
  2. Dietary modifications required
  3. Follow-up in 3 months
  
  NEXT STEPS:
  - Review prescription in next section
  - Schedule follow-up appointment
  ```
- [ ] **[MANUAL]** Save document
- [ ] Return to chat
- [ ] Type "What did the doctor say?"
- [ ] AI displays consultation summary
- [ ] Diagnosis shown
- [ ] Treatment plan shown

#### **Stage 11: Prescription & Follow-up** ✅
- [ ] **[MANUAL]** Open document
- [ ] **[MANUAL]** Find Section 7
- [ ] **[MANUAL]** Add prescription:
  ```
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
  📅 Suggested Date: [3 months from now]
  
  SAFETY MEASURES:
  ⚠️ Monitor blood sugar weekly
  ⚠️ Report any side effects immediately
  ```
- [ ] **[MANUAL]** Save document
- [ ] Return to chat
- [ ] Type "What is my prescription?"
- [ ] AI displays prescription
- [ ] Medications shown with dosage
- [ ] Dietary instructions listed
- [ ] Follow-up appointment scheduled
- [ ] Calendar event created
- [ ] **[CHECK]** Follow-up in Google Calendar

#### **Stage 12: Completion** ✅
- [ ] Type "Thank you"
- [ ] AI displays journey summary
- [ ] All stages listed with dates
- [ ] Final diagnosis shown
- [ ] Treatment plan summary
- [ ] Document link provided
- [ ] **[CHECK]** Section 8 updated in document
- [ ] Email summary received

### Frontend-Specific Tests

#### **Chatbot Interface**
- [ ] Messages load correctly
- [ ] New messages appear at bottom
- [ ] Auto-scroll works
- [ ] Typing indicator shows
- [ ] Quick action buttons work
- [ ] Timestamps display correctly
- [ ] Message history persists

#### **Calendar Integration**
- [ ] Calendar widget loads
- [ ] Available slots shown
- [ ] Date selection works
- [ ] Time selection works
- [ ] Appointment confirmation shows
- [ ] Calendar sync verified

#### **Document Viewer**
- [ ] Document link opens
- [ ] Sections visible
- [ ] Content readable
- [ ] Sharing permissions correct
- [ ] Doctor can edit
- [ ] Patient can view only

#### **Notifications**
- [ ] Toast notifications appear
- [ ] Stage completion alerts
- [ ] Appointment reminders
- [ ] Results ready notifications

#### **Mobile Responsiveness**
- [ ] Layout adapts to mobile
- [ ] Touch interactions work
- [ ] Scrolling smooth
- [ ] Buttons accessible

---

## 🎨 Known Features

### Implemented ✅

1. **Intelligent Patient Detection**
   - Auto-detects returning patients
   - Loads previous medical history
   - Smart search by name/phone/email

2. **Document Skip Option**
   - Returning patients can skip Stage 2
   - Automatic advancement to Stage 3
   - State properly saved

3. **Unified Document System** (Phase 2)
   - Single Google Doc for entire workflow
   - 8 sections for different stages
   - Bidirectional updates (AI ↔ Doctor)
   - Section reading functions with flexible markers

4. **Calendar Integration**
   - Automatic appointment creation
   - Google Calendar sync
   - Event ID tracking
   - Email invitations

5. **Lab Results Reading** (Phase 2 - NEW)
   - Reads from Section 5 (not Google Sheets)
   - Parses test results
   - Counts normal/abnormal
   - AI analysis extraction

6. **Prescription Parsing**
   - Medication extraction
   - Dosage and timing parsing
   - Dietary instructions
   - Follow-up date detection

7. **Stage Progress Tracking**
   - Current stage indicator
   - Stage completion flags
   - Next stage routing
   - Stage data persistence

8. **Flexible Section Markers**
   - Handles emoji headers (`👨‍⚕️ SECTION 3:`)
   - Multiple format support
   - Backward compatible

### Planned/In Development 🚧

1. **Real-time Notifications**
   - WebSocket integration
   - Push notifications
   - SMS alerts

2. **Advanced Analytics**
   - Health trends
   - Predictive insights
   - Risk assessment

3. **Multi-language Support**
   - English, Hindi, Spanish
   - Language auto-detection
   - Translation API

4. **Voice Input**
   - Speech-to-text
   - Voice commands
   - Audio messages

5. **Telemedicine Integration**
   - Video consultations
   - Screen sharing
   - Document collaboration

---

## 🔐 Credentials & Setup

### Required Credentials

#### **Google Cloud Console**
1. **Client Secret** (`credentials/client_secret.json`)
   ```json
   {
     "installed": {
       "client_id": "your-client-id",
       "project_id": "your-project",
       "auth_uri": "https://accounts.google.com/o/oauth2/auth",
       "token_uri": "https://oauth2.googleapis.com/token",
       "client_secret": "your-client-secret"
     }
   }
   ```

2. **Token Pickles** (Generated on first use)
   - `calendar_token.pickle` - Google Calendar API
   - `docs_token.pickle` - Google Docs API
   - `drive_token.pickle` - Google Drive API (optional)
   - `sheets_token.pickle` - Google Sheets API (optional)

#### **Environment Variables**

Create `.env` file:
```bash
# Database
DATABASE_URL=postgresql://user:password@localhost:5432/medical_ai
REDIS_HOST=localhost
REDIS_PORT=6379

# API Keys
GEMINI_API_KEY=your_gemini_api_key
GROQ_API_KEY=your_groq_api_key

# Google APIs
GOOGLE_CLIENT_ID=your_client_id
GOOGLE_CLIENT_SECRET=your_client_secret
DOCTOR_EMAIL=doctor@hospital.com

# Frontend
NEXT_PUBLIC_API_URL=http://localhost:8000
```

### Setup Steps

1. **Install Dependencies**
   ```bash
   # Backend
   cd backend
   pip install -r requirements.txt
   
   # Frontend
   cd frontend
   npm install
   ```

2. **Start Services**
   ```bash
   # Start Redis
   redis-server
   
   # Start PostgreSQL
   # (Ensure PostgreSQL is running)
   
   # Start Backend
   python main.py
   
   # Start Frontend
   cd frontend
   npm run dev
   ```

3. **Initial OAuth Flow**
   - First API call will open browser
   - Login with Google account
   - Grant permissions
   - Token saved automatically

4. **Test Credentials**
   ```bash
   python check_credentials.py
   ```

---

## 🚀 Testing Tomorrow - Action Items

### Before Testing

1. **Verify All Services Running**
   - [ ] Backend API (`localhost:8000`)
   - [ ] Frontend (`localhost:3000`)
   - [ ] Redis
   - [ ] PostgreSQL

2. **Reset Test Patient State**
   ```bash
   python reset_patient_state.py
   ```

3. **Prepare Test Document**
   - [ ] Open document: https://docs.google.com/document/d/1kAgV4vOZkrrh2FZeKmQ2r8CDp9w2MG6KfZiKuSXw_pY/edit
   - [ ] Clear all sections (or create new one)
   - [ ] Keep it open in separate tab

4. **Setup Doctor Email**
   - [ ] Configure `DOCTOR_EMAIL` in `.env`
   - [ ] Ensure doctor has document access

### During Testing

1. **Keep These Open**
   - Frontend (patient view)
   - Backend logs (terminal)
   - Google Document (doctor actions)
   - Google Calendar

2. **Test in Order**
   - Follow testing checklist sequentially
   - Don't skip stages
   - Document any issues

3. **Record Results**
   - Screenshots of each stage
   - Note any errors
   - Time each stage completion

4. **Monitor APIs**
   - Check network tab
   - Verify API responses
   - Note any failed requests

### After Testing

1. **Document Issues**
   - Create issue list
   - Categorize by priority
   - Include reproduction steps

2. **Improvement Ideas**
   - Note UX improvements
   - Suggest feature enhancements
   - Identify bottlenecks

3. **Next Steps**
   - Plan fixes
   - Prioritize improvements
   - Schedule next test

---

## 📞 Support & Contact

**Documentation:** This file  
**Test Script:** `test_complete_end_to_end_workflow.py`  
**Credentials Checker:** `check_credentials.py`  
**State Reset:** `reset_patient_state.py`

---

## 🎯 Success Criteria for Tomorrow's Test

✅ **Must Work:**
1. Patient login and recognition
2. Medical history collection
3. Document creation and sharing
4. Calendar appointment creation
5. Section reading (3, 5, 6, 7)
6. End-to-end flow completion

✅ **Should Work:**
1. Real-time stage updates
2. Proper error handling
3. Smooth user experience
4. Calendar sync

✅ **Nice to Have:**
1. Push notifications
2. Mobile responsiveness
3. Advanced analytics

---

**Last Updated:** November 14, 2025  
**Version:** 2.0 (Phase 2 Complete)  
**Status:** ✅ Ready for Testing

**Good luck with tomorrow's end-to-end test! 🚀**
