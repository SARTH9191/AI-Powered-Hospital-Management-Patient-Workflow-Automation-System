# 🎨 Visual Workflow Diagrams

## 1. Complete AI-Powered Workflow

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                         PATIENT REGISTRATION                                │
│                            (Stage 1)                                        │
└─────────────────────────────────────────────────────────────────────────────┘
                                    ↓
┌─────────────────────────────────────────────────────────────────────────────┐
│                         DOCUMENT UPLOAD                                     │
│                            (Stage 2)                                        │
│                   ✅ ID Proof Mandatory                                     │
└─────────────────────────────────────────────────────────────────────────────┘
                                    ↓
┌─────────────────────────────────────────────────────────────────────────────┐
│                      MEDICAL HISTORY COLLECTION                             │
│                            (Stage 3)                                        │
│                                                                             │
│  1️⃣ Retrieve past records (if existing patient)                            │
│  2️⃣ Collect NEW symptoms/conditions                                        │
│  3️⃣ Combine: Past History + Current Symptoms                               │
│  ────────────────────────────────────────────────────────────────────────  │
│  🤖 AI ANALYSIS (NEW)                                                       │
│  ────────────────────────────────────────────────────────────────────────  │
│  4️⃣ ChromaDB Semantic Search (more.json)                                   │
│  5️⃣ Suggest Lab Tests (e.g., ECG, Troponin, Echo)                          │
│  6️⃣ Identify Specialist (e.g., Cardiologist)                               │
│  ────────────────────────────────────────────────────────────────────────  │
│  📊 COLLABORATIVE SHEET (ENHANCED)                                          │
│  ────────────────────────────────────────────────────────────────────────  │
│  7️⃣ Create Google Sheet with AI suggestions                                │
│  8️⃣ Share with identified specialist                                       │
│  9️⃣ Create approval request                                                │
│  🔟 Auto-approve (testing mode)                                             │
└─────────────────────────────────────────────────────────────────────────────┘
                                    ↓
                          ┌─────────────────┐
                          │ DOCTOR DECISION │
                          └─────────────────┘
                                    ↓
                 ┌──────────────────┼──────────────────┐
                 ↓                  ↓                  ↓
       ┌─────────────────┐ ┌─────────────────┐ ┌─────────────────┐
       │  APPROVE TESTS  │ │   APPOINTMENT   │ │    OPERATION    │
       │                 │ │                 │ │                 │
       │   Stage 4:      │ │   Stage 11:     │ │   Stage 7:      │
       │ Lab Coordination│ │  Follow-up Care │ │ Admission Plan  │
       └─────────────────┘ └─────────────────┘ └─────────────────┘
                 ↓                  ↓                  ↓
       ┌─────────────────┐ ┌─────────────────┐ ┌─────────────────┐
       │ Schedule Labs   │ │Schedule Appt    │ │Admission Process│
       │ → Lab Results   │ │→ Doctor Visit   │ │→ Treatment      │
       │ → Doctor Review │ │→ Prescription   │ │→ Surgery        │
       └─────────────────┘ └─────────────────┘ └─────────────────┘
```

## 2. ChromaDB Medical Knowledge Flow

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                           more.json (30+ Entries)                           │
├─────────────────────────────────────────────────────────────────────────────┤
│  Entry 1: Chest Pain → Cardiologist → [ECG, Troponin, Echo]                │
│  Entry 2: Hypertension → Cardiologist → [BP log, Lipid, Kidney]            │
│  Entry 3: Diabetes → Endocrinologist → [Glucose, HbA1c]                    │
│  Entry 4: Abdominal Pain → Gastroenterologist → [LFT, Amylase]             │
│  ... (26 more entries)                                                      │
└─────────────────────────────────────────────────────────────────────────────┘
                                    ↓
                          ┌─────────────────┐
                          │  Index Process  │
                          │  (On Tool Init) │
                          └─────────────────┘
                                    ↓
┌─────────────────────────────────────────────────────────────────────────────┐
│                    ChromaDB Vector Store                                    │
│                  (Collection: medical_knowledge)                            │
├─────────────────────────────────────────────────────────────────────────────┤
│  Vector 1: [0.12, -0.34, 0.56, ...] → Chest Pain entry                     │
│  Vector 2: [0.23, 0.45, -0.12, ...] → Hypertension entry                   │
│  Vector 3: [-0.34, 0.67, 0.23, ...] → Diabetes entry                       │
│  ... (30 embeddings total)                                                 │
└─────────────────────────────────────────────────────────────────────────────┘
                                    ↓
                          ┌─────────────────┐
                          │ Patient History │
                          │ "Chest pain +   │
                          │  palpitations + │
                          │  hypertension"  │
                          └─────────────────┘
                                    ↓
                          ┌─────────────────┐
                          │ Semantic Search │
                          │ (Similarity)    │
                          └─────────────────┘
                                    ↓
┌─────────────────────────────────────────────────────────────────────────────┐
│                         Search Results (Top 3)                              │
├─────────────────────────────────────────────────────────────────────────────┤
│  1. Chest Pain (Score: 0.95)                                                │
│     Doctor: Cardiologist                                                    │
│     Tests: [ECG, Troponin Test, Echocardiogram]                             │
│                                                                             │
│  2. Hypertension (Score: 0.85)                                              │
│     Doctor: Cardiologist                                                    │
│     Tests: [BP log, Lipid Profile, Kidney Function]                         │
│                                                                             │
│  3. Palpitations (Score: 0.78)                                              │
│     Doctor: Cardiologist                                                    │
│     Tests: [ECG, Holter Monitor, Thyroid Function]                          │
└─────────────────────────────────────────────────────────────────────────────┘
                                    ↓
                          ┌─────────────────┐
                          │   AI Decision   │
                          │ Specialist:     │
                          │  Cardiologist   │
                          │ Tests: ECG,     │
                          │  Troponin, Echo │
                          └─────────────────┘
```

## 3. Doctor Approval Flow

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                      DOCTOR REVIEW SHEET CREATED                            │
│                                                                             │
│  URL: https://docs.google.com/spreadsheets/d/ABC123/edit                   │
│  Title: Doctor Review - John Doe (REG2025001)                              │
└─────────────────────────────────────────────────────────────────────────────┘
                                    ↓
              ┌───────────────────────────────────────┐
              │  DoctorApprovalFlowTool._run()        │
              └───────────────────────────────────────┘
                                    ↓
                 ┌──────────────────┼──────────────────┐
                 ↓                                     ↓
       ┌─────────────────┐                   ┌─────────────────┐
       │  Identify Email │                   │  Share Sheet    │
       │                 │                   │  (Writer Access)│
       │ Cardiologist →  │                   │                 │
       │ cardio@hospital │                   │ Email sent to:  │
       │     .com        │                   │ cardio@hospital │
       └─────────────────┘                   │     .com        │
                                             └─────────────────┘
                                                      ↓
                                             ┌─────────────────┐
                                             │Create Approval  │
                                             │   Request       │
                                             │                 │
                                             │ Action: order   │
                                             │  _lab_test      │
                                             │ Priority: high  │
                                             │ Tests: [ECG,    │
                                             │  Troponin, Echo]│
                                             └─────────────────┘
                                                      ↓
                                   ┌──────────────────────────────┐
                                   │   AUTO_APPROVE_MODE = True   │
                                   │   (Testing Only)             │
                                   └──────────────────────────────┘
                                                      ↓
                                             ┌─────────────────┐
                                             │ Approval Result │
                                             │                 │
                                             │ ✅ Approved     │
                                             │ ID: APR2025001  │
                                             │ Tests: [ECG,    │
                                             │  Troponin, Echo]│
                                             └─────────────────┘
                                                      ↓
                                          ┌────────────────────┐
                                          │  Update State      │
                                          │                    │
                                          │ pending_actions:   │
                                          │  [schedule_labs]   │
                                          │ current_stage: 4   │
                                          └────────────────────┘
```

## 4. State Transitions

```
┌──────────┐     ┌──────────┐     ┌──────────┐     ┌──────────┐
│ Stage 1  │────>│ Stage 2  │────>│ Stage 3  │────>│ Stage 3.5│
│Register  │     │Documents │     │ History  │     │AI Analysis│
└──────────┘     └──────────┘     └──────────┘     └──────────┘
                                                           │
                              ┌────────────────────────────┼────────────────────┐
                              │                            │                    │
                         ┌─────────┐                  ┌─────────┐        ┌──────────┐
                         │Approve  │                  │Schedule │        │Operation │
                         │Tests    │                  │Appt     │        │Required  │
                         └─────────┘                  └─────────┘        └──────────┘
                              │                            │                    │
                              ↓                            ↓                    ↓
                         ┌─────────┐                  ┌─────────┐        ┌──────────┐
                         │ Stage 4 │                  │Stage 11 │        │ Stage 7  │
                         │Lab Coord│                  │Follow-up│        │Admission │
                         └─────────┘                  └─────────┘        └──────────┘
                              │                            │                    │
                              ↓                            ↓                    ↓
                         ┌─────────┐                  ┌─────────┐        ┌──────────┐
                         │ Stage 5 │                  │ Stage 12│        │ Stage 8  │
                         │Lab Sched│                  │Complete │        │Treatment │
                         └─────────┘                  └─────────┘        └──────────┘
                              │                                                 │
                              ↓                                                 ↓
                         ┌─────────┐                                      ┌──────────┐
                         │ Stage 6 │                                      │ Stage 9  │
                         │Results  │                                      │Discharge │
                         └─────────┘                                      └──────────┘
                              │                                                 │
                              └────────────────────┬────────────────────────────┘
                                                   ↓
                                            ┌─────────────┐
                                            │  Stage 10   │
                                            │ Medication  │
                                            └─────────────┘
                                                   ↓
                                            ┌─────────────┐
                                            │  Stage 11   │
                                            │  Follow-up  │
                                            └─────────────┘
                                                   ↓
                                            ┌─────────────┐
                                            │  Stage 12   │
                                            │  Complete   │
                                            └─────────────┘
```

## 5. Doctor Specialty Routing

```
                           ┌─────────────────┐
                           │ Patient History │
                           │   Symptoms      │
                           └─────────────────┘
                                    ↓
                          ┌─────────────────┐
                          │  AI Analyzes    │
                          │  Symptoms       │
                          └─────────────────┘
                                    ↓
              ┌─────────────────────┼─────────────────────┐
              │                     │                     │
        ┌───────────┐         ┌───────────┐       ┌───────────┐
        │  Cardiac  │         │ Endocrine │       │  Gastro   │
        │ Symptoms  │         │ Symptoms  │       │ Symptoms  │
        └───────────┘         └───────────┘       └───────────┘
              │                     │                     │
              ↓                     ↓                     ↓
    ┌─────────────────┐   ┌─────────────────┐   ┌─────────────────┐
    │ Cardiologist    │   │Endocrinologist  │   │Gastroenterologist│
    │                 │   │                 │   │                 │
    │ cardio@hospital │   │endocrine@hospital│   │gastro@hospital │
    │     .com        │   │     .com        │   │     .com        │
    └─────────────────┘   └─────────────────┘   └─────────────────┘
              │                     │                     │
              ↓                     ↓                     ↓
    ┌─────────────────┐   ┌─────────────────┐   ┌─────────────────┐
    │ Tests:          │   │ Tests:          │   │ Tests:          │
    │ • ECG           │   │ • Glucose       │   │ • LFT           │
    │ • Troponin      │   │ • HbA1c         │   │ • Amylase       │
    │ • Echocardiogram│   │ • TSH           │   │ • Ultrasound    │
    │ • Lipid Profile │   │ • T3/T4         │   │ • Endoscopy     │
    └─────────────────┘   └─────────────────┘   └─────────────────┘
```

## 6. Data Flow

```
┌───────────────────────────────────────────────────────────────────────────┐
│                           PATIENT INPUT                                   │
│  "I have chest pain and palpitations. I also have hypertension."         │
└───────────────────────────────────────────────────────────────────────────┘
                                   ↓
┌───────────────────────────────────────────────────────────────────────────┐
│                          STATE STORAGE                                    │
│  self.state['stage_data'][3] = {                                         │
│    'chief_complaint': 'Chest pain and palpitations',                     │
│    'past_conditions': 'Hypertension',                                    │
│    'allergies': [],                                                      │
│    'medications': []                                                     │
│  }                                                                        │
└───────────────────────────────────────────────────────────────────────────┘
                                   ↓
┌───────────────────────────────────────────────────────────────────────────┐
│                       AI ANALYSIS (ChromaDB)                              │
│  SuggestTestsFromHistoryTool._run(                                        │
│    history_text="Chest pain palpitations hypertension",                  │
│    n_results=3                                                            │
│  )                                                                        │
│  ↓                                                                        │
│  Returns: {                                                               │
│    'suggested_doctor': 'Cardiologist',                                   │
│    'suggested_tests': [                                                  │
│      {'tests': ['ECG', 'Troponin', 'Echo'], 'score': 0.95}              │
│    ]                                                                     │
│  }                                                                        │
└───────────────────────────────────────────────────────────────────────────┘
                                   ↓
┌───────────────────────────────────────────────────────────────────────────┐
│                      UPDATE STATE (AI Results)                            │
│  self.state['suggested_doctor'] = 'Cardiologist'                         │
│  self.state['suggested_tests'] = [...]                                   │
│  self.state['doctor_review_sheet_url'] = 'https://...'                   │
└───────────────────────────────────────────────────────────────────────────┘
                                   ↓
┌───────────────────────────────────────────────────────────────────────────┐
│                       DOCTOR APPROVAL FLOW                                │
│  DoctorApprovalFlowTool._run(                                             │
│    spreadsheet_url='https://...',                                         │
│    suggested_tests=[...],                                                 │
│    doctor_specialty='Cardiologist',                                       │
│    patient_id='REG2025001'                                                │
│  )                                                                        │
│  ↓                                                                        │
│  Returns: {                                                               │
│    'approved': True,                                                      │
│    'tests': ['ECG', 'Troponin', 'Echo'],                                 │
│    'shared_with': 'cardio@hospital.com'                                  │
│  }                                                                        │
└───────────────────────────────────────────────────────────────────────────┘
                                   ↓
┌───────────────────────────────────────────────────────────────────────────┐
│                      UPDATE STATE (Approval)                              │
│  self.state['doctor_approval_result'] = {...}                            │
│  self.state['pending_actions'] = ['schedule_lab_tests']                  │
│  self.state['scheduled_tests'] = ['ECG', 'Troponin', 'Echo']             │
│  self.state['current_stage'] = 4                                         │
└───────────────────────────────────────────────────────────────────────────┘
                                   ↓
┌───────────────────────────────────────────────────────────────────────────┐
│                         STAGE TRANSITION                                  │
│  Patient proceeds to Stage 4: Lab Coordination                            │
│  with pre-approved tests: ECG, Troponin Test, Echocardiogram             │
└───────────────────────────────────────────────────────────────────────────┘
```

---

## Legend

- 🔥 **NEW** - Newly added feature
- ✅ **ENHANCED** - Improved existing feature
- 📊 **AUTOMATED** - Happens automatically without user input
- 👨‍⚕️ **DOCTOR ACTION** - Requires doctor intervention
- 🤖 **AI DECISION** - AI-powered intelligent decision

---

**These diagrams show the complete flow of the AI-powered doctor approval workflow!**
