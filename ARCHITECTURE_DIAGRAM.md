# 🏗️ Complete Architecture Diagram

## Technology Stack Overview

```
┌─────────────────────────────────────────────────────────────────────────┐
│                         👤 PATIENT (END USER)                           │
│                    Browser (Chrome, Firefox, Edge)                      │
└────────────────────────────────┬────────────────────────────────────────┘
                                 │ HTTPS
                                 ▼
┌─────────────────────────────────────────────────────────────────────────┐
│                         🎨 FRONTEND LAYER                               │
│                                                                         │
│  ┌──────────────────────────────────────────────────────────────────┐  │
│  │                     Next.js 14 + React 18                        │  │
│  │  • TypeScript                                                    │  │
│  │  • Tailwind CSS + Shadcn/ui                                      │  │
│  │  • React Query (TanStack)                                        │  │
│  │  • Axios for HTTP                                                │  │
│  │                                                                  │  │
│  │  Pages:                                                          │  │
│  │  ├─ /loginPage - Authentication                                 │  │
│  │  ├─ /patient/dashboard - Overview                               │  │
│  │  ├─ /patient/chatbot - AI Chat (Main Interface) ⭐              │  │
│  │  ├─ /patient/appointments - Calendar                            │  │
│  │  ├─ /patient/labs - Lab Results                                 │  │
│  │  ├─ /patient/medications - Prescriptions                        │  │
│  │  ├─ /patient/records - Medical Records                          │  │
│  │  └─ /patient/billing - Invoices                                 │  │
│  └──────────────────────────────────────────────────────────────────┘  │
│                                                                         │
│  Running on: http://localhost:3000                                     │
└────────────────────────────────┬────────────────────────────────────────┘
                                 │ REST API (JSON)
                                 ▼
┌─────────────────────────────────────────────────────────────────────────┐
│                         ⚙️ BACKEND LAYER                                │
│                                                                         │
│  ┌──────────────────────────────────────────────────────────────────┐  │
│  │                      FastAPI (Python)                            │  │
│  │  • Async/await support                                           │  │
│  │  • JWT authentication                                            │  │
│  │  • CORS enabled                                                  │  │
│  │                                                                  │  │
│  │  Endpoints:                                                      │  │
│  │  ├─ POST /api/workflow/chat/message - AI Chat ⭐                │  │
│  │  ├─ GET /api/agent/chat/history/{patient_id}                    │  │
│  │  ├─ GET /api/patients/{patient_id}                              │  │
│  │  ├─ POST /api/patients/search                                   │  │
│  │  ├─ POST /api/calendar/create-appointment                       │  │
│  │  ├─ GET /api/workflow/documents/{doc_id}/section/{num}          │  │
│  │  └─ PUT /api/workflow/documents/{doc_id}/section/{num}          │  │
│  └──────────────────────────────────────────────────────────────────┘  │
│                                                                         │
│  ┌──────────────────────────────────────────────────────────────────┐  │
│  │             WorkflowChatAgent (7508 lines)                       │  │
│  │  • LangChain-based AI orchestration                              │  │
│  │  • 12 stage handlers                                             │  │
│  │  • Tool-based architecture                                       │  │
│  │  • State management                                              │  │
│  │  • Context-aware Q&A                                             │  │
│  └──────────────────────────────────────────────────────────────────┘  │
│                                                                         │
│  Running on: http://localhost:8000                                     │
└─────┬─────────────┬──────────────┬──────────────┬─────────────┬────────┘
      │             │              │              │             │
      ▼             ▼              ▼              ▼             ▼
┌──────────┐  ┌──────────┐  ┌──────────┐  ┌──────────┐  ┌──────────┐
│ AI/LLM   │  │ Google   │  │Database  │  │  Cache   │  │Messaging │
│ Layer    │  │Workspace │  │  Layer   │  │  Layer   │  │  Layer   │
└──────────┘  └──────────┘  └──────────┘  └──────────┘  └──────────┘
```

---

## 🤖 AI/LLM Layer

```
┌─────────────────────────────────────────────────────────────┐
│                      LangChain Framework                    │
│                                                             │
│  ┌─────────────────────────┐  ┌──────────────────────────┐ │
│  │  Google Gemini Pro 1.5  │  │  Groq (Llama 3)          │ │
│  │  • Primary LLM          │  │  • Backup LLM            │ │
│  │  • Conversation         │  │  • Fast responses        │ │
│  │  • Analysis             │  │  • Alternative model     │ │
│  └─────────────────────────┘  └──────────────────────────┘ │
│                                                             │
│  Agent Tools:                                               │
│  ├─ SearchPatientTool                                       │
│  ├─ CreatePatientRecordTool                                 │
│  ├─ CreateAppointmentTool                                   │
│  ├─ SendEmailTool                                           │
│  ├─ SendSMSTool                                             │
│  └─ ContextAwareQATool                                      │
└─────────────────────────────────────────────────────────────┘
```

---

## 📁 Google Workspace Integration

```
┌───────────────────────────────────────────────────────────────────┐
│                    Google Cloud Platform                          │
│                                                                   │
│  ┌────────────────────┐  ┌────────────────────┐                  │
│  │   Google Docs API  │  │ Google Calendar    │                  │
│  │                    │  │       API          │                  │
│  │  • Create docs     │  │  • Create events   │                  │
│  │  • Read sections   │  │  • Update events   │                  │
│  │  • Update sections │  │  • Delete events   │                  │
│  │  • Share docs      │  │  • Send invites    │                  │
│  │                    │  │                    │                  │
│  │  Used in:          │  │  Used in:          │                  │
│  │  ✅ Stage 3 (Create)│  │  ✅ Stage 5 (Lab)  │                  │
│  │  ✅ Stage 4 (Read)  │  │  ✅ Stage 11       │                  │
│  │  ✅ Stage 5 (Update)│  │     (Follow-up)    │                  │
│  │  ✅ Stage 6 (Read)  │  │                    │                  │
│  │  ✅ Stage 7 (Read)  │  │  Token:            │                  │
│  │  ✅ Stage 11 (Read) │  │  📄 calendar_      │                  │
│  │  ✅ Stage 12        │  │     token.pickle   │                  │
│  │     (Update)        │  │                    │                  │
│  │                    │  │                    │                  │
│  │  Token:            │  │                    │                  │
│  │  📄 docs_token.    │  │                    │                  │
│  │     pickle         │  │                    │                  │
│  └────────────────────┘  └────────────────────┘                  │
│                                                                   │
│  ┌────────────────────┐  ┌────────────────────┐                  │
│  │  Google Drive API  │  │ Google Sheets API  │                  │
│  │                    │  │  (Optional/Legacy) │                  │
│  │  • Upload files    │  │                    │                  │
│  │  • Share files     │  │  • Patient tracking│                  │
│  │  • Organize files  │  │  • Lab monitoring  │                  │
│  │                    │  │    (Phase 1 only)  │                  │
│  │  Used in:          │  │                    │                  │
│  │  ✅ Stage 2 (Upload)│  │  ⚠️ Not used in   │                  │
│  │                    │  │     Phase 2        │                  │
│  │  Token:            │  │                    │                  │
│  │  📄 drive_token.   │  │  Token:            │                  │
│  │     pickle         │  │  📄 sheets_token.  │                  │
│  │                    │  │     pickle         │                  │
│  └────────────────────┘  └────────────────────┘                  │
│                                                                   │
│  Auth: OAuth 2.0                                                  │
│  Config: credentials/client_secret.json                           │
└───────────────────────────────────────────────────────────────────┘
```

### **Unified Document Structure (Phase 2):**

```
📄 SINGLE GOOGLE DOC (8 Sections)

┌─────────────────────────────────────────────────┐
│ SECTION 1: Patient Information (AI writes)     │
│ • Name, Age, Contact                            │
│ • Visit Date                                    │
│ • Chief Complaint                               │
├─────────────────────────────────────────────────┤
│ SECTION 2: Medical History & AI Analysis       │
│            (AI writes)                          │
│ • Symptoms                                      │
│ • Chronic Conditions                            │
│ • Medications                                   │
│ • AI Assessment                                 │
├─────────────────────────────────────────────────┤
│ SECTION 3: Doctor's Decision (Doctor updates)  │ ⬅ READ
│ • Tests Approved: Yes/No                        │
│ • Recommended Tests                             │
│ • Special Instructions                          │
├─────────────────────────────────────────────────┤
│ SECTION 4: Lab Test Scheduling (AI writes)     │
│ • Scheduled Tests                               │
│ • Appointment Date/Time                         │
│ • Location                                      │
│ • Calendar Event ID                             │
├─────────────────────────────────────────────────┤
│ SECTION 5: Lab Results (Lab staff updates)     │ ⬅ READ
│ • Test Results                                  │
│ • Normal/Abnormal Status                        │
│ • AI Analysis                                   │
├─────────────────────────────────────────────────┤
│ SECTION 6: Post-Lab Consultation               │ ⬅ READ
│            (Doctor updates)                     │
│ • Diagnosis                                     │
│ • Treatment Plan                                │
│ • Next Steps                                    │
├─────────────────────────────────────────────────┤
│ SECTION 7: Prescription & Follow-up            │ ⬅ READ
│            (Doctor updates)                     │
│ • Medications                                   │
│ • Dosage & Duration                             │
│ • Dietary Instructions                          │
│ • Follow-up Date                                │
├─────────────────────────────────────────────────┤
│ SECTION 8: Workflow Completion (AI writes)     │
│ • Journey Timeline                              │
│ • Final Diagnosis                               │
│ • Complete Treatment Plan                       │
└─────────────────────────────────────────────────┘

Created in: Stage 3
Updated by: AI (1,2,4,5,8) | Doctor (3,6,7) | Lab (5)
Read by: AI (3,5,6,7)
```

---

## 💾 Database Layer

```
┌───────────────────────────────────────────────────────────┐
│                     PostgreSQL                            │
│                 Relational Database                       │
│                                                           │
│  Tables:                                                  │
│  ┌───────────────────────────────────────────────────┐   │
│  │ patients                                          │   │
│  │ ├─ patient_id (PK)                                │   │
│  │ ├─ email (UNIQUE)                                 │   │
│  │ ├─ phone                                          │   │
│  │ ├─ name                                           │   │
│  │ ├─ date_of_birth                                  │   │
│  │ └─ ...                                            │   │
│  └───────────────────────────────────────────────────┘   │
│                                                           │
│  ┌───────────────────────────────────────────────────┐   │
│  │ medical_records                                   │   │
│  │ ├─ record_id (PK)                                 │   │
│  │ ├─ patient_id (FK)                                │   │
│  │ ├─ symptoms                                       │   │
│  │ ├─ diagnosis                                      │   │
│  │ ├─ workflow_doc_id                                │   │
│  │ └─ workflow_doc_url                               │   │
│  └───────────────────────────────────────────────────┘   │
│                                                           │
│  ┌───────────────────────────────────────────────────┐   │
│  │ appointments                                      │   │
│  │ ├─ appointment_id (PK)                            │   │
│  │ ├─ patient_id (FK)                                │   │
│  │ ├─ appointment_type                               │   │
│  │ ├─ appointment_date                               │   │
│  │ ├─ calendar_event_id                              │   │
│  │ └─ status                                         │   │
│  └───────────────────────────────────────────────────┘   │
│                                                           │
│  ┌───────────────────────────────────────────────────┐   │
│  │ lab_results                                       │   │
│  │ ├─ result_id (PK)                                 │   │
│  │ ├─ patient_id (FK)                                │   │
│  │ ├─ test_name                                      │   │
│  │ ├─ result_value                                   │   │
│  │ ├─ status (NORMAL/ABNORMAL)                       │   │
│  │ └─ test_date                                      │   │
│  └───────────────────────────────────────────────────┘   │
│                                                           │
│  ┌───────────────────────────────────────────────────┐   │
│  │ prescriptions                                     │   │
│  │ ├─ prescription_id (PK)                           │   │
│  │ ├─ patient_id (FK)                                │   │
│  │ ├─ medication_name                                │   │
│  │ ├─ dosage                                         │   │
│  │ ├─ frequency                                      │   │
│  │ └─ status                                         │   │
│  └───────────────────────────────────────────────────┘   │
│                                                           │
│  + doctor_notes, workflow_states, etc.                   │
│                                                           │
│  Connection: SQLAlchemy ORM                               │
└───────────────────────────────────────────────────────────┘
```

---

## 🗄️ Cache Layer

```
┌───────────────────────────────────────────────────────────┐
│                        Redis                              │
│                   In-Memory Cache                         │
│                                                           │
│  Usage:                                                   │
│  ┌─────────────────────────────────────────────────────┐ │
│  │ Patient State Caching                               │ │
│  │ Key: workflow_state:{patient_email}                 │ │
│  │ Value: {                                            │ │
│  │   current_stage: 5,                                 │ │
│  │   stage_name: "lab_coordination",                   │ │
│  │   stage_data: {...},                                │ │
│  │   workflow_doc_id: "...",                           │ │
│  │   conversation_history: [...]                       │ │
│  │ }                                                   │ │
│  └─────────────────────────────────────────────────────┘ │
│                                                           │
│  ┌─────────────────────────────────────────────────────┐ │
│  │ Session Management                                  │ │
│  │ Key: session:{session_id}                           │ │
│  │ Value: { user_id, token, expires_at }              │ │
│  └─────────────────────────────────────────────────────┘ │
│                                                           │
│  ┌─────────────────────────────────────────────────────┐ │
│  │ Rate Limiting                                       │ │
│  │ Key: rate_limit:{user_id}:{endpoint}                │ │
│  │ Value: request_count                                │ │
│  │ TTL: 60 seconds                                     │ │
│  └─────────────────────────────────────────────────────┘ │
│                                                           │
│  ┌─────────────────────────────────────────────────────┐ │
│  │ Real-time Data Cache                                │ │
│  │ • Appointment slots                                 │ │
│  │ • Lab result notifications                          │ │
│  │ • Document update flags                             │ │
│  └─────────────────────────────────────────────────────┘ │
│                                                           │
│  Port: 6379                                               │
│  DB: 0                                                    │
└───────────────────────────────────────────────────────────┘
```

---

## 📱 Messaging Layer

```
┌─────────────────────────────────────────────────────────────┐
│                    Twilio (SMS & WhatsApp)                  │
│                                                             │
│  ┌─────────────────────────────────────────────────────┐   │
│  │ SMS Messages                                        │   │
│  │ • Appointment confirmations                         │   │
│  │ • Lab result notifications                          │   │
│  │ • Prescription reminders                            │   │
│  │ • OTP verification                                  │   │
│  │                                                     │   │
│  │ Number: +1234567890 (configured)                    │   │
│  └─────────────────────────────────────────────────────┘   │
│                                                             │
│  ┌─────────────────────────────────────────────────────┐   │
│  │ WhatsApp Messages                                   │   │
│  │ • Rich formatted messages                           │   │
│  │ • Document links                                    │   │
│  │ • Appointment reminders                             │   │
│  │                                                     │   │
│  │ Number: whatsapp:+1234567890                        │   │
│  └─────────────────────────────────────────────────────┘   │
│                                                             │
│  Credentials: TWILIO_ACCOUNT_SID, TWILIO_AUTH_TOKEN        │
└─────────────────────────────────────────────────────────────┘

┌─────────────────────────────────────────────────────────────┐
│                      Gmail API (Email)                      │
│                                                             │
│  Email Types:                                               │
│  ├─ Appointment confirmations                               │
│  ├─ Lab result notifications                                │
│  ├─ Prescription emails                                     │
│  ├─ Journey completion summary                              │
│  └─ Emergency alerts                                        │
│                                                             │
│  SMTP Config: smtp.gmail.com:587                            │
└─────────────────────────────────────────────────────────────┘
```

---

## 🔐 Security & Authentication

```
┌─────────────────────────────────────────────────────────────┐
│                  Authentication Flow                        │
│                                                             │
│  Frontend:                                                  │
│  ┌──────────────────────────────────────────────────────┐  │
│  │ 1. User enters email/phone                           │  │
│  │ 2. POST /api/auth/login                              │  │
│  │ 3. Receive JWT token                                 │  │
│  │ 4. Store in localStorage                             │  │
│  │ 5. Include in Authorization header                   │  │
│  └──────────────────────────────────────────────────────┘  │
│                                                             │
│  Backend:                                                   │
│  ┌──────────────────────────────────────────────────────┐  │
│  │ 1. Validate JWT token                                │  │
│  │ 2. Extract user_id                                   │  │
│  │ 3. Load patient state from Redis/DB                  │  │
│  │ 4. Process request                                   │  │
│  │ 5. Update state                                      │  │
│  └──────────────────────────────────────────────────────┘  │
│                                                             │
│  OAuth 2.0 (Google):                                        │
│  ┌──────────────────────────────────────────────────────┐  │
│  │ Used for: Google Workspace APIs                      │  │
│  │ Flow: Authorization Code                             │  │
│  │ Tokens: Stored in .pickle files                      │  │
│  │ Refresh: Automatic when expired                      │  │
│  └──────────────────────────────────────────────────────┘  │
└─────────────────────────────────────────────────────────────┘
```

---

## 📊 Data Flow Example (Stage 5: Lab Scheduling)

```
┌──────────┐
│  User    │ "I want to schedule the lab tests"
└────┬─────┘
     │ HTTP POST
     ▼
┌──────────────────────────────────────────────────┐
│  Frontend: /patient/chatbot                      │
│  • Send message to backend                       │
│  • Display loading state                         │
└────┬─────────────────────────────────────────────┘
     │ POST /api/workflow/chat/message
     ▼
┌──────────────────────────────────────────────────┐
│  Backend: FastAPI                                │
│  • Receive message                               │
│  • Load patient state from Redis                 │
└────┬─────────────────────────────────────────────┘
     │
     ▼
┌──────────────────────────────────────────────────┐
│  WorkflowChatAgent                               │
│  • Route to Stage 5 handler                      │
│  • _handle_lab_coordination()                    │
└────┬─────────────────────────────────────────────┘
     │
     ├──────────────────────────────────┐
     │                                  │
     ▼                                  ▼
┌────────────────────┐      ┌────────────────────┐
│ CreateAppointment  │      │ Google Calendar    │
│ Tool               │─────→│ API                │
│                    │      │                    │
│ • Create event     │      │ • Event created    │
│ • Get event_id     │←─────│ • Return event_id  │
└────────┬───────────┘      └────────────────────┘
         │
         ▼
┌──────────────────────────────────────────────────┐
│  update_doc_section()                            │
│  • Write to Section 4                            │
│  • Include calendar event_id                     │
└────┬─────────────────────────────────────────────┘
     │
     ├──────────────────────────────────┐
     │                                  │
     ▼                                  ▼
┌────────────────────┐      ┌────────────────────┐
│  PostgreSQL        │      │  Redis             │
│  • Save appointment│      │  • Update state    │
│  • Store event_id  │      │  • Cache event     │
└────────────────────┘      └────────────────────┘
     │
     ├──────────────────────┐
     │                      │
     ▼                      ▼
┌────────────────┐   ┌────────────────┐
│  Twilio SMS    │   │  Gmail Email   │
│  • Send conf.  │   │  • Send conf.  │
└────────────────┘   └────────────────┘
     │
     ▼
┌──────────────────────────────────────────────────┐
│  Backend: Return Response                        │
│  {                                               │
│    response: "Appointment scheduled!",           │
│    stage: 5,                                     │
│    stage_complete: true,                         │
│    next_stage: 6                                 │
│  }                                               │
└────┬─────────────────────────────────────────────┘
     │ JSON Response
     ▼
┌──────────────────────────────────────────────────┐
│  Frontend: Update UI                             │
│  • Display success message                       │
│  • Show calendar event                           │
│  • Update stage progress                         │
│  • Show appointment details                      │
└──────────────────────────────────────────────────┘
     │
     ▼
┌──────────┐
│  User    │ Sees confirmation + calendar event
└──────────┘
```

---

**This architecture supports the entire workflow from registration to completion!** 🚀

**Total Components:** 15+ services working together seamlessly
