# 🏥 AI-Powered Doctor Approval Workflow

## Overview

This document describes the complete AI-powered doctor approval workflow that intelligently:
1. **Analyzes patient medical history** using ChromaDB semantic search
2. **Suggests appropriate lab tests** based on symptoms and conditions
3. **Recommends specialist doctors** (Cardiologist, Endocrinologist, Gastroenterologist, General Physician)
4. **Creates collaborative review sheets** for doctor review
5. **Handles doctor decisions** (approve tests, schedule appointment, or recommend operation)
6. **Automatically advances workflow stages** based on doctor input

---

## Architecture

### Components

1. **Medical Knowledge Database (`more.json`)**
   - 30+ symptom/disease entries mapped to doctor specialists
   - Required lab tests for each condition
   - Tags for semantic matching (e.g., "chest", "pain", "heart")

2. **ChromaDB Vector Store**
   - Indexes `more.json` entries with embeddings
   - Enables semantic search for symptom matching
   - Falls back to keyword matching if ChromaDB unavailable

3. **Tools**
   - `SuggestTestsFromHistoryTool`: Analyzes history → suggests tests + doctor
   - `DoctorApprovalFlowTool`: Shares sheet + creates approval request
   - `CreateDoctorReviewSheetTool`: Generates collaborative Google Sheet

4. **Workflow Agent (`workflow_chat_agent.py`)**
   - Orchestrates Stage 3 medical history collection
   - Calls tools in sequence
   - Manages state transitions

---

## Workflow Stages

### Stage 1-2: Registration & Document Upload
*(No changes - existing functionality)*

### Stage 3: Medical History + AI Analysis (Enhanced)

```
Patient provides medical history
         ↓
Existing patient? → Retrieve past records from Google Sheets
         ↓
Collect NEW symptoms/conditions only
         ↓
Combine: Past Medical History + Current Symptoms
         ↓
🔥 NEW: AI analyzes combined history using ChromaDB
         ↓
🔥 NEW: Suggest lab tests (e.g., ECG, Troponin, Echo)
         ↓
🔥 NEW: Identify specialist (e.g., Cardiologist)
         ↓
Create Doctor Review Sheet (Google Sheets)
         ↓
🔥 NEW: Share sheet with identified doctor
         ↓
🔥 NEW: Create approval request for lab tests
         ↓
🔥 NEW: Auto-approved in testing mode (AUTO_APPROVE_MODE=True)
         ↓
Store: suggested_tests, suggested_doctor, scheduled_tests
         ↓
Advance to Stage 4 or Stage 11 based on doctor decision
```

### Stage 3.5: Doctor Decision Point (New)

Doctor reviews the Google Sheet and has 3 options:

**Option A: Approve Lab Tests**
- Doctor fills "Recommended Lab Tests" section in sheet
- System reads approved tests from sheet
- Patient proceeds to **Stage 4: Lab Coordination**

**Option B: Schedule Direct Appointment**
- Doctor notes "No tests required - schedule appointment"
- System skips lab stages
- Patient proceeds to **Stage 11: Follow-up Care**

**Option C: Recommend Operation**
- Doctor notes "Operation required"
- System skips intermediate stages
- Patient proceeds to **Stage 7: Admission Planning**

### Stage 4-6: Lab Coordination & Results
*(Updated to read tests from doctor review sheet)*

### Stage 7+: Admission/Treatment/Discharge
*(Triggered only if doctor recommends operation)*

---

## Technical Implementation

### 1. Medical Knowledge Tool

**File:** `tools/medical_knowledge_chromadb_tool.py`

**Key Features:**
- Indexes `more.json` into ChromaDB collection `medical_knowledge`
- Semantic search using sentence-transformers (`all-MiniLM-L6-v2`)
- Keyword fallback for reliability
- Returns: `{suggested_tests: [...], suggested_doctor: "Cardiologist"}`

**Example Usage:**
```python
from tools.medical_knowledge_chromadb_tool import SuggestTestsFromHistoryTool

tool = SuggestTestsFromHistoryTool()
result = tool._run(
    history_text="Patient with chest pain and palpitations, prior history of hypertension",
    n_results=3
)

print(result)
# Output:
# {
#   'success': True,
#   'suggested_tests': [
#     {'doctor': 'Cardiologist', 'tests': ['ECG', 'Troponin Test', 'Echocardiogram'], 'notes': 'Chest Pain', 'score': 0.95},
#     {'doctor': 'Cardiologist', 'tests': ['Blood Pressure log', 'Lipid Profile'], 'notes': 'Hypertension', 'score': 0.85}
#   ],
#   'suggested_doctor': 'Cardiologist'
# }
```

### 2. Doctor Approval Flow Tool

**File:** `tools/doctor_approval_flow_tool.py`

**Key Features:**
- Extracts spreadsheet ID from review sheet URL
- Looks up doctor email by specialty (using `SPECIALTY_EMAIL_MAP`)
- Shares sheet with doctor (writer permissions)
- Creates approval request using `approval_tool.py`
- Returns approval status and tests to schedule

**Specialty Email Mapping:**
```python
SPECIALTY_EMAIL_MAP = {
    'Cardiologist': 'cardio@cityhospital.com',
    'Endocrinologist': 'endocrine@cityhospital.com',
    'Gastroenterologist': 'gastro@cityhospital.com',
    'General Physician': 'doctor@cityhospital.com'
}
```

**Example Usage:**
```python
from tools.doctor_approval_flow_tool import DoctorApprovalFlowTool

tool = DoctorApprovalFlowTool()
result = tool._run(
    spreadsheet_url="https://docs.google.com/spreadsheets/d/ABC123/edit",
    suggested_tests=[{'tests': ['ECG', 'Echo'], 'doctor': 'Cardiologist'}],
    doctor_specialty='Cardiologist',
    patient_id='REG2025001',
    patient_name='John Doe'
)

print(result)
# Output:
# {
#   'success': True,
#   'shared_with': 'cardio@cityhospital.com',
#   'approved': True,
#   'approval_id': 'APR20251112001',
#   'tests': ['ECG', 'Echo'],
#   'message': 'Shared with doctor and auto-approved'
# }
```

### 3. Workflow Agent Integration

**File:** `src/workflow_chat_agent.py` (Lines 2960-3010)

**Code:**
```python
# After creating doctor review sheet...

# 🔎 Suggest tests & identify doctor specialty using Chroma/medical knowledge
try:
    suggest_tool = SuggestTestsFromHistoryTool()
    suggest_input = full_medical_history + "\n" + current_symptoms
    suggest_res = suggest_tool._run(history_text=suggest_input, n_results=3)
    suggested_tests = suggest_res.get('suggested_tests', [])
    suggested_doctor = suggest_res.get('suggested_doctor')
    
    # Save suggestions to state
    self.state['suggested_tests'] = suggested_tests
    self.state['suggested_doctor'] = suggested_doctor
    self._save_state()
    
    # Share sheet with identified doctor and create approval request
    approval_tool = DoctorApprovalFlowTool()
    approval_res = approval_tool._run(
        spreadsheet_url=sheet_url,
        suggested_tests=suggested_tests,
        doctor_specialty=suggested_doctor,
        patient_id=self.patient_id,
        patient_name=patient_name
    )
    
    # Store approval result
    self.state['doctor_approval_result'] = approval_res
    
    # If approved, enqueue scheduling action for lab tests
    if approval_res.get('approved'):
        if 'schedule_lab_tests' not in self.state.get('pending_actions', []):
            self.state.setdefault('pending_actions', []).append('schedule_lab_tests')
            self.state['scheduled_tests'] = approval_res.get('tests', [])
    else:
        # Handle doctor decisions
        decision = approval_res.get('decision')
        if decision == 'operation':
            self.state['current_stage'] = 7  # Jump to admission
        elif decision == 'appointment':
            self.state.setdefault('pending_actions', []).append('schedule_doctor_appointment')
    
    self._save_state()
except Exception as e:
    print(f"⚠️ Suggest tests error: {str(e)}")
```

---

## Doctor Specialist Mapping

### Cardiologist
**Conditions:** Chest Pain, Hypertension, Palpitations, Heart Attack, Arrhythmia, High Cholesterol
**Tests:** ECG, Troponin Test, Echocardiogram, Lipid Profile, Holter Monitor, Treadmill Test (TMT)

### Endocrinologist
**Conditions:** Diabetes, Thyroid Issues, PCOS, Obesity, Infertility, Osteoporosis
**Tests:** Fasting Glucose, HbA1c, TSH, T3/T4, LH, FSH, Testosterone, Vitamin D, Calcium, PTH

### Gastroenterologist
**Conditions:** Abdominal Pain, Nausea, Vomiting, Diarrhea, Constipation, Jaundice, Acid Reflux
**Tests:** LFT, Amylase, Lipase, Ultrasound, Endoscopy, Colonoscopy, Stool Tests, H. pylori

### General Physician
**Conditions:** General consultation, minor ailments, preventive checkups
**Tests:** CBC, Basic Metabolic Panel, Urinalysis

---

## State Management

### New State Fields (Added in Stage 3)

```python
self.state = {
    # ... existing fields ...
    
    # 🔥 NEW: AI Analysis Results
    'suggested_tests': [
        {
            'doctor': 'Cardiologist',
            'tests': ['ECG', 'Troponin Test', 'Echocardiogram'],
            'notes': 'Chest Pain',
            'score': 0.95
        }
    ],
    'suggested_doctor': 'Cardiologist',
    
    # 🔥 NEW: Doctor Approval
    'doctor_approval_result': {
        'success': True,
        'approved': True,
        'approval_id': 'APR20251112001',
        'tests': ['ECG', 'Troponin Test', 'Echocardiogram'],
        'shared_with': 'cardio@cityhospital.com'
    },
    
    # 🔥 NEW: Scheduled Tests
    'scheduled_tests': ['ECG', 'Troponin Test', 'Echocardiogram'],
    
    # 🔥 NEW: Pending Actions
    'pending_actions': ['schedule_lab_tests']  # or ['schedule_doctor_appointment']
}
```

---

## User Experience

### Patient View

```
AI Agent: 📋 I've analyzed your medical history:

Past Conditions: Hypertension, High Cholesterol
Current Symptoms: Chest pain and palpitations for 3 days

🔬 Based on your symptoms, I recommend:
• Specialist: Cardiologist
• Suggested Tests:
  1. ECG (Electrocardiogram)
  2. Troponin Test
  3. Echocardiogram

📊 I've created a Doctor Review Sheet and shared it with our cardiologist.

✅ Tests have been approved! 
You can now proceed to schedule your lab tests.

Would you like to schedule your lab appointments? (yes/no)
```

### Doctor View (Google Sheet)

```
┌─────────────────────────────────────────────────────────┐
│              DOCTOR REVIEW SHEET                        │
├─────────────────────────────────────────────────────────┤
│ Patient ID:   REG2025001                                │
│ Patient Name: John Doe                                  │
│ Review Date:  2025-01-12 10:30:00                       │
├─────────────────────────────────────────────────────────┤
│ MEDICAL HISTORY (Past + Current)                        │
│ • Past Conditions: Hypertension, High Cholesterol       │
│ • Known Allergies: Penicillin                           │
│ • Current Medications: Metformin, Lisinopril            │
│ • Current Symptoms: Chest pain and palpitations         │
├─────────────────────────────────────────────────────────┤
│ DOCTOR'S ASSESSMENT (Please fill below)                 │
│                                                          │
│ Initial Assessment: [DOCTOR FILLS THIS]                 │
│ Preliminary Diagnosis: [DOCTOR FILLS THIS]              │
│ Risk Assessment: [DOCTOR FILLS THIS]                    │
├─────────────────────────────────────────────────────────┤
│ RECOMMENDED LAB TESTS (AI Suggested)                    │
│                                                          │
│ Test Name          | Priority | Reason                  │
│ ─────────────────────────────────────────────────────── │
│ 1. ECG             | High     | Chest pain evaluation   │
│ 2. Troponin Test   | High     | Rule out heart attack   │
│ 3. Echocardiogram  | Medium   | Heart function check    │
│ 4. [Doctor adds more tests if needed]                   │
├─────────────────────────────────────────────────────────┤
│ DECISION (Check one):                                   │
│ [ ] Approve tests above → Patient proceeds to lab       │
│ [ ] Schedule appointment → Skip tests, see patient      │
│ [ ] Recommend operation → Admit patient immediately     │
└─────────────────────────────────────────────────────────┘
```

---

## Configuration

### Environment Variables

Add to `.env`:
```bash
# Doctor Email Addresses by Specialty
CARDIOLOGIST_EMAIL=cardio@cityhospital.com
ENDOCRINOLOGIST_EMAIL=endocrine@cityhospital.com
GASTROENTEROLOGIST_EMAIL=gastro@cityhospital.com
GENERAL_DOC_EMAIL=doctor@cityhospital.com

# Fallback doctor email
DOCTOR_EMAIL=doctor@cityhospital.com
```

### Approval Tool Configuration

In `tools/approval_tool.py`:
```python
# AUTO_APPROVE_MODE: Set to True for testing (skips human approval)
AUTO_APPROVE_MODE = True
```

For production, set `AUTO_APPROVE_MODE = False` to require real doctor approval.

---

## Testing

### Run Test Suite

```bash
python test_stage3_doctor_approval.py
```

**Test Coverage:**
1. ✅ Test medical knowledge lookup (3 specialties)
2. ✅ Test doctor approval flow
3. ✅ Test complete workflow simulation (Stage 3 → 4)

**Expected Output:**
```
🎉 ALL TESTS PASSED! 🎉

✅ Features Verified:
   • ChromaDB medical knowledge lookup
   • Test suggestion from patient history
   • Doctor specialty recommendation
   • Doctor approval flow
   • Lab test scheduling
   • Stage transitions
```

---

## Benefits

### For Patients
✅ **Faster diagnosis** - AI pre-analyzes symptoms
✅ **Right specialist** - Automatically routed to correct doctor
✅ **Relevant tests** - No unnecessary procedures
✅ **Clear communication** - Know what to expect

### For Doctors
✅ **Pre-screened patients** - AI filters and categorizes
✅ **Contextual review** - Complete history in one sheet
✅ **Flexible decisions** - Approve tests, schedule appointments, or admit
✅ **Time-saving** - No manual test selection

### For Hospital
✅ **Efficient routing** - Patients see right specialists
✅ **Reduced wait times** - Pre-approved tests ready to schedule
✅ **Better outcomes** - Evidence-based test recommendations
✅ **Audit trail** - All decisions tracked in approval system

---

## Future Enhancements

🔮 **Read doctor's handwritten decisions from sheet**
   - Parse "Recommended Lab Tests" section
   - Extract custom tests added by doctor
   - Detect decision checkboxes

🔮 **Multi-doctor consultation**
   - Route to 2+ specialists if needed
   - Coordinate approval from multiple doctors

🔮 **Predictive analytics**
   - Learn from historical cases
   - Improve test suggestions over time

🔮 **Real-time collaboration**
   - Doctor can edit sheet while patient waits
   - Instant notification to patient when approved

---

## Troubleshooting

### ChromaDB Not Available
**Symptom:** `⚠️ ChromaDB not installed. Run: pip install chromadb sentence-transformers`

**Fix:**
```bash
pip install chromadb sentence-transformers
```

Tool will fall back to keyword matching if ChromaDB fails.

### No Tests Suggested
**Symptom:** `suggested_tests` is empty

**Possible Causes:**
1. Patient history too vague → Ask more specific questions
2. Condition not in `more.json` → Add entry or use General Physician fallback
3. Semantic search failed → Check ChromaDB connection

**Fix:** Improve `more.json` coverage or use keyword-rich descriptions

### Sheet Sharing Failed
**Symptom:** `Error sharing sheet: permission denied`

**Fix:** Verify Google Sheets API credentials and doctor email permissions

---

## Summary

This AI-powered doctor approval workflow transforms Stage 3 from a simple data collection stage into an intelligent medical decision support system. By combining:
- **ChromaDB semantic search**
- **Specialist recommendation**
- **Collaborative Google Sheets**
- **Automated approval workflow**

...we create an end-to-end solution that benefits patients, doctors, and hospital operations.

**Next Steps:** Extend this workflow to read doctor's actual decisions from the sheet and dynamically adjust patient journey based on those decisions.
