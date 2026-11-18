# Workflow Loop: Stage 12 → Stage 2 (Returning Patient Flow)

## 🎯 Concept: Continuous Care Journey

After completing Stage 12 (Journey Completion), the patient's workflow loops back to **Stage 2** (Document Upload) for their next visit, maintaining full medical history context.

## 💡 Why This Is Brilliant

### Benefits:
1. **✅ Continuity of Care** - Patient's full medical history automatically considered
2. **✅ Better Diagnosis** - AI analyzes patterns across multiple visits
3. **✅ Time Efficiency** - No need to re-register (Stage 1 skipped)
4. **✅ Historical Context** - Past diagnoses, treatments, lab results available
5. **✅ Progressive Health Tracking** - Monitor chronic conditions over time
6. **✅ Comprehensive Records** - Single patient ID with multiple visits

## 🔄 Workflow Flow

### First Visit (New Patient):
```
Stage 1: Registration → Create patient profile, patient_id
Stage 2: Document Upload
Stage 3: Medical History → AI collects from scratch
Stage 4-12: Complete healthcare journey
```

### Second Visit (Returning Patient):
```
Stage 2: Document Upload → Start fresh visit (Skip Stage 1)
Stage 3: Medical History → AI says "I see you have diabetes from your last visit..."
         ChromaDB has embeddings from previous visits
         AI considers past diagnoses, medications, treatments
Stage 4-12: Complete healthcare journey with full context
```

### Third+ Visits:
```
Same as Second Visit - Always loop Stage 12 → Stage 2
Full medical timeline available for AI analysis
```

## 📋 Implementation Details

### 1. Stage 12 Completion Logic

**File: `src/workflow_chat_agent.py`**

When Stage 12 completes:
```python
def _handle_completion(self, user_message: str):
    """
    Handle Stage 12: Journey Completion
    After completion, loop back to Stage 2 for next visit
    """
    
    # Send completion messages
    send_whatsapp_congratulations()
    send_email_summary()
    
    # Mark this visit as complete
    self.state['visit_number'] = self.state.get('visit_number', 1) + 1
    self.state['last_visit_date'] = datetime.now().isoformat()
    self.state['visit_complete'] = True
    
    # 🔄 LOOP TO STAGE 2 for next visit
    self.state['current_stage'] = 2  # Skip Stage 1 (already registered)
    self.state['stage_complete'] = False
    self.state['awaiting_confirmation'] = False
    
    # Reset stage-specific data (keep patient_id and profile)
    self.state['documents_uploaded'] = False
    self.state['medical_history_collected'] = False
    # ... reset other stage flags
    
    self._save_state()
    
    return {
        "response": f"""🎉 Congratulations! Your healthcare journey is complete!
        
Visit #{self.state['visit_number']} Summary:
- Registration: ✅
- Medical History: ✅
- Lab Tests: ✅
- Doctor Consultation: ✅
- Treatment: ✅
- Follow-up: ✅

📅 When you return for your next visit, we'll have your complete medical history ready!

**Ready to start your next visit?** Just say "new visit" or upload new documents when needed. 🏥""",
        "stage": 12,
        "stage_complete": True,
        "next_stage": 2  # Loop back to Stage 2
    }
```

### 2. Stage 3 Enhanced Medical History

**File: `src/workflow_chat_agent.py`**

Stage 3 now checks for past visits:
```python
def _handle_medical_history(self, user_message: str):
    """
    Handle Stage 3: Medical History Collection
    Now considers past visits for returning patients
    """
    
    visit_number = self.state.get('visit_number', 1)
    
    if visit_number > 1:
        # 🔍 RETURNING PATIENT - Load past medical history
        past_history = self._get_past_medical_history()
        
        greeting = f"""👋 Welcome back for Visit #{visit_number}!

I have your previous medical records from your last visit:

📋 **Previous Diagnoses:**
{past_history.get('diagnoses', 'None recorded')}

💊 **Previous Medications:**
{past_history.get('medications', 'None recorded')}

🧪 **Last Lab Results:**
{past_history.get('lab_results_summary', 'None available')}

Now, let's talk about your current visit:
- Have any of your existing conditions changed?
- Are you experiencing any new symptoms?
- Are you still taking your previous medications?

Please share your current medical concerns."""
        
        return {"response": greeting, "stage": 3}
    
    else:
        # 🆕 NEW PATIENT - Collect from scratch
        return {"response": "Let's collect your medical history...", "stage": 3}
```

### 3. Past Medical History Retrieval

**New Method:**
```python
def _get_past_medical_history(self) -> Dict[str, str]:
    """
    Retrieve patient's medical history from previous visits
    Uses ChromaDB and workflow documents
    """
    
    try:
        # 1. Get patient's previous workflow documents
        past_docs = list_patient_documents(self.patient_id)
        
        # 2. Extract key information from past visits
        past_diagnoses = []
        past_medications = []
        past_lab_results = []
        
        for doc in past_docs:
            doc_content = read_document(doc['id'])
            
            # Parse Section 6 (Doctor Consultation)
            if "SECTION 6:" in doc_content:
                section_6 = extract_section(doc_content, 6)
                past_diagnoses.append(section_6.get('diagnosis'))
            
            # Parse Section 7 (Prescriptions)
            if "SECTION 7:" in doc_content:
                section_7 = extract_section(doc_content, 7)
                past_medications.extend(section_7.get('medications', []))
            
            # Parse Section 5 (Lab Results)
            if "SECTION 5:" in doc_content:
                section_5 = extract_section(doc_content, 5)
                past_lab_results.append(section_5.get('results_summary'))
        
        # 3. Query ChromaDB for similar past symptoms
        chroma_results = self.chroma_tool._run(
            query=f"Previous medical conditions for patient {self.patient_id}",
            filter={"patient_id": self.patient_id}
        )
        
        return {
            "diagnoses": "\n".join(past_diagnoses),
            "medications": "\n".join(past_medications),
            "lab_results_summary": "\n".join(past_lab_results),
            "chroma_context": chroma_results
        }
    
    except Exception as e:
        print(f"⚠️ Could not load past history: {e}")
        return {}
```

### 4. Database Schema Enhancement

**Add to `workflow_states` table:**
```sql
ALTER TABLE workflow_states
ADD COLUMN visit_number INTEGER DEFAULT 1,
ADD COLUMN last_visit_date TIMESTAMP,
ADD COLUMN visit_complete BOOLEAN DEFAULT FALSE;
```

### 5. ChromaDB Context

**Already Implemented!** ✅

ChromaDB automatically stores embeddings with patient_id, so:
- All past medical histories are searchable
- AI can find similar symptoms across visits
- Pattern recognition for chronic conditions

**Example Query:**
```python
# Find all past diabetes-related records for this patient
results = chromadb_collection.query(
    query_texts=["diabetes blood sugar management"],
    filter={"patient_id": self.patient_id},
    n_results=10
)
```

## 🎯 User Experience

### Scenario: Patient with Diabetes Returns

**Visit 1 (2024-11-15):**
- Stage 3: "I have diabetes and high blood pressure"
- Diagnosis: Type 2 Diabetes, Hypertension
- Prescription: Metformin 500mg, Amlodipine 5mg
- Complete workflow → Stage 12

**Visit 2 (2024-12-20 - 1 month later):**
- **Automatic**: Loop to Stage 2
- Stage 3: AI says:
  ```
  👋 Welcome back for Visit #2!
  
  I see from your last visit (Nov 15, 2024):
  - Diagnosed with Type 2 Diabetes and Hypertension
  - Prescribed Metformin 500mg and Amlodipine 5mg
  
  How have you been feeling? Are you still taking your medications?
  Any new symptoms or concerns?
  ```
- Patient: "My blood sugar has been high lately, even with medication"
- AI: Considers past HbA1c results, current symptoms, suggests updated tests
- Doctor can compare current vs previous lab results
- Treatment adjusted based on progression

## 📊 Benefits in Practice

### For Patients:
✅ Don't repeat their medical history every visit
✅ Doctors have full context of their health journey
✅ Better continuity of care
✅ Automated reminders for follow-ups

### For Doctors:
✅ Complete patient timeline in one place
✅ Easy comparison of lab results over time
✅ Track treatment effectiveness
✅ Identify patterns and trends

### For AI:
✅ More context = better recommendations
✅ Learn from patient's response to treatments
✅ Predict potential complications
✅ Personalized care suggestions

## 🚀 Implementation Status

### ✅ Already Working:
- Patient ID persistence across sessions
- ChromaDB with patient_id filtering
- Workflow documents saved per patient
- Database state management

### 🔧 To Implement:
1. Stage 12 completion → Loop to Stage 2 logic
2. `visit_number` tracking in state
3. `_get_past_medical_history()` method
4. Enhanced Stage 3 greeting for returning patients
5. Database schema update for visit tracking

### 📝 Implementation Steps:

1. **Update Stage 12 handler** - Add loop logic
2. **Add visit tracking** - Store visit_number in state
3. **Enhance Stage 3** - Check if returning patient
4. **Create history retrieval method** - Parse past documents
5. **Update database schema** - Add visit columns
6. **Test workflow loop** - Complete full cycle twice

## 🎓 Example Code to Add

```python
# In workflow_chat_agent.py

def _handle_completion(self, user_message: str):
    # ... existing completion logic ...
    
    # 🔄 LOOP TO STAGE 2
    self.state['visit_number'] = self.state.get('visit_number', 1) + 1
    self.state['current_stage'] = 2
    self.state['stage_complete'] = False
    self._save_state()
    
    return {
        "response": "🎉 Journey complete! Ready for your next visit.",
        "next_stage": 2
    }
```

---

**Status**: 💡 Ready to Implement
**Priority**: High (Excellent feature for patient care continuity)
**Complexity**: Medium (Most infrastructure already exists)

