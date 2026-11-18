"""
Individual Tool Execution Tests
Test each tool with real execution to verify they work correctly

Run this AFTER verify_tool_signatures.py passes
"""

import os
from dotenv import load_dotenv
from datetime import datetime

# Load environment
load_dotenv()

print("=" * 70)
print("INDIVIDUAL TOOL EXECUTION TESTS")
print("=" * 70)
print("\n⚠️ WARNING: These tests will create real documents/records!")
print("Press Ctrl+C to cancel, or wait 3 seconds to continue...")
import time
time.sleep(3)

# Test 1: CreateMedicalDocumentTool
print("\n" + "=" * 70)
print("TEST 1: CreateMedicalDocumentTool")
print("=" * 70)
try:
    from tools.docs_monitoring_tools import CreateMedicalDocumentTool
    
    tool = CreateMedicalDocumentTool()
    
    test_content = f"""TEST MEDICAL DOCUMENT

Patient Information:
• Patient ID: TEST-{datetime.now().strftime('%Y%m%d-%H%M%S')}
• Test Date: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}

This is a test document to verify the CreateMedicalDocumentTool is working correctly.

Medical Notes:
- Tool execution test
- Parameter validation
- Document creation verification

--- END OF TEST DOCUMENT ---
"""
    
    print("Executing tool with test data...")
    result = tool._run(
        patient_id=f"TEST-{datetime.now().strftime('%Y%m%d')}",
        document_type="test_document",
        content=test_content,
        doctor_name="Test Doctor"
    )
    
    print("\n📄 Result:")
    print(result)
    
    # Check for success
    if "✅" in result and "Medical Document Created Successfully" in result:
        print("\n✅ TEST PASSED: Document created successfully")
        
        # Try to extract document ID
        import re
        doc_id_match = re.search(r'Document ID:\*\*\s+([a-zA-Z0-9_-]+)', result)
        if doc_id_match:
            doc_id = doc_id_match.group(1)
            print(f"✅ Document ID extracted: {doc_id}")
            
            # Save for next test
            with open("test_doc_id.txt", "w") as f:
                f.write(doc_id)
            print("✅ Document ID saved to test_doc_id.txt")
        else:
            print("⚠️ Could not extract document ID from result")
    else:
        print("\n❌ TEST FAILED: Document creation failed")
        
except Exception as e:
    print(f"\n❌ TEST FAILED with exception: {e}")
    import traceback
    traceback.print_exc()

# Test 2: ShareMedicalDocumentTool
print("\n" + "=" * 70)
print("TEST 2: ShareMedicalDocumentTool")
print("=" * 70)

# Check if we have a document ID from previous test
if os.path.exists("test_doc_id.txt"):
    try:
        with open("test_doc_id.txt", "r") as f:
            doc_id = f.read().strip()
        
        print(f"Using document ID from previous test: {doc_id}")
        
        from tools.docs_monitoring_tools import ShareMedicalDocumentTool
        
        tool = ShareMedicalDocumentTool()
        
        # Use your email for testing
        test_email = os.getenv("TEST_EMAIL", "pawarsamarth786@gmail.com")
        
        print(f"Sharing document with: {test_email}")
        result = tool._run(
            document_id=doc_id,
            email=test_email,
            role="writer"
        )
        
        print("\n📄 Result:")
        print(result)
        
        if "✅" in result and "Document Shared Successfully" in result:
            print("\n✅ TEST PASSED: Document shared successfully")
        else:
            print("\n❌ TEST FAILED: Document sharing failed")
            
    except Exception as e:
        print(f"\n❌ TEST FAILED with exception: {e}")
        import traceback
        traceback.print_exc()
else:
    print("⚠️ Skipping test - no document ID from previous test")
    print("   Run Test 1 first to create a document")

# Test 3: SendNotificationTool with custom type
print("\n" + "=" * 70)
print("TEST 3: SendNotificationTool (custom notification)")
print("=" * 70)
try:
    from tools.notification_tool import SendNotificationTool
    
    tool = SendNotificationTool()
    
    print("Sending test notification...")
    result = tool._run(
        recipient_id=f"TEST-{datetime.now().strftime('%Y%m%d')}",
        notification_type="custom",
        channel=["email"],
        template_data={
            "patient_name": "Test Patient",
            "test_date": datetime.now().strftime('%Y-%m-%d')
        },
        custom_subject="Tool Test Notification",
        custom_body="This is a test notification to verify SendNotificationTool is working correctly."
    )
    
    print("\n📄 Result:")
    print(result)
    
    # Note: This might fail if patient doesn't exist in DB, that's OK for this test
    if "notification sent" in str(result).lower() or "success" in str(result).lower():
        print("\n✅ TEST PASSED: Notification tool executed successfully")
    else:
        print("\n⚠️ Result: Tool executed but check if patient exists in database")
        
except Exception as e:
    print(f"\n❌ TEST FAILED with exception: {e}")
    import traceback
    traceback.print_exc()

# Test 4: AddLabResultTool
print("\n" + "=" * 70)
print("TEST 4: AddLabResultTool")
print("=" * 70)
try:
    from tools.google_sheets_tool import AddLabResultTool
    
    tool = AddLabResultTool()
    
    # Get sheet ID from environment
    sheet_id = os.getenv("LAB_RESULTS_MONITORING_SHEET_ID", "default_sheet")
    
    print(f"Using sheet ID: {sheet_id}")
    print("Adding test lab result...")
    
    result = tool._run(
        spreadsheet_id=sheet_id,
        patient_name="Test Patient",
        patient_id=f"TEST-{datetime.now().strftime('%Y%m%d')}",
        test_name="Tool Verification Test",
        result="TEST",
        reference_range="N/A",
        status="COMPLETED",
        test_date=datetime.now().strftime('%Y-%m-%d')
    )
    
    print("\n📄 Result:")
    print(result)
    
    if "success" in str(result).lower() or "added" in str(result).lower():
        print("\n✅ TEST PASSED: Lab result added successfully")
    else:
        print("\n⚠️ Check result above - tool executed")
        
except Exception as e:
    print(f"\n❌ TEST FAILED with exception: {e}")
    import traceback
    traceback.print_exc()

print("\n" + "=" * 70)
print("TEST SUMMARY")
print("=" * 70)
print("""
If all tests passed:
✅ CreateMedicalDocumentTool working
✅ ShareMedicalDocumentTool working  
✅ SendNotificationTool working
✅ AddLabResultTool working

Your workflow should now work correctly!

Next steps:
1. Check your Google Drive for the test document
2. Check your email for the test notification (if patient exists)
3. Check your Google Sheet for the test lab result
4. Clean up test data if needed
5. Run the full workflow test

If any tests failed:
- Check error messages above
- Verify credentials are set up correctly
- Check .env file has correct sheet IDs
- Verify Google API permissions
""")

# Cleanup
print("\n💡 Cleanup: test_doc_id.txt saved for reference")
print("   You can manually delete the test document from Google Drive")
