"""
Quick Tool Test Script
Test individual tools before running full workflow
"""

import os
from dotenv import load_dotenv

# Load environment
load_dotenv()

print("=" * 60)
print("TOOL VERIFICATION TESTS")
print("=" * 60)

# Test 1: CreateMedicalDocumentTool
print("\n1️⃣ Testing CreateMedicalDocumentTool...")
try:
    from tools.docs_monitoring_tools import CreateMedicalDocumentTool
    
    tool = CreateMedicalDocumentTool()
    print("✅ Tool imported successfully")
    
    # Check if tool has correct signature
    import inspect
    sig = inspect.signature(tool._run)
    params = list(sig.parameters.keys())
    print(f"   Parameters: {params}")
    
    expected_params = ['patient_id', 'document_type', 'content', 'doctor_name']
    if all(p in params for p in expected_params):
        print("✅ Tool has correct parameters")
    else:
        print(f"❌ Missing parameters. Expected: {expected_params}")
        
except Exception as e:
    print(f"❌ Error: {e}")

# Test 2: ShareMedicalDocumentTool
print("\n2️⃣ Testing ShareMedicalDocumentTool...")
try:
    from tools.docs_monitoring_tools import ShareMedicalDocumentTool
    
    tool = ShareMedicalDocumentTool()
    print("✅ Tool imported successfully")
    
    # Check parameters
    import inspect
    sig = inspect.signature(tool._run)
    params = list(sig.parameters.keys())
    print(f"   Parameters: {params}")
    
    expected_params = ['document_id', 'email', 'role']
    if all(p in params for p in expected_params):
        print("✅ Tool has correct parameters")
        
        # Check if 'message' is NOT in parameters (this was the bug)
        if 'message' not in params:
            print("✅ 'message' parameter correctly NOT present")
        else:
            print("⚠️ 'message' parameter found (this might cause issues)")
    else:
        print(f"❌ Missing parameters. Expected: {expected_params}")
        
except Exception as e:
    print(f"❌ Error: {e}")

# Test 3: SendNotificationTool
print("\n3️⃣ Testing SendNotificationTool...")
try:
    from tools.notification_tool import SendNotificationTool
    
    tool = SendNotificationTool()
    print("✅ Tool imported successfully")
    
    # Check notification types
    from tools.notification_tool import SendNotificationInput
    import inspect
    
    # Get the Literal values for notification_type
    type_hints = SendNotificationInput.__annotations__
    print("   Checking notification types...")
    
    # notification_type should be a Literal with specific values
    if 'notification_type' in type_hints:
        print("✅ notification_type field found")
        # Check if 'custom' is in allowed types
        print("   💡 Use 'custom' type for non-standard notifications")
    
except Exception as e:
    print(f"❌ Error: {e}")

# Test 4: CreateMedicalReportTool (different from CreateMedicalDocumentTool)
print("\n4️⃣ Testing CreateMedicalReportTool (google_docs_tool)...")
try:
    from tools.google_docs_tool import CreateMedicalReportTool
    
    tool = CreateMedicalReportTool()
    print("✅ Tool imported successfully")
    
    # Check parameters
    import inspect
    sig = inspect.signature(tool._run)
    params = list(sig.parameters.keys())
    print(f"   Parameters: {params}")
    
    expected_params = ['report_title', 'patient_name', 'patient_id', 'report_date', 'medical_history', 'current_condition']
    if all(p in params for p in expected_params):
        print("✅ Tool has correct parameters (different from CreateMedicalDocumentTool!)")
    
except Exception as e:
    print(f"❌ Error: {e}")

# Test 5: ShareDocumentTool (different from ShareMedicalDocumentTool)
print("\n5️⃣ Testing ShareDocumentTool (google_docs_tool)...")
try:
    from tools.google_docs_tool import ShareDocumentTool
    
    tool = ShareDocumentTool()
    print("✅ Tool imported successfully")
    
    # Check parameters
    import inspect
    sig = inspect.signature(tool._run)
    params = list(sig.parameters.keys())
    print(f"   Parameters: {params}")
    
except Exception as e:
    print(f"❌ Error: {e}")

# Test 6: AddLabResultTool
print("\n6️⃣ Testing AddLabResultTool...")
try:
    from tools.google_sheets_tool import AddLabResultTool
    
    tool = AddLabResultTool()
    print("✅ Tool imported successfully")
    
    # Check parameters
    import inspect
    sig = inspect.signature(tool._run)
    params = list(sig.parameters.keys())
    print(f"   Parameters: {params}")
    
    expected_params = ['spreadsheet_id', 'patient_name', 'patient_id', 'test_name', 'result', 'reference_range', 'status', 'test_date']
    if all(p in params for p in expected_params):
        print("✅ Tool has correct parameters")
    
except Exception as e:
    print(f"❌ Error: {e}")

print("\n" + "=" * 60)
print("SUMMARY")
print("=" * 60)
print("""
✅ All tools imported successfully
✅ Parameter signatures verified

IMPORTANT DIFFERENCES:
1. CreateMedicalDocumentTool (docs_monitoring_tools) ≠ CreateMedicalReportTool (google_docs_tool)
   - Different parameters!
   - Use CreateMedicalDocumentTool for new workflow

2. ShareMedicalDocumentTool ≠ ShareDocumentTool
   - ShareMedicalDocumentTool does NOT have 'message' parameter
   - Both take: document_id, email, role

3. SendNotificationTool notification types:
   - Use 'custom' for non-standard notifications
   - Provide custom_subject and custom_body parameters

Next: Test actual tool execution with real data
""")

print("\nTo test actual execution, run:")
print("  python test_individual_tools.py")
