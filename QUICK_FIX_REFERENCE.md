# 🔧 Quick Fix Reference - Tool Calling Patterns

## Common Tool Issues & Solutions

### Issue 1: Wrong Tool Import
```python
# ❌ WRONG - Different tools with similar names
from tools.google_docs_tool import CreateMedicalDocumentTool  # Wrong one!

# ✅ CORRECT - Use the right tool
from tools.docs_monitoring_tools import CreateMedicalDocumentTool
```

### Issue 2: Parameter Mismatch
```python
# ❌ WRONG - Using CreateMedicalReportTool parameters
tool._run(
    report_title="Report",
    patient_name="John Doe",
    report_date="2025-11-03",
    medical_history="...",
    current_condition="...",
    lab_results="...",
    doctor_notes="..."
)

# ✅ CORRECT - CreateMedicalDocumentTool parameters
tool._run(
    patient_id="PAT123",
    document_type="admission_notes",
    content="Full document content here...",
    doctor_name="Dr. Smith"
)
```

### Issue 3: Placeholder Document IDs
```python
# ❌ WRONG - Using placeholder string
share_tool._run(
    document_id="generated_medical_report",  # This doesn't exist!
    email="doctor@hospital.com",
    role="writer"
)

# ✅ CORRECT - Extract real document ID
import re
doc_id_match = re.search(r'Document ID:\*\*\s+([a-zA-Z0-9_-]+)', doc_result)
if doc_id_match:
    document_id = doc_id_match.group(1)
    
    share_tool._run(
        document_id=document_id,  # Real ID!
        email="doctor@hospital.com",
        role="writer"
    )
```

### Issue 4: Invalid Notification Type
```python
# ❌ WRONG - "doctor_approval" not in allowed types
notification_tool._run(
    recipient_id="PAT123",
    notification_type="doctor_approval",  # Invalid!
    channel=["email"],
    template_data={...}
)

# ✅ CORRECT - Use "custom" type
notification_tool._run(
    recipient_id="PAT123",
    notification_type="custom",  # Valid!
    channel=["email"],
    template_data={...},
    custom_subject="Doctor Approval Confirmed",
    custom_body="Your case has been approved..."
)
```

### Issue 5: Invalid Tool Parameters
```python
# ❌ WRONG - "message" parameter doesn't exist
share_tool._run(
    document_id="doc123",
    email="user@example.com",
    role="reader",
    message="Your document is ready"  # Invalid parameter!
)

# ✅ CORRECT - Only use valid parameters
share_tool._run(
    document_id="doc123",
    email="user@example.com",
    role="reader"  # Only these 3 parameters
)
```

## Tool Parameter Quick Reference

### CreateMedicalDocumentTool (docs_monitoring_tools)
```python
tool._run(
    patient_id: str,
    document_type: str,  # "admission_notes", "treatment_plan", "discharge_summary", "consultation_notes"
    content: str,
    doctor_name: Optional[str]
)
```

### CreateMedicalReportTool (google_docs_tool)
```python
tool._run(
    report_title: str,
    patient_name: str,
    patient_id: str,
    report_date: str,
    medical_history: str,
    current_condition: str,
    lab_results: Optional[str],
    doctor_notes: Optional[str]
)
```

### ShareMedicalDocumentTool / ShareDocumentTool
```python
tool._run(
    document_id: str,  # Must be real Google Docs ID
    email: str,
    role: str  # "reader", "writer", or "commenter"
)
```

### SendNotificationTool
```python
tool._run(
    recipient_id: str,
    notification_type: str,  # See allowed types below
    channel: List[str],  # ["email", "sms", "in_app"]
    template_data: dict,
    custom_subject: Optional[str],  # Required if type="custom"
    custom_body: Optional[str],     # Required if type="custom"
    priority: Optional[str]
)

# Allowed notification_type values:
# "appointment_reminder", "critical_results", "approval_request",
# "billing_reminder", "prescription_refill", "appointment_confirmation",
# "test_results_ready", "welcome", "custom"
```

### AddLabResultTool
```python
tool._run(
    spreadsheet_id: str,
    patient_name: str,
    patient_id: str,
    test_name: str,
    result: str,
    reference_range: str,
    status: str,  # "Normal", "Abnormal", "Critical", "PENDING", etc.
    test_date: str  # "YYYY-MM-DD"
)
```

## Extracting Document IDs from Responses

### From CreateMedicalDocumentTool
```python
import re
doc_id_match = re.search(r'Document ID:\*\*\s+([a-zA-Z0-9_-]+)', result)
if doc_id_match:
    document_id = doc_id_match.group(1)
```

### From CreateMedicalReportTool
```python
import re
link_match = re.search(r'https://docs\.google\.com/document/d/([a-zA-Z0-9_-]+)', result)
if link_match:
    document_id = link_match.group(1)
```

## Testing Workflow

### Step 1: Verify Tool Signatures
```bash
python verify_tool_signatures.py
```

### Step 2: Test Individual Tools
```bash
python test_individual_tools.py
```

### Step 3: Test Full Workflow
```bash
# Start backend
python main.py

# In another terminal, test the workflow
python test_complete_workflow_integration.py
```

## Common Debugging Steps

1. **Tool not importing:**
   - Check file path
   - Verify tool is in correct file
   - Check for typos in import

2. **Parameter errors:**
   - Run `verify_tool_signatures.py` to see expected parameters
   - Compare your code with the tool's `_run()` signature
   - Check for typos in parameter names

3. **Document ID not found:**
   - Print the tool result to see what's returned
   - Check regex pattern for extracting ID
   - Verify tool actually created the document

4. **Sharing fails:**
   - Make sure document ID is real (not placeholder)
   - Check email address is valid
   - Verify role is "reader", "writer", or "commenter"

5. **Notification fails:**
   - Check notification_type is in allowed list
   - Use "custom" type with custom_subject and custom_body
   - Verify patient exists in database

## Quick Checklist Before Running Workflow

- [ ] All tools import without errors
- [ ] Tool parameters match the `_run()` signature
- [ ] No placeholder document IDs in code
- [ ] Notification types are valid
- [ ] Document ID extraction regex patterns are correct
- [ ] Error handling is in place for all tool calls
- [ ] `.env` file has all required IDs (sheet IDs, etc.)
- [ ] Google API credentials are set up correctly

---

**Last Updated:** November 3, 2025
**Status:** All fixes applied and documented
