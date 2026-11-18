# 🚀 Quick Start: Testing AI-Powered Doctor Approval

## Prerequisites

```powershell
# Install required dependencies
pip install chromadb sentence-transformers

# Verify installation
python -c "import chromadb; from sentence_transformers import SentenceTransformer; print('✅ All dependencies installed')"
```

## Test 1: Medical Knowledge Lookup (30 seconds)

```powershell
# Test ChromaDB lookup with sample patient history
python -c "from tools.medical_knowledge_chromadb_tool import SuggestTestsFromHistoryTool; t=SuggestTestsFromHistoryTool(); res=t._run(history_text='Patient with chest pain and palpitations, prior history of hypertension', n_results=3); import json; print(json.dumps(res, indent=2))"
```

**Expected Output:**
```json
{
  "success": true,
  "suggested_tests": [
    {
      "doctor": "Cardiologist",
      "tests": ["ECG", "Troponin Test", "Echocardiogram"],
      "notes": "Chest Pain",
      "score": 0.95
    }
  ],
  "suggested_doctor": "Cardiologist"
}
```

## Test 2: Complete Test Suite (2 minutes)

```powershell
# Run comprehensive test suite
python test_stage3_doctor_approval.py
```

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

## Test 3: Manual Patient Scenarios

### Scenario A: Cardiac Patient
```powershell
# Test cardiac symptoms
python -c "from tools.medical_knowledge_chromadb_tool import SuggestTestsFromHistoryTool; t=SuggestTestsFromHistoryTool(); res=t._run(history_text='Patient complains of chest tightness after exercise, irregular heartbeat, and dizziness', n_results=3); print('Doctor:', res.get('suggested_doctor')); print('Tests:', [s.get('tests') for s in res.get('suggested_tests', [])])"
```

**Expected:** Doctor: Cardiologist, Tests: ECG, Treadmill Test, Holter Monitor

### Scenario B: Diabetes Patient
```powershell
# Test endocrine symptoms
python -c "from tools.medical_knowledge_chromadb_tool import SuggestTestsFromHistoryTool; t=SuggestTestsFromHistoryTool(); res=t._run(history_text='Patient with excessive thirst, frequent urination, fatigue, and unexplained weight loss', n_results=3); print('Doctor:', res.get('suggested_doctor')); print('Tests:', [s.get('tests') for s in res.get('suggested_tests', [])])"
```

**Expected:** Doctor: Endocrinologist, Tests: Fasting Glucose, HbA1c

### Scenario C: Gastro Patient
```powershell
# Test gastro symptoms
python -c "from tools.medical_knowledge_chromadb_tool import SuggestTestsFromHistoryTool; t=SuggestTestsFromHistoryTool(); res=t._run(history_text='Patient has severe abdominal pain, nausea, vomiting, and bloating for 5 days', n_results=3); print('Doctor:', res.get('suggested_doctor')); print('Tests:', [s.get('tests') for s in res.get('suggested_tests', [])])"
```

**Expected:** Doctor: Gastroenterologist, Tests: LFT, Amylase, Ultrasound

## Test 4: End-to-End Workflow (Manual)

### Step 1: Start Server
```powershell
# Terminal 1: Start FastAPI backend
uvicorn main:app --reload
```

### Step 2: Start Frontend
```powershell
# Terminal 2: Start React frontend
cd frontend
npm run dev
```

### Step 3: Test Patient Journey
1. Navigate to: http://localhost:3000
2. Register as new patient
3. Upload documents (ID proof required)
4. **Stage 3:** Provide medical history:
   - "I have chest pain and palpitations for 3 days"
   - "I have hypertension and high cholesterol"
5. **Observe AI Analysis:**
   - System suggests: Cardiologist
   - System suggests: ECG, Troponin Test, Echocardiogram
6. **Confirm doctor review sheet creation**
7. **Check Google Sheets:**
   - Open shared sheet URL
   - Verify pre-filled AI suggestions
   - Check it's shared with cardio@cityhospital.com
8. **Verify auto-approval:**
   - Tests should be auto-approved (AUTO_APPROVE_MODE=True)
   - Patient advances to Stage 4: Lab Coordination

## Test 5: Doctor View (Google Sheets)

### Open Review Sheet
1. Click on sheet URL provided by AI agent
2. Verify structure:
   - ✅ Patient Information section
   - ✅ Medical History (past + current)
   - ✅ Current Symptoms
   - ✅ AI-suggested tests (pre-filled)
   - ✅ Editable doctor assessment sections
   - ✅ Editable lab tests table
   - ✅ Doctor signature section

### Doctor Actions (Manual Test)
1. **Approve Tests:** Fill assessment, approve AI suggestions
2. **Modify Tests:** Add/remove tests in "Recommended Lab Tests" section
3. **Make Decision:** Write in notes:
   - "Approve tests" → Patient goes to Stage 4
   - "Schedule appointment" → Patient goes to Stage 11
   - "Recommend operation" → Patient goes to Stage 7

## Troubleshooting

### ChromaDB Not Found
```powershell
pip install chromadb sentence-transformers
```

### No Tests Suggested
- Check if `more.json` exists in project root
- Verify patient history contains relevant keywords
- Try more specific symptoms (e.g., "chest pain" vs "feeling unwell")

### Sheet Sharing Failed
- Verify Google Sheets API credentials
- Check doctor email in `.env` file
- Ensure `sheets_token.pickle` is valid

### Approval Not Working
- Check `AUTO_APPROVE_MODE` in `tools/approval_tool.py`
- For testing: Set to `True`
- For production: Set to `False`

## Quick Commands Reference

```powershell
# Install dependencies
pip install chromadb sentence-transformers

# Run full test suite
python test_stage3_doctor_approval.py

# Test medical lookup only
python -c "from tools.medical_knowledge_chromadb_tool import SuggestTestsFromHistoryTool; t=SuggestTestsFromHistoryTool(); print(t._run(history_text='chest pain palpitations hypertension', n_results=3))"

# Test approval flow only (mock data)
python -c "from tools.doctor_approval_flow_tool import DoctorApprovalFlowTool; t=DoctorApprovalFlowTool(); print(t._run(spreadsheet_url='https://docs.google.com/spreadsheets/d/MOCK/edit', suggested_tests=[{'tests': ['ECG'], 'doctor': 'Cardiologist'}], doctor_specialty='Cardiologist', patient_id='TEST001', patient_name='Test Patient'))"

# Check ChromaDB database stats
python -c "from tools.vector_search_tool import get_all_collection_stats; print(get_all_collection_stats())"

# Start backend server
uvicorn main:app --reload

# Start frontend
cd frontend; npm run dev
```

## Environment Setup (.env)

```bash
# Add to .env file
CARDIOLOGIST_EMAIL=cardio@cityhospital.com
ENDOCRINOLOGIST_EMAIL=endocrine@cityhospital.com
GASTROENTEROLOGIST_EMAIL=gastro@cityhospital.com
GENERAL_DOC_EMAIL=doctor@cityhospital.com
DOCTOR_EMAIL=doctor@cityhospital.com
```

## Success Indicators

✅ **Test Suite:** "🎉 ALL TESTS PASSED!"
✅ **Medical Lookup:** Returns `suggested_doctor` + `suggested_tests`
✅ **Approval Flow:** Returns `approved: true` + `approval_id`
✅ **Stage Transition:** Patient advances to Stage 4 after approval
✅ **Sheet Sharing:** Doctor receives email notification with sheet link

## Next Steps After Testing

1. **Review Documentation:**
   - `DOCTOR_APPROVAL_WORKFLOW.md` - Complete workflow guide
   - `STAGE3_DOCTOR_REVIEW_SHEET.md` - Stage 3 details
   - `IMPLEMENTATION_COMPLETE.md` - Summary of changes

2. **Configure Production:**
   - Set `AUTO_APPROVE_MODE = False` in `tools/approval_tool.py`
   - Add real doctor email addresses to `.env`
   - Test with real Google Sheets API

3. **Extend Functionality:**
   - Add more entries to `more.json`
   - Implement reading doctor's decisions from sheet
   - Add multi-doctor consultation support

## Getting Help

- Check `DOCTOR_APPROVAL_WORKFLOW.md` for detailed documentation
- Review test output for specific errors
- Verify all dependencies installed
- Ensure Google API tokens are valid

**Happy Testing! 🚀**
