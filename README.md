# 🏥 AI-Powered Hospital Management & Patient Workflow Automation System

[![FastAPI](https://img.shields.io/badge/FastAPI-0.104.1-009688.svg?style=flat&logo=FastAPI&logoColor=white)](https://fastapi.tiangolo.com)
[![Next.js](https://img.shields.io/badge/Next.js-15.5-black.svg?style=flat&logo=next.js&logoColor=white)](https://nextjs.org/)
[![React](https://img.shields.io/badge/React-19.1-61DAFB.svg?style=flat&logo=react&logoColor=black)](https://react.dev/)
[![LangChain](https://img.shields.io/badge/LangChain-LangGraph-1C3C3C.svg?style=flat&logo=langchain&logoColor=white)](https://langchain.com/)
[![Google Cloud](https://img.shields.io/badge/Google_Cloud-Workspace_APIs-4285F4.svg?style=flat&logo=googlecloud&logoColor=white)](https://cloud.google.com/)
[![PostgreSQL](https://img.shields.io/badge/PostgreSQL-16-336791.svg?style=flat&logo=postgresql&logoColor=white)](https://www.postgresql.org/)
[![Redis](https://img.shields.io/badge/Redis-Cache-DC382D.svg?style=flat&logo=redis&logoColor=white)](https://redis.io/)
[![ChromaDB](https://img.shields.io/badge/ChromaDB-Vector_Store-FF6F00.svg?style=flat)](https://www.trychroma.com/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

An enterprise-grade, proactive, autonomous, and human-in-the-loop (HITL) AI hospital operating system. It orchestrates end-to-end patient care journeys across 12 distinct stages—from registration, document verification, and AI-assisted symptom triage to bidirectional doctor reviews, automated lab scheduling, real-time result monitoring, prescription PDF generation, and discharge planning.

Deeply integrated with **Google Workspace (Drive, Docs, Sheets, Calendar, Gmail)**, **Twilio (SMS/WhatsApp)**, **ChromaDB Vector RAG**, **PostgreSQL**, and **Redis**, backed by a modern **Next.js 15 & React 19** clinical dashboard.

---

## 📑 Table of Contents

- [Key Features & Highlights](#-key-features--highlights)
- [System Architecture](#-system-architecture)
- [12-Stage Patient Journey Workflow](#-12-stage-patient-journey-workflow)
- [Agentic HITL Approval System](#-agentic-hitl-approval-system)
- [Google Workspace Deep Integration](#-google-workspace-deep-integration)
- [Tech Stack](#-tech-stack)
- [Repository Structure](#-repository-structure)
- [Getting Started](#-getting-started)
  - [Prerequisites](#prerequisites)
  - [Environment Configuration](#environment-configuration)
  - [Google Workspace & OAuth Setup](#google-workspace--oauth-setup)
  - [Database & Cache Setup](#database--cache-setup)
  - [Backend Setup (FastAPI)](#backend-setup-fastapi)
  - [Frontend Setup (Next.js)](#frontend-setup-nextjs)
- [API Reference](#-api-reference)
- [Security & Compliance](#-security--compliance)
- [Contributing](#-contributing)
- [License](#-license)

---

## ✨ Key Features & Highlights

- **Autonomous 12-Stage Workflow Orchestration**: Guides patients and staff through an end-to-end clinical journey, adapting dynamically to doctor decisions and diagnostic outcomes.
- **Human-in-the-Loop (HITL) Doctor Collaboration**: Bidirectional communication where doctors review AI recommendations directly via Google Sheets/Docs, and the agent adapts the care pathway accordingly.
- **RAG-Powered Medical History & Memory**: Utilizes **ChromaDB** vector database to index symptoms, past medical history, and clinical diagnoses for contextual recall during subsequent visits.
- **Google Workspace as a Clinical Infrastructure**:
  - **Drive**: Auto-provisions 5 isolated folders per patient for HIPAA-compliant organization.
  - **Docs**: Generates and continuously updates live collaborative clinical notes.
  - **Sheets**: Real-time lab dashboards and doctor approval workbenches.
  - **Calendar**: Automatically reserves lab slots, physician consultations, and follow-ups.
  - **Gmail**: Sends instant confirmation emails and report dispatches.
- **Automated Prescription PDF Engine**: Generates professional, branded medical prescriptions using ReportLab, auto-uploads them to patient Drive folders, and notifies the patient.
- **Returning Patient Detection**: Recognizes existing phone/email identities to skip redundant intake forms and reload medical history seamlessly.
- **Dual Database Architecture**: Combines PostgreSQL for relational ACID state persistence with Redis for real-time caching and sub-millisecond session resume.
- **Modern Clinical Web UI**: Built with Next.js 15 App Router, React 19, Tailwind CSS, Radix UI, TanStack Query, and Zustand.

---

## 🏗️ System Architecture

```
                                  ┌───────────────────────────────┐
                                  │      Next.js 15 Frontend      │
                                  │   (Patient & Staff Portals)   │
                                  └───────────────┬───────────────┘
                                                  │ REST / WebSocket
                                                  ▼
                                  ┌───────────────────────────────┐
                                  │        FastAPI Backend        │
                                  │  (OAuth2, Routers, Security)  │
                                  └───────────────┬───────────────┘
                                                  │
                 ┌────────────────────────────────┼────────────────────────────────┐
                 ▼                                ▼                                ▼
    ┌─────────────────────────┐      ┌─────────────────────────┐      ┌─────────────────────────┐
    │    LangGraph & Agent    │      │    ChromaDB Vector DB   │      │ Dual Database & Storage │
    │ 110+ Hospital Tools     │◄────►│   (Semantic History,    │◄────►│  PostgreSQL (Relational)│
    │ 3-Tier HITL Approvals   │      │    RAG Medical Memory)  │      │  Redis (Fast State Sync)│
    └────────────┬────────────┘      └─────────────────────────┘      └─────────────────────────┘
                 │
                 ├───────────────────────────────┬───────────────────────────────┐
                 ▼                               ▼                               ▼
    ┌─────────────────────────┐     ┌─────────────────────────┐     ┌─────────────────────────┐
    │    Google Workspace     │     │      Communication      │     │    Billing & Reports    │
    │ • Drive (5 Folders/Pt)  │     │ • Twilio SMS            │     │ • ReportLab PDF Prescr. │
    │ • Docs (Live Notes)     │     │ • Twilio WhatsApp       │     │ • Google Sheets Billing │
    │ • Sheets (Lab Queue)    │     │ • Gmail Notifications   │     │ • Razorpay Integration  │
    │ • Calendar (3 Events)   │     │                         │     │                         │
    └─────────────────────────┘     └─────────────────────────┘     └─────────────────────────┘
```

---

## 🔄 12-Stage Patient Journey Workflow

| Stage | Name | Description | Calendar Event | Artifacts Generated |
| :---: | :--- | :--- | :---: | :--- |
| **1** | **Patient Registration** | Captures demographics, issues Patient ID, provisions 5 Drive folders, creates live Doc & Sheet. | — | 5 Google Drive folders, Patient Doc, Lab Sheet |
| **2** | **Document Upload** | Enforces mandatory identity proof verification (Aadhaar/PAN/ID) and stores files securely. | — | Verified documents in Drive |
| **3** | **Medical History & Triage** | Ingests symptoms and chronic history; AI recommends targeted lab investigations; indexes in ChromaDB. | — | Doctor Review Sheet, Vector Embeddings |
| **4** | **Test Determination (HITL)** | Doctor reviews AI recommendations via Google Sheet and approves, rejects, or amends tests. | — | Approved Diagnostic Order |
| **5** | **Lab Appointment** | Selects convenient timeslot, provisions Google Calendar event, and shares lab upload folder. | 📅 Lab Booking | Calendar Event, Email Confirmation |
| **6** | **Lab Results Analysis** | Real-time polling detects lab uploads, AI checks normal ranges, flags anomalies, and books doctor review. | 📅 Doctor Meeting | Analyzed Lab Findings, Calendar Event |
| **7** | **Doctor Consultation** | Doctor consults patient and decides: **Option A (Admission/Surgery)** or **Option B (Outpatient/Prescription)**. | — | Treatment Decision in Live Doc |
| **8** | **Admission Planning** | *(If admitted)* Room allocation (General/Semi-Private/ICU), insurance verification, and bed reservation. | — | Admission Clearance Sheet |
| **9** | **Pre-Op Assessment** | *(If surgical)* Pre-anesthesia checkup (PAC), surgical consent verification, and pre-op vitals clearance. | — | Surgical Clearance Record |
| **10**| **Procedure Scheduling** | *(If surgical)* Operation Theater (OT) booking, surgical team allocation, and prep instructions. | — | Confirmed Surgery Schedule |
| **11**| **Post-Treatment & Rx** | AI parses doctor instructions, generates high-res prescription PDF, uploads to Drive, books follow-up. | 📅 Follow-up Appt | Auto-Generated Prescription PDF |
| **12**| **Discharge & Summary** | Compiles comprehensive discharge summary with home care, medications, and final billing records. | — | Final Discharge Summary PDF |

---

## 🛡️ Agentic HITL Approval System

To maintain patient safety and clinical integrity, the system implements a **3-Tier Execution Framework**:

- **Tier 1: Auto-Execute (Safe & Routine)**
  - Appointment reminders, automated inventory checks, routine wellness updates, system metric logging.
- **Tier 2: Request Approval (Staff / Nurse Review)**
  - Diagnostic test ordering, outpatient appointment scheduling, non-critical record amendments.
- **Tier 3: Admin Authorization (Physician / Clinical Authority)**
  - Surgery cancellations, dosage modifications, prescription sign-offs, inpatient admissions, patient record deletion.

---

## 📂 Google Workspace Deep Integration

Every registered patient receives an automated, organized folder tree inside Google Drive:

```
Hospital_AI_Patient_Documents/
└── PAT202511180001_John_Doe/
    ├── 1_Medical_History/         # Past clinical documents, discharge papers
    ├── 2_Essential_Documents/     # Mandatory Government ID (Aadhaar/PAN), Insurance
    ├── 3_Lab_Reports/             # Diagnostic reports, Blood tests, Imaging
    ├── 4_Prescriptions/           # Auto-generated Prescription PDFs
    └── 5_Consultation_Notes/      # Doctor notes and clinical evaluation summaries
```

---

## 💻 Tech Stack

### Backend & AI
- **Framework**: FastAPI (Python 3.11 / 3.12)
- **Agent Orchestration**: LangChain, LangGraph
- **LLM / Foundation Models**: Google Gemini Pro / Flash (`langchain-google-genai`)
- **Vector Database (RAG)**: ChromaDB, Sentence-Transformers
- **PDF Generation**: ReportLab
- **Security**: OAuth2 with JWT (`python-jose`), bcrypt password hashing

### Frontend
- **Framework**: Next.js 15 (Turbopack, App Router)
- **UI & Components**: React 19, Tailwind CSS v4, Radix UI / Shadcn UI
- **State Management & Data Fetching**: Zustand, TanStack React Query v5
- **Icons & Visuals**: Lucide React, Recharts

### Infrastructure & External Services
- **Databases**: PostgreSQL (SQLAlchemy, Alembic), Redis (Session cache & state persistence)
- **Workspace Integrations**: Google Drive API, Google Docs API, Google Sheets API, Google Calendar API, Gmail API
- **Telephony & Messaging**: Twilio (SMS & WhatsApp Business API)
- **Payments**: Razorpay API

---

## 📁 Repository Structure

```
├── api/                        # FastAPI routers & endpoints
│   ├── ai_chat_router.py       # Conversational workflow chat agent endpoint
│   ├── auth.py                 # JWT token utilities & password verification
│   ├── auth_router.py          # User authentication endpoints (login, register)
│   └── patients_router.py      # Patient management & query endpoints
├── src/                        # Core AI agent & business logic
│   ├── conversational_agent.py # Natural language conversation handling
│   ├── llm.py                  # LLM initialization & prompt factories
│   ├── medical_data_handler.py # Clinical extraction & schema formatting
│   ├── workflow_chat_agent.py  # 12-stage state machine & tool orchestrator
│   └── workflow_state.py       # Pydantic state representations
├── tools/                      # 110+ specialized agent tools
│   ├── appointment_tool.py     # Appointment booking & scheduling
│   ├── billing_sheets_tool.py  # Billing records synchronization
│   ├── google_calendar_tool.py # Google Calendar event creation & management
│   ├── google_docs_tool.py     # Live Google Doc clinical notes management
│   ├── google_drive_tool.py    # Patient folder creation & upload verification
│   ├── google_sheets_tool.py   # Lab result tracking & doctor review sheets
│   ├── gmail_tool.py           # Automated email dispatch
│   ├── lab_management_tool.py  # Diagnostic test workflows
│   ├── pharmacy_tool.py        # Medication inventory & tracking
│   ├── twilio_tool.py          # SMS & WhatsApp notifications
│   └── unified_workflow_doc_tool.py # Comprehensive document synchronization
├── database/                   # Database models & cache layers
│   ├── db_manager.py           # PostgreSQL database manager & models
│   ├── redis_cache.py          # Redis state caching & session recovery
│   └── schema.sql              # Relational database schema definitions
├── frontend/                   # Next.js 15 clinical frontend application
│   ├── src/
│   │   ├── app/                # Next.js App Router (pages & layouts)
│   │   ├── components/         # Reusable UI & workflow widgets
│   │   ├── hooks/              # Custom React hooks
│   │   ├── lib/                # Utility helpers & API client
│   │   └── store/              # Zustand state management stores
│   ├── package.json            # Node.js dependencies
│   └── tailwind.config.ts      # Tailwind CSS styling configuration
├── credentials/                # OAuth client credentials (gitignored)
│   ├── .gitkeep
│   └── client_secret.example.json
├── data/                       # Local data & vector indices (gitignored)
├── scripts/                    # Maintenance & diagnostic utility scripts
├── .env.example                # Template for environment configuration
├── .gitignore                  # Git ignore rules for security & hygiene
├── main.py                     # FastAPI application entry point
├── requirements.txt            # Python backend dependencies
└── README.md                   # Project documentation
```

---

## 🚀 Getting Started

### Prerequisites

- **Python**: 3.11 or 3.12
- **Node.js**: v18.17+ or v20+ & npm / pnpm
- **PostgreSQL**: v14+ (or cloud instance)
- **Redis**: v6+ (or cloud instance)
- **Google Cloud Platform Project** with enabled APIs:
  - Google Drive API
  - Google Docs API
  - Google Sheets API
  - Google Calendar API
  - Gmail API

---

### Environment Configuration

1. Clone the repository:
   ```bash
   git clone https://github.com/SARTH9191/AI-Powered-Hospital-Management-Patient-Workflow-Automation-System.git
   cd AI-Powered-Hospital-Management-Patient-Workflow-Automation-System
   ```

2. Copy the sample environment file:
   ```bash
   cp .env.example .env
   ```

3. Open `.env` and fill in your credentials (database passwords, Google OAuth IDs, Twilio keys).

---

### Google Workspace & OAuth Setup

1. Go to the [Google Cloud Console](https://console.cloud.google.com/).
2. Create a project and enable the **Google Drive**, **Docs**, **Sheets**, **Calendar**, and **Gmail** APIs.
3. Navigate to **APIs & Services > Credentials**.
4. Create an **OAuth 2.0 Client ID** (Desktop Application or Web Application).
5. Download the credentials JSON and save it as:
   ```
   credentials/client_secret.json
   ```
   *(Refer to `credentials/client_secret.example.json` for format details).*

---

### Database & Cache Setup

1. Start PostgreSQL and create the database:
   ```sql
   CREATE DATABASE hospital_ai;
   ```
2. Initialize tables using the provided schema:
   ```bash
   psql -U postgres -d hospital_ai -f database/schema.sql
   ```
3. Start the Redis service:
   ```bash
   redis-server
   ```

---

### Backend Setup (FastAPI)

1. Create and activate a Python virtual environment:
   ```bash
   python -m venv venv
   # On Windows:
   venv\Scripts\activate
   # On Linux/macOS:
   source venv/bin/activate
   ```

2. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

3. Launch the FastAPI server:
   ```bash
   uvicorn main:app --reload --port 8000
   ```
4. Access interactive API documentation:
   - Swagger UI: [http://localhost:8000/docs](http://localhost:8000/docs)
   - ReDoc: [http://localhost:8000/redoc](http://localhost:8000/redoc)

---

### Frontend Setup (Next.js)

1. Open a new terminal and navigate to `frontend`:
   ```bash
   cd frontend
   ```

2. Install dependencies:
   ```bash
   npm install
   ```

3. Start the Next.js development server:
   ```bash
   npm run dev
   ```

4. Open the application in your browser:
   [http://localhost:3000](http://localhost:3000)

---

## 📡 API Reference

| Method | Endpoint | Description | Auth Required |
| :--- | :--- | :--- | :---: |
| `POST` | `/token` | OAuth2 username/password login for JWT token | ❌ |
| `POST` | `/auth/register` | Register new hospital staff or patient user | ❌ |
| `GET` | `/auth/me` | Fetch authenticated user profile | ✅ |
| `POST` | `/ai-chat/message` | Send chat message to 12-stage AI agent | Optional |
| `GET` | `/ai-chat/status/{patient_id}` | Retrieve current workflow stage and state | ✅ |
| `POST` | `/ai-chat/reset-session` | Clear conversation session and reset stage | Optional |
| `GET` | `/patients/` | List hospital patients with pagination | ✅ |
| `GET` | `/patients/{patient_id}` | Get complete patient record and history | ✅ |
| `GET` | `/docs` | Interactive Swagger documentation | ❌ |

---

## 🔒 Security & Compliance

- **Zero Credential Leaks**: `.env` and OAuth token pickles are strictly ignored from version control.
- **Role-Based Access Control (RBAC)**: Enforced via JWT authentication for Admin, Doctor, Nurse, and Patient roles.
- **HIPAA-Ready Architecture**: Isolated patient Google Drive folders with restricted sharing scopes.
- **Audit Trails**: All clinical decisions, doctor approvals, and agent tool executions are permanently logged in PostgreSQL.

---

## 🤝 Contributing

Contributions are welcome! To contribute:

1. Fork the Project.
2. Create your Feature Branch (`git checkout -b feature/AmazingFeature`).
3. Commit your Changes (`git commit -m 'Add some AmazingFeature'`).
4. Push to the Branch (`git push origin feature/AmazingFeature`).
5. Open a Pull Request.

---

## 📄 License

Distributed under the MIT License. See `LICENSE` for more information.

---

**Built with ❤️ for intelligent, autonomous, and compassionate healthcare automation.**
