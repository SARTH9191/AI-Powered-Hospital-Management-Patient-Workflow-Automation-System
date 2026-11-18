"""
Context-Aware Q&A Tools for Workflow Agent
Allows patients to ask questions during workflow without losing their place
"""

from typing import Type, Dict, Any, List, Optional
from pydantic import BaseModel, Field
from langchain.tools import BaseTool

# Import data sources
from database.db_manager import PatientDB, WorkflowStateDB
from tools.vector_search_tool import SemanticSearchTool, MedicalRAGTool

# ============================================================================
# INPUT SCHEMAS
# ============================================================================

class AskQuestionInput(BaseModel):
    """Input for asking questions during workflow"""
    question: str = Field(description="Patient's question about their health, appointments, medications, etc.")
    patient_id: str = Field(description="Patient ID to retrieve personalized information")


# ============================================================================
# PATIENT DATA RETRIEVAL TOOLS
# ============================================================================

class GetMyInformationTool(BaseTool):
    """
    Retrieve patient's own information from multiple sources
    
    Data Sources:
    1. PostgreSQL: Basic patient info, workflow state
    2. Google Sheets: Appointment tracking, status updates
    3. Vector DB: Medical records, diagnoses, treatments
    """
    
    name: str = "get_my_information"
    description: str = """Get patient's personal information including:
    - Basic details (name, contact, DOB)
    - Current workflow stage and status
    - Registration information
    - Appointments and tracking data
    
    Use this when patient asks: "What's my information?", "Where am I in the process?", "What's my status?"
    """
    args_schema: Type[BaseModel] = AskQuestionInput
    
    def _run(self, question: str, patient_id: str) -> str:
        """Retrieve patient information"""
        
        try:
            question_lower = question.lower().strip()
            
            # 🆕 Handle workflow commands first
            if question_lower in ['done', 'finished', 'complete', 'ready']:
                return """✅ **Great! Ready for Next Step**

Your current stage is complete and you're ready to proceed.

🚀 **What happens next:**
• The system will guide you to the next stage
• You'll receive instructions for the next steps
• Continue following the workflow prompts

💬 **Need help?** Just ask "what's my status?" or "what's next?"

---
*Continue with your workflow - you're doing great!* 🎯"""
            
            if question_lower in ['yes', 'y', 'okay', 'ok', 'proceed']:
                return """✅ **Confirmed! Proceeding...**

Moving forward with your request.

🔄 **Status:** Your response has been recorded
🚀 **Next:** Follow the workflow instructions
💬 **Questions?** Ask anytime during the process

---
*The system will guide you through the next steps.* ➡️"""
            
            if question_lower in ['no', 'n', 'not yet', 'wait']:
                return """⏸️ **No Problem!**

Take your time. The system will wait for you to be ready.

💡 **When you're ready:**
• Type "done" or "ready" to continue
• Ask "what's my status?" to check your progress
• Type "help" for assistance

---
*We're here when you need us!* 🤝"""
            
            response_parts = []
            
            # 1. Get from PostgreSQL
            patient_db = PatientDB()
            patient_data = patient_db.get_patient_by_id(patient_id)
            
            if patient_data:
                response_parts.append("📋 **Your Information:**")
                response_parts.append(f"• Patient ID: {patient_data.get('patient_id')}")
                response_parts.append(f"• Name: {patient_data.get('first_name')} {patient_data.get('last_name')}")
                response_parts.append(f"• Email: {patient_data.get('email')}")
                response_parts.append(f"• Phone: {patient_data.get('phone')}")
                
                if patient_data.get('date_of_birth'):
                    response_parts.append(f"• Age: {patient_data.get('age')} years")
                
                if patient_data.get('gender'):
                    response_parts.append(f"• Gender: {patient_data.get('gender')}")
                
                response_parts.append("")
            
            # 2. Get workflow state
            workflow_db = WorkflowStateDB()
            workflow_state = workflow_db.load_state(patient_id)
            
            if workflow_state:
                stage_names = {
                    1: "Registration",
                    2: "Document Upload",
                    3: "Medical History",
                    4: "Test Determination",
                    5: "Lab Coordination",
                    6: "Results Analysis",
                    7: "Admission Planning",
                    8: "Treatment Monitoring",
                    9: "Discharge",
                    10: "Analytics",
                    11: "Follow-up Care"
                }
                
                current_stage = workflow_state.get('current_stage', 1)
                stage_name = stage_names.get(current_stage, "Unknown")
                
                response_parts.append("🔄 **Current Status:**")
                response_parts.append(f"• Stage: {current_stage} - {stage_name}")
                response_parts.append(f"• Last Update: {workflow_state.get('updated_at', 'N/A')}")
                response_parts.append("")
            
            # 3. Get from Google Sheets (if available)
            if patient_data and patient_data.get('spreadsheet_id'):
                response_parts.append("📊 **Tracking:**")
                response_parts.append(f"• Your tracking spreadsheet is active")
                response_parts.append(f"• All updates are being recorded")
                response_parts.append("")
            
            # 4. Get Drive folder info
            if patient_data and patient_data.get('drive_folder_url'):
                response_parts.append("📁 **Your Documents:**")
                response_parts.append(f"• Drive Folder: {patient_data.get('drive_folder_url')}")
                response_parts.append(f"• Upload your documents here")
                response_parts.append("")
            
            # 5. 🆕 EMAIL & WORKFLOW SUPPORT (context-aware responses)
            question_lower = question.lower()
            if any(keyword in question_lower for keyword in ['email', 'not get email', 'didn\'t receive', 'no email']):
                response_parts.append("📧 **Email Support:**")
                response_parts.append("• Check your spam/junk folder")
                response_parts.append("• Email sender: pawarsamarth786@gmail.com")
                response_parts.append("• Emails are sent immediately after registration")
                response_parts.append("• If still not received, the system may need email re-authentication")
                response_parts.append("")
                response_parts.append("💡 **Troubleshooting:** Contact support if emails continue to not arrive")
                response_parts.append("")
            
            if any(keyword in question_lower for keyword in ['stage', 'progress', 'next step', 'what now']):
                response_parts.append("🚀 **Next Steps:**")
                if workflow_state and workflow_state.get('current_stage'):
                    stage = workflow_state.get('current_stage', 1)
                    if stage == 1:
                        response_parts.append("• Continue with Document Upload (Stage 2)")
                    elif stage == 2:
                        response_parts.append("• Upload required medical documents")
                    elif stage == 3:
                        response_parts.append("• Complete medical history collection")
                    else:
                        response_parts.append(f"• Continue with Stage {stage + 1}")
                else:
                    response_parts.append("• Complete patient registration first")
                response_parts.append("")
            
            if not response_parts:
                return "❌ No information found for this patient ID. Please complete registration first."
            
            return "\n".join(response_parts)
            
        except Exception as e:
            return f"❌ Error retrieving information: {str(e)}"
    
    async def _arun(self, question: str, patient_id: str) -> str:
        return self._run(question, patient_id)


class GetMyAppointmentsTool(BaseTool):
    """Get patient's appointments from database"""
    
    name: str = "get_my_appointments"
    description: str = """Get patient's appointment information including:
    - Scheduled appointments
    - Appointment dates and times
    - Doctor assignments
    - Appointment status
    
    Use when patient asks: "What are my appointments?", "When is my next appointment?", "Who is my doctor?"
    """
    args_schema: Type[BaseModel] = AskQuestionInput
    
    def _run(self, question: str, patient_id: str) -> str:
        """Get appointments from database"""
        
        try:
            from database.db_manager import DatabaseManager
            
            db = DatabaseManager()
            query = """
            SELECT 
                appointment_date,
                appointment_time,
                doctor_name,
                department,
                appointment_type,
                status,
                notes
            FROM appointments
            WHERE patient_id = %s
            ORDER BY appointment_date DESC, appointment_time DESC
            """
            
            appointments = db.execute_query(query, (patient_id,))
            
            if not appointments:
                return "📅 You don't have any appointments scheduled yet.\n\nWould you like to schedule one?"
            
            response = ["📅 **Your Appointments:**\n"]
            
            for i, apt in enumerate(appointments, 1):
                response.append(f"**Appointment {i}:**")
                response.append(f"• Date: {apt.get('appointment_date', 'N/A')}")
                response.append(f"• Time: {apt.get('appointment_time', 'N/A')}")
                response.append(f"• Doctor: {apt.get('doctor_name', 'Not assigned')}")
                response.append(f"• Department: {apt.get('department', 'N/A')}")
                response.append(f"• Type: {apt.get('appointment_type', 'N/A')}")
                response.append(f"• Status: {apt.get('status', 'N/A')}")
                
                if apt.get('notes'):
                    response.append(f"• Notes: {apt.get('notes')}")
                
                response.append("")
            
            return "\n".join(response)
            
        except Exception as e:
            return f"📅 No appointments found yet. They will appear here once scheduled.\n\n(Error: {str(e)})"
    
    async def _arun(self, question: str, patient_id: str) -> str:
        return self._run(question, patient_id)


class GetMyLabResultsTool(BaseTool):
    """Get patient's lab test results"""
    
    name: str = "get_my_lab_results"
    description: str = """Get patient's laboratory test results including:
    - Test names and values
    - Normal ranges
    - Test dates
    - Interpretation
    
    Use when patient asks: "What are my lab results?", "What were my test results?", "What's my blood sugar level?"
    """
    args_schema: Type[BaseModel] = AskQuestionInput
    
    def _run(self, question: str, patient_id: str) -> str:
        """Get lab results from database"""
        
        try:
            from database.db_manager import DatabaseManager
            
            db = DatabaseManager()
            query = """
            SELECT 
                test_name,
                test_date,
                result_value,
                unit,
                normal_range,
                status,
                notes
            FROM lab_tests
            WHERE patient_id = %s
            ORDER BY test_date DESC
            """
            
            results = db.execute_query(query, (patient_id,))
            
            if not results:
                return "🧪 No lab results available yet.\n\nTests will be ordered during your medical consultation."
            
            response = ["🧪 **Your Lab Results:**\n"]
            
            for i, test in enumerate(results, 1):
                response.append(f"**{test.get('test_name', 'N/A')}:**")
                response.append(f"• Date: {test.get('test_date', 'N/A')}")
                response.append(f"• Result: {test.get('result_value', 'N/A')} {test.get('unit', '')}")
                response.append(f"• Normal Range: {test.get('normal_range', 'N/A')}")
                response.append(f"• Status: {test.get('status', 'N/A')}")
                
                if test.get('notes'):
                    response.append(f"• Notes: {test.get('notes')}")
                
                response.append("")
            
            return "\n".join(response)
            
        except Exception as e:
            return f"🧪 No lab results found yet.\n\n(Error: {str(e)})"
    
    async def _arun(self, question: str, patient_id: str) -> str:
        return self._run(question, patient_id)


class AskMedicalQuestionTool(BaseTool):
    """
    Ask general medical questions using RAG system
    
    Uses Vector DB to search medical knowledge base
    Provides evidence-based answers with sources
    """
    
    name: str = "ask_medical_question"
    description: str = """Ask general medical questions about:
    - Diseases, symptoms, and conditions
    - Medications and side effects
    - Treatment options and procedures
    - Lab test interpretations
    - Medical terminology
    
    Use when patient asks: "What is diabetes?", "What are side effects of metformin?", "What causes high blood pressure?"
    
    This tool searches the medical knowledge base (not patient-specific data).
    """
    args_schema: Type[BaseModel] = AskQuestionInput
    
    def _run(self, question: str, patient_id: str) -> str:
        """Answer medical question using RAG"""
        
        try:
            rag_tool = MedicalRAGTool()
            
            result = rag_tool._run(
                question=question,
                collection="medical_knowledge",
                n_context=3
            )
            
            if result.get("success"):
                answer = result.get("answer", "")
                sources = result.get("sources", [])
                
                response = ["💡 **Medical Information:**\n"]
                response.append(answer)
                response.append("\n")
                response.append(f"📚 *Based on {len(sources)} medical references*")
                response.append("\n⚠️ *This is general information. Consult your doctor for personalized advice.*")
                
                return "\n".join(response)
            else:
                return f"❌ Unable to find information about: {question}\n\nPlease rephrase or ask your doctor."
                
        except Exception as e:
            return f"❌ Error searching medical knowledge: {str(e)}"
    
    async def _arun(self, question: str, patient_id: str) -> str:
        return self._run(question, patient_id)


# ============================================================================
# UNIFIED Q&A ROUTER
# ============================================================================

class ContextAwareQATool(BaseTool):
    """
    Intelligent Q&A router that determines which tool to use based on question type
    
    Routes to:
    1. GetMyInformationTool - Personal info, status, workflow position
    2. GetMyAppointmentsTool - Appointment scheduling and details
    3. GetMyLabResultsTool - Lab test results
    4. AskMedicalQuestionTool - General medical knowledge
    """
    
    name: str = "answer_patient_question"
    description: str = """Answer patient questions intelligently by routing to the appropriate data source.
    
    Automatically detects question type and searches:
    - Patient database for personal information
    - Appointments database for scheduling
    - Lab results database for test results
    - Medical knowledge base for general medical questions
    
    Maintains workflow context - patient continues from where they left off after question is answered.
    """
    args_schema: Type[BaseModel] = AskQuestionInput
    
    def _classify_question(self, question: str) -> str:
        """Classify question type using keyword matching"""
        
        question_lower = question.lower()
        
        # 🆕 PHASE 2: Doctor notes keywords (PRIORITY - check first!)
        doctor_keywords = [
            'doctor', 'diagnosis', 'treatment', 'prescription', 'medication',
            'what did the doctor say', 'doctor recommend', 'doctor prescribe',
            'my diagnosis', 'my treatment', 'treatment plan', 'doctor notes',
            'consultation', 'doctor\'s notes', 'what\'s my diagnosis'
        ]
        if any(keyword in question_lower for keyword in doctor_keywords):
            return "doctor_notes"
        
        # Personal information keywords
        if any(word in question_lower for word in ['my information', 'my details', 'my status', 'where am i', 'my stage', 'my progress', 'my id', 'my name', 'my email']):
            return "personal_info"
        
        # Appointment keywords
        if any(word in question_lower for word in ['appointment', 'schedule', 'doctor', 'when is my', 'visit', 'consultation']):
            return "appointments"
        
        # Lab results keywords
        if any(word in question_lower for word in ['lab result', 'test result', 'blood test', 'glucose', 'cholesterol', 'hba1c', 'my results', 'my tests']):
            return "lab_results"
        
        # 🆕 WORKFLOW & TECHNICAL SUPPORT KEYWORDS (check before defaulting to medical)
        workflow_keywords = [
            'email', 'not get email', 'didn\'t receive email', 'no email', 'email not working',
            'registration', 'stage', 'workflow', 'progress', 'next step', 'what now',
            'folder', 'drive', 'documents', 'upload', 'system', 'not working',
            'error', 'problem', 'issue', 'help', 'support', 'technical',
            'done', 'finished', 'complete', 'ready', 'yes', 'no', 'okay', 'ok',
            'continue', 'proceed', 'next', 'back', 'previous', 'status'
        ]
        if any(keyword in question_lower for keyword in workflow_keywords):
            return "personal_info"  # Route to personal info which handles workflow context
        
        # Check if it's actually a medical question
        medical_keywords = [
            'symptoms', 'disease', 'medication', 'treatment', 'diagnosis', 'cure',
            'pain', 'fever', 'headache', 'diabetes', 'blood pressure', 'heart',
            'infection', 'allergy', 'medicine', 'drug', 'dosage', 'side effect'
        ]
        if any(keyword in question_lower for keyword in medical_keywords):
            return "medical_knowledge"
        
        # Default to personal_info for non-medical questions during workflow
        return "personal_info"
    
    def _answer_doctor_notes_question(self, question: str, patient_id: str) -> str:
        """
        Answer questions about doctor's notes by reading from Google Doc
        
        Phase 2 Integration: Reads doctor's consultation notes from Google Docs
        """
        try:
            # Load patient's workflow state to get doc ID
            from database.db_manager import WorkflowStateDB
            
            workflow_db = WorkflowStateDB()
            state = workflow_db.load_state(patient_id)
            
            if not state or not state.get("doctor_notes_doc_id"):
                return """📋 **Doctor's Notes Not Available Yet**

Your doctor hasn't completed your consultation notes yet. This typically happens after:
1. Your initial consultation with the doctor
2. Lab results are reviewed
3. Treatment plan is finalized

**What you can do:**
- Continue with your workflow stages
- Schedule an appointment with a doctor
- Ask general medical questions

💬 **You can ask more questions anytime, or continue with your workflow.**"""
            
            # Read doctor notes from Google Doc
            from tools.google_docs_tool import ReadDoctorNotesTool
            from src.llm import llm
            
            doc_id = state["doctor_notes_doc_id"]
            read_tool = ReadDoctorNotesTool()
            
            doc_result = read_tool._run(document_id=doc_id, patient_id=patient_id)
            
            if not doc_result.get("success"):
                return f"""⚠️ **Unable to Access Doctor's Notes**

{doc_result.get('message', 'Could not read the document.')}

💬 **You can ask more questions anytime, or continue with your workflow.**"""
            
            # Get doctor notes content
            doctor_notes = doc_result.get("doctor_notes", "")
            sections = doc_result.get("sections", {})
            
            # Use LLM to generate patient-friendly answer
            answer_prompt = f"""You are a friendly medical AI assistant helping a patient understand their doctor's notes.

**Patient's Question:** "{question}"

**Doctor's Full Notes:**
{doctor_notes}

**Parsed Sections:**
- Diagnosis: {sections.get('diagnosis', 'Not specified')}
- Treatment: {sections.get('treatment', 'Not specified')}
- Follow-up: {sections.get('followup', 'Not specified')}

**Task:** Answer the patient's question in a friendly, easy-to-understand way:
1. Use simple language (avoid medical jargon)
2. Be encouraging and supportive
3. Quote specific parts from doctor's notes when relevant
4. If diagnosis is "pending", explain what's happening next
5. If treatment plan exists, explain it clearly

Generate a warm, helpful response."""
            
            try:
                llm_response = llm.invoke(answer_prompt)
                friendly_answer = llm_response.content.strip()
                
                return f"""👨‍⚕️ **Doctor's Notes Summary**

{friendly_answer}

📄 **Full consultation notes available in:** [Google Doc]({state.get('doctor_notes_doc_url', 'N/A')})

💬 **You can ask more questions anytime, or continue with your workflow.**"""
            
            except Exception as llm_error:
                # Fallback: return raw sections
                diagnosis = sections.get('diagnosis', 'Pending doctor assessment')
                treatment = sections.get('treatment', 'To be determined')
                
                return f"""👨‍⚕️ **Doctor's Notes**

**Diagnosis:**
{diagnosis}

**Treatment Plan:**
{treatment}

📄 **Full details:** [View consultation notes]({state.get('doctor_notes_doc_url', 'N/A')})

💬 **You can ask more questions anytime, or continue with your workflow.**"""
        
        except Exception as e:
            return f"""❌ **Error Accessing Doctor's Notes**

{str(e)}

**What you can do:**
- Continue with your workflow
- Ask other questions
- Contact support if issue persists

💬 **You can ask more questions anytime, or continue with your workflow.**"""
    
    def _run(self, question: str, patient_id: str) -> str:
        """Route question to appropriate tool"""
        
        try:
            # Classify question
            question_type = self._classify_question(question)
            
            # 🆕 PHASE 2: Handle doctor notes questions
            if question_type == "doctor_notes":
                return self._answer_doctor_notes_question(question, patient_id)
            
            # Route to appropriate tool
            if question_type == "personal_info":
                tool = GetMyInformationTool()
            elif question_type == "appointments":
                tool = GetMyAppointmentsTool()
            elif question_type == "lab_results":
                tool = GetMyLabResultsTool()
            else:
                tool = AskMedicalQuestionTool()
            
            # Get answer
            answer = tool._run(question=question, patient_id=patient_id)
            
            # Add continuation prompt
            continuation = "\n\n---\n\n💬 **You can ask more questions anytime, or continue with your workflow.**"
            
            return answer + continuation
            
        except Exception as e:
            return f"❌ Error answering question: {str(e)}\n\nPlease try rephrasing or contact support."
    
    async def _arun(self, question: str, patient_id: str) -> str:
        return self._run(question, patient_id)


# ============================================================================
# EXPORT ALL TOOLS
# ============================================================================

def get_all_qa_tools():
    """Get all context-aware Q&A tools"""
    return [
        GetMyInformationTool(),
        GetMyAppointmentsTool(),
        GetMyLabResultsTool(),
        AskMedicalQuestionTool(),
        ContextAwareQATool()
    ]


# ============================================================================
# TESTING
# ============================================================================

if __name__ == "__main__":
    print("=" * 80)
    print("🧪 TESTING CONTEXT-AWARE Q&A TOOLS")
    print("=" * 80)
    print()
    
    # Test with sample patient ID
    test_patient_id = "REG2025001"
    
    # Test 1: Personal information
    print("TEST 1: Personal Information")
    print("-" * 80)
    tool1 = GetMyInformationTool()
    result1 = tool1._run("What's my information?", test_patient_id)
    print(result1)
    print()
    
    # Test 2: Medical question
    print("TEST 2: Medical Knowledge")
    print("-" * 80)
    tool2 = AskMedicalQuestionTool()
    result2 = tool2._run("What are the symptoms of diabetes?", test_patient_id)
    print(result2)
    print()
    
    # Test 3: Unified router
    print("TEST 3: Intelligent Routing")
    print("-" * 80)
    router = ContextAwareQATool()
    
    questions = [
        "What's my current status?",
        "When is my next appointment?",
        "What were my lab results?",
        "What causes high blood pressure?"
    ]
    
    for q in questions:
        print(f"\nQ: {q}")
        print(f"Classified as: {router._classify_question(q)}")
    
    print()
    print("=" * 80)
    print("✅ ALL TOOLS READY!")
    print("=" * 80)
