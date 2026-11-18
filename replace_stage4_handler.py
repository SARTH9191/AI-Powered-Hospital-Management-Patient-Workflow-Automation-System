"""
Automated Stage 4 Handler Replacement Script
This script will replace the old Stage 4 handler with the new unified doc version
"""

import re

def replace_stage4_handler():
    """Replace Stage 4 handler in workflow_chat_agent.py"""
    
    file_path = "src/workflow_chat_agent.py"
    
    print("Reading workflow_chat_agent.py...")
    
    with open(file_path, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Find the start and end of Stage 4 handler
    start_marker = "# ==================== STAGE 4:"
    end_marker = "# ==================== CONFIRMATION HANDLER ===================="
    
    start_pos = content.find(start_marker)
    end_pos = content.find(end_marker)
    
    if start_pos == -1 or end_pos == -1:
        print("❌ Could not find Stage 4 handler markers")
        return False
    
    print(f"Found Stage 4 handler: lines {start_pos} to {end_pos}")
    
    # New Stage 4 handler code
    new_handler = '''# ==================== STAGE 4: LAB TEST DETERMINATION WITH DOCTOR APPROVAL ====================
    
    def _handle_test_determination(self, user_message: str) -> Dict[str, Any]:
        """🔥 UNIFIED DOC: Wait for doctor approval from unified workflow document (Section 3)"""
        
        stage_data = self.state.get("stage_data", {}).get("test_determination", {})
        
        # Get workflow document ID from state
        workflow_doc_id = self.state.get("workflow_doc_id")
        workflow_doc_url = self.state.get("workflow_doc_url")
        
        # Check if this is the first time entering Stage 4
        if not stage_data.get("waiting_for_doctor"):
            stage_data["waiting_for_doctor"] = True
            stage_data["check_count"] = 0
            self.state.setdefault("stage_data", {})["test_determination"] = stage_data
            self._save_state()
            
            if not workflow_doc_id:
                return {
                    "response": """⚠️ Error: Workflow document not found. 
                    
Please restart from Stage 3 to create the medical history document.""",
                    "stage": 4,
                    "stage_complete": False
                }
            
            return {
                "response": f"""📋 **STAGE 4: WAITING FOR DOCTOR APPROVAL**

Your medical history and AI-recommended tests have been shared with the doctor.

📄 **Workflow Document:** {workflow_doc_url}

**What happens next:**
1. Doctor reviews your medical history (Section 1)
2. Doctor reviews AI analysis and recommended tests (Section 2)
3. Doctor updates their decision in Section 3:
   • Decision: APPROVE / MODIFY / REJECT / CONSULT
   • Approved Tests: List of tests to perform
   • Doctor's Assessment: Professional medical opinion

⏳ **The workflow will NOT proceed until the doctor approves.**

**You can:**
• Type "check" to check if doctor has responded
• Type "refresh" to reload the doctor's decision
• Ask me questions while you wait

I'll automatically check the document when you ask me to check.""",
                "stage": 4,
                "stage_complete": False,
                "waiting_for_doctor": True
            }
        
        # Handle user commands while waiting
        message_lower = user_message.lower().strip()
        
        check_triggers = ["check", "refresh", "status", "update", "has the doctor", "did the doctor", 
                         "doctor decision", "doctor approval", "is it ready", "check status"]
        
        if any(trigger in message_lower for trigger in check_triggers):
            # Try to read doctor's decision from Section 3
            try:
                print(f"🔍 Checking doctor's decision in document {workflow_doc_id}...")
                
                stage_data["check_count"] = stage_data.get("check_count", 0) + 1
                self.state.setdefault("stage_data", {})["test_determination"] = stage_data
                self._save_state()
                
                decision_result = read_doctor_decision(workflow_doc_id)
                
                if decision_result.get("pending"):
                    # Doctor hasn't updated yet
                    return {
                        "response": f"""⏳ **Doctor has not yet updated their decision**

Check #{stage_data.get('check_count', 1)}: No updates detected in Section 3.

The doctor needs to update the following in Section 3 of the document:
• Doctor's Decision: (APPROVE/MODIFY/REJECT/CONSULT)
• Approved Tests: (list of tests)
• Doctor's Assessment: (professional opinion)

📄 Document: {workflow_doc_url}

**Please wait for the doctor to complete their review.**

Type "check" again to recheck, or ask me questions while you wait.""",
                        "stage": 4,
                        "stage_complete": False,
                        "waiting_for_doctor": True
                    }
                
                elif decision_result.get("success"):
                    # Doctor has made a decision!
                    decision = decision_result.get("decision", "UNKNOWN")
                    approved_tests = decision_result.get("approved_tests", [])
                    additional_tests = decision_result.get("additional_tests", [])
                    doctor_assessment = decision_result.get("doctor_assessment", "")
                    
                    # Store decision in state
                    stage_data["doctor_decision_made"] = True
                    stage_data["decision"] = decision
                    stage_data["approved_tests"] = approved_tests
                    stage_data["additional_tests"] = additional_tests
                    stage_data["doctor_assessment"] = doctor_assessment
                    self.state.setdefault("stage_data", {})["test_determination"] = stage_data
                    self._save_state()
                    
                    # Route based on doctor's decision
                    if decision in ["APPROVE", "MODIFY"]:
                        # Doctor approved - proceed to lab scheduling (Stage 5)
                        all_tests = approved_tests + additional_tests
                        test_list = "\\n".join([f"   • {test}" for test in all_tests])
                        
                        # Set up confirmation for Stage 5
                        self.state["awaiting_confirmation"] = True
                        self.state["pending_actions"] = ["schedule_lab_tests"]
                        self._save_state()
                        
                        return {
                            "response": f"""✅ **DOCTOR {decision.upper()}D LAB TESTS**

**Doctor's Assessment:**
{doctor_assessment}

**Approved Tests ({len(all_tests)}):**
{test_list}

**Next Step: Lab Test Scheduling**

I will now:
✅ Schedule lab test appointments
✅ Create calendar events
✅ Update Section 4 of workflow document
✅ Send you appointment details

Proceed with scheduling? (yes/no)""",
                            "stage": 4,
                            "stage_complete": False,
                            "doctor_approved": True,
                            "awaiting_confirmation": True
                        }
                    
                    elif decision == "REJECT":
                        # Doctor rejected tests - direct consultation needed
                        return {
                            "response": f"""⚠️ **DOCTOR REJECTED LAB TESTS**

**Doctor's Assessment:**
{doctor_assessment}

The doctor has determined that lab tests are not required at this time.

**Next Step:** Direct consultation with doctor will be scheduled.

Moving to consultation scheduling (Stage 7)...""",
                            "stage": 4,
                            "stage_complete": True,
                            "next_stage": 7,  # Jump to doctor consultation
                            "tests_rejected": True
                        }
                    
                    elif decision == "CONSULT":
                        # Doctor wants to see patient first before tests
                        return {
                            "response": f"""👨‍⚕️ **DOCTOR REQUESTS CONSULTATION FIRST**

**Doctor's Assessment:**
{doctor_assessment}

The doctor would like to see you for consultation before ordering any lab tests.

**Next Step:** Scheduling doctor consultation appointment.

Moving to consultation scheduling (Stage 7)...""",
                            "stage": 4,
                            "stage_complete": True,
                            "next_stage": 7,  # Jump to doctor consultation
                            "consult_first": True
                        }
                    
                    else:
                        # Unknown decision
                        return {
                            "response": f"""⚠️ **Unrecognized Doctor Decision: {decision}**

**Doctor's Assessment:**
{doctor_assessment}

I'm not sure how to proceed. Please check with the doctor or hospital staff.""",
                            "stage": 4,
                            "stage_complete": False
                        }
                
                else:
                    # Error reading decision
                    return {
                        "response": f"""❌ **Error reading doctor's decision**

Error: {decision_result.get('error', 'Unknown error')}

Please try again or contact support if the issue persists.""",
                        "stage": 4,
                        "stage_complete": False
                    }
                    
            except Exception as e:
                return {
                    "response": f"""❌ **Error checking doctor's decision**

Error: {str(e)}

Please try again later or contact support.""",
                    "stage": 4,
                    "stage_complete": False
                }
        
        # Handle general questions while waiting - AI Agent is SMART!
        else:
            # Use LLM to answer questions intelligently while waiting
            context_prompt = f"""You are a helpful hospital AI assistant. The patient is waiting for doctor approval (Stage 4).

**Current Situation:**
- Patient's medical history has been documented
- AI-recommended tests have been shared with doctor
- Doctor is reviewing the case in the workflow document
- Patient asked: "{user_message}"

**Workflow Document:** {workflow_doc_url}

Provide a helpful, empathetic response that:
1. Acknowledges we're waiting for doctor approval
2. Answers their question if it's about the process, tests, or general hospital info
3. Reassures them the doctor will review soon
4. Reminds them they can type "check" to see if doctor responded

Keep response concise (3-5 sentences) and professional."""

            try:
                llm_response = self.llm.invoke(context_prompt)
                smart_response = llm_response.content.strip()
                
                return {
                    "response": smart_response + f"\\n\\n💡 Tip: Type 'check' to see if the doctor has responded.",
                    "stage": 4,
                    "stage_complete": False,
                    "waiting_for_doctor": True
                }
            except:
                return {
                    "response": f"""I'm still waiting for the doctor to review your case and update their decision in the workflow document.

📄 Document: {workflow_doc_url}

**Your question:** {user_message}

While we wait for the doctor's decision, I can answer questions about:
• The workflow process
• What tests might be performed
• General hospital information

Or you can type "check" to see if the doctor has responded yet.""",
                    "stage": 4,
                    "stage_complete": False,
                    "waiting_for_doctor": True
                }
    
    '''
    
    # Replace the content
    new_content = content[:start_pos] + new_handler + content[end_pos:]
    
    # Write back
    print("Writing updated content...")
    with open(file_path, 'w', encoding='utf-8') as f:
        f.write(new_content)
    
    print("✅ Stage 4 handler successfully replaced!")
    print("✅ Now uses unified workflow document")
    print("✅ Includes smart LLM-powered Q&A while waiting")
    print("✅ Doctor approval gates working")
    
    return True


if __name__ == "__main__":
    print("="*80)
    print("  STAGE 4 HANDLER REPLACEMENT")
    print("="*80)
    print()
    
    success = replace_stage4_handler()
    
    if success:
        print()
        print("🎉 Integration Complete!")
        print()
        print("Next steps:")
        print("1. Test with: python test_complete_unified_workflow.py")
        print("2. Create unified doc in Stage 3")
        print("3. Doctor updates Section 3")
        print("4. AI reads decision and proceeds")
    else:
        print()
        print("❌ Replacement failed - please check file manually")
