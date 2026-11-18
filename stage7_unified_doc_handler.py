"""
Stage 7 Handler Replacement - Unified Document Approach
Replaces Google Sheets with Section 6 reading from unified workflow document
"""

NEW_STAGE7_HANDLER = '''
    def _handle_doctor_consultation(self, user_message: str) -> Dict[str, Any]:
        """🔥 UNIFIED DOC: Handle doctor consultation and read Section 6"""
        
        stage_data = self.state.get("stage_data", {}).get("doctor_consultation", {})
        results_data = self.state.get("stage_data", {}).get("results_analysis", {})
        registration_data = self.state.get("stage_data", {}).get("registration", {})
        
        # Get unified workflow document from state
        workflow_doc_id = self.state.get("workflow_doc_id")
        workflow_doc_url = self.state.get("workflow_doc_url")
        patient_id = registration_data.get("patient_id", "Unknown")
        patient_name = registration_data.get("full_name", "Patient")
        
        if not workflow_doc_id:
            return {
                "response": "⚠️ Workflow document not found. Please contact support.",
                "stage": 7,
                "stage_complete": False
            }
        
        # Step 1: First entry - Show consultation scheduling message
        if not stage_data.get("consultation_scheduled"):
            # Update Section 6 with consultation scheduled header
            from tools.unified_workflow_doc_tool import update_doc_section
            
            section_6_header = f"""
CONSULTATION APPOINTMENT SCHEDULED:
📅 Status: Scheduling in progress
📋 Purpose: Review lab results and determine treatment plan

The doctor will review:
• Your lab test results (Section 5)
• Your medical history (Section 1)
• Current symptoms and assessment
• Treatment options

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
[Doctor will update below after consultation]

Updated by: AI Agent
Last Updated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
"""
            
            try:
                update_result = update_doc_section(
                    workflow_doc_id, 
                    "6: POST-LAB CONSULTATION", 
                    section_6_header
                )
                
                if update_result.get('success'):
                    print("✅ Section 6 initialized with consultation header")
            except Exception as e:
                print(f"⚠️ Failed to update Section 6: {str(e)}")
            
            stage_data["consultation_scheduled"] = True
            stage_data["waiting_for_doctor"] = True
            self.state.setdefault("stage_data", {})["doctor_consultation"] = stage_data
            self._save_state()
            
            return {
                "response": f"""📅 **DOCTOR CONSULTATION SCHEDULED**

Your lab results are ready for doctor review.

📄 **Consultation Document:** {workflow_doc_url}

🏥 **Review Process:**
The doctor will review your complete medical information:
• Lab results (Section 5)
• Medical history (Section 1)
• AI analysis (Section 2)
• Symptoms and assessment

Once the review is complete, the doctor will update Section 6 with:
• Diagnosis
• Treatment plan
• Admission requirements (if any)
• Prescription details
• Follow-up schedule

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

⏳ **WAITING FOR DOCTOR'S CONSULTATION**

💬 **While you wait:**
Feel free to ask me any questions about your test results, treatment process, or general health concerns. I'm here to help!

🔍 **Check Status:**
Type **"check"** anytime to see if the doctor has completed your consultation.

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━""",
                "stage": 7,
                "stage_complete": False
            }
        
        # Step 2: User is waiting for doctor's consultation decision
        if stage_data.get("waiting_for_doctor"):
            message_lower = user_message.lower()
            
            # User types "check" - Read Section 6 for doctor's decision
            if "check" in message_lower:
                print(f"🔍 User checking for doctor consultation updates...")
                
                try:
                    from tools.unified_workflow_doc_tool import read_doctor_consultation
                    consultation_result = read_doctor_consultation(workflow_doc_id)
                    
                    if consultation_result.get("pending"):
                        return {
                            "response": f"""⏳ **Doctor consultation still in progress...**

The doctor hasn't completed the consultation review yet.

📄 **Document:** {workflow_doc_url}
📍 **Section to check:** Section 6 (POST-LAB CONSULTATION)

💡 **Tip:** The doctor will update Section 6 with:
• Diagnosis
• Treatment plan
• Admission requirements
• Prescription details

Please check back in a few minutes, or I'll notify you when it's ready!

💬 In the meantime, feel free to ask me any questions!""",
                            "stage": 7,
                            "stage_complete": False
                        }
                    
                    # ✅ Doctor has completed consultation! Parse Section 6
                    print("✅ Doctor consultation complete! Parsing Section 6...")
                    
                    diagnosis = consultation_result.get("diagnosis", "")
                    treatment_decision = consultation_result.get("treatment_decision", "")
                    treatment_plan = consultation_result.get("treatment_plan", "")
                    requires_admission = consultation_result.get("requires_admission", False)
                    requires_prescription = consultation_result.get("requires_prescription", False)
                    requires_followup = consultation_result.get("requires_followup", False)
                    additional_notes = consultation_result.get("additional_notes", "")
                    
                    # Store in stage data
                    stage_data["waiting_for_doctor"] = False
                    stage_data["consultation_complete"] = True
                    stage_data["diagnosis"] = diagnosis
                    stage_data["treatment_decision"] = treatment_decision
                    stage_data["treatment_plan"] = treatment_plan
                    stage_data["requires_admission"] = requires_admission
                    stage_data["requires_prescription"] = requires_prescription
                    stage_data["requires_followup"] = requires_followup
                    self.state.setdefault("stage_data", {})["doctor_consultation"] = stage_data
                    self._save_state()
                    
                    # Route based on doctor's decision
                    if requires_admission:
                        return {
                            "response": f"""✅ **DOCTOR CONSULTATION COMPLETE**

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

👨‍⚕️ **DIAGNOSIS:** {diagnosis}

🏥 **DECISION: HOSPITAL ADMISSION REQUIRED**

The doctor has determined that hospital admission is necessary for your condition.

📋 **Treatment Plan:**
{treatment_plan}

{f"📝 **Additional Notes:**{chr(10)}{additional_notes}" if additional_notes else ""}

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

📍 **Next Steps:**
• Check bed availability
• Complete insurance verification
• Schedule admission date
• Prepare admission documents

Type **"continue"** to proceed with admission planning...""",
                            "stage": 7,
                            "stage_complete": True,
                            "next_stage": 8  # Go to admission execution
                        }
                    
                    elif requires_prescription and requires_followup:
                        return {
                            "response": f"""✅ **DOCTOR CONSULTATION COMPLETE**

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

👨‍⚕️ **DIAGNOSIS:** {diagnosis}

✅ **DECISION: OUTPATIENT TREATMENT**

Good news! You can be treated without hospital admission.

📋 **Treatment Plan:**
{treatment_plan}

{f"📝 **Additional Notes:**{chr(10)}{additional_notes}" if additional_notes else ""}

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

📍 **Next Steps:**
• Review prescription details (Section 7)
• Schedule follow-up appointment
• Receive medication instructions
• Get home care guidelines

Type **"continue"** to proceed with prescription and follow-up planning...""",
                            "stage": 7,
                            "stage_complete": True,
                            "next_stage": 11  # Go to follow-up care
                        }
                    
                    elif requires_followup:
                        return {
                            "response": f"""✅ **DOCTOR CONSULTATION COMPLETE**

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

👨‍⚕️ **DIAGNOSIS:** {diagnosis}

📅 **DECISION: FOLLOW-UP CONSULTATION RECOMMENDED**

The doctor would like to schedule a follow-up appointment to monitor your progress.

📋 **Treatment Plan:**
{treatment_plan}

{f"📝 **Additional Notes:**{chr(10)}{additional_notes}" if additional_notes else ""}

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

📍 **Next Steps:**
• Schedule follow-up appointment
• Review any monitoring instructions
• Continue current care plan

Type **"continue"** to proceed with follow-up scheduling...""",
                            "stage": 7,
                            "stage_complete": True,
                            "next_stage": 11  # Go to follow-up care
                        }
                    
                    else:
                        # Default: proceed to follow-up
                        return {
                            "response": f"""✅ **DOCTOR CONSULTATION COMPLETE**

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

👨‍⚕️ **DIAGNOSIS:** {diagnosis}

📋 **Treatment Plan:**
{treatment_plan}

{f"📝 **Additional Notes:**{chr(10)}{additional_notes}" if additional_notes else ""}

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

Type **"continue"** to proceed...""",
                            "stage": 7,
                            "stage_complete": True,
                            "next_stage": 11
                        }
                    
                except Exception as e:
                    print(f"❌ Error reading Section 6: {str(e)}")
                    return {
                        "response": f"""⚠️ **Error reading consultation results**

I encountered an error while trying to read the doctor's consultation notes from Section 6.

Error details: {str(e)}

Please try typing **"check"** again, or contact support if the issue persists.""",
                        "stage": 7,
                        "stage_complete": False
                    }
            
            # User asks questions while waiting - Smart LLM response
            else:
                print(f"🧠 User asked while waiting: {user_message}")
                
                # Build context for LLM
                context_prompt = f"""You are a helpful medical AI assistant. A patient is waiting for their doctor consultation.

**Patient Context:**
- Name: {patient_name}
- Patient ID: {patient_id}
- Current Stage: Waiting for doctor consultation (Stage 7)
- Lab results have been completed and shared with doctor
- Doctor is reviewing results and will update treatment plan

**Patient's Question:** "{user_message}"

**Your Task:**
Provide a helpful, empathetic response to the patient's question. Keep it:
- Professional but warm
- Informative without making medical diagnoses
- Encouraging and supportive
- Clear that the doctor will provide the official treatment plan

If the question is about:
- Test results: Explain general information, but note doctor will interpret specifically
- Treatment: Note that doctor will decide the best treatment plan
- Waiting time: Reassure that doctor is carefully reviewing their case
- Symptoms: Acknowledge concerns and note doctor will address them
"""
                
                try:
                    llm_response = self.llm.invoke(context_prompt)
                    smart_answer = llm_response.content.strip()
                    
                    return {
                        "response": f"""{smart_answer}

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
💡 Remember: Type **"check"** to see if the doctor has completed your consultation.
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━""",
                        "stage": 7,
                        "stage_complete": False
                    }
                    
                except Exception as e:
                    print(f"⚠️ LLM response failed: {str(e)}")
                    return {
                        "response": f"""I understand your concern about: "{user_message}"

The doctor is currently reviewing your case and will provide detailed guidance soon.

Type **"check"** to see if the consultation is complete, and I'll help you with the next steps!""",
                        "stage": 7,
                        "stage_complete": False
                    }
        
        # Step 3: Consultation complete, waiting for user to proceed
        if stage_data.get("consultation_complete"):
            if "continue" in user_message.lower() or "proceed" in user_message.lower():
                return {
                    "response": "Moving to next stage...",
                    "stage": 7,
                    "stage_complete": True,
                    "next_stage": stage_data.get("requires_admission") and 8 or 11
                }
        
        # Default: waiting for input
        return {
            "response": "Please type **'check'** to see if the doctor has completed your consultation, or ask me any questions!",
            "stage": 7,
            "stage_complete": False
        }
'''

print("Stage 7 handler code prepared for replacement")
print("\n" + "="*60)
print("This will replace the Google Sheets approach with:")
print("1. Section 6 initialization on first entry")
print("2. Waiting gate (like Stage 4)")
print("3. 'check' command to read Section 6")
print("4. Smart LLM Q&A while waiting")
print("5. Decision routing based on Section 6 content")
print("="*60)
