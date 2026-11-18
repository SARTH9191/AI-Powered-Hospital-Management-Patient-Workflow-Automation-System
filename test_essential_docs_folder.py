"""
Quick test to verify Essential_Documents folder naming update
"""

from tools.google_drive_tool import CreatePatientFolderTool

print("\n" + "="*70)
print("🧪 Testing Updated Folder Structure: 2_Essential_Documents")
print("="*70)

try:
    folder_tool = CreatePatientFolderTool()
    result = folder_tool._run(
        folder_name="TEST_Essential_Docs_20250115"
    )
    
    print(result)
    
    # Check if new folder name is present
    if "2_Essential_Documents" in result:
        print("\n✅ SUCCESS: Folder renamed to '2_Essential_Documents'")
    else:
        print("\n❌ ERROR: Still using old folder name")
    
    # Check if all 5 folders are present
    expected_folders = [
        '1_Medical_History',
        '2_Essential_Documents',
        '3_Lab_Reports',
        '4_Prescriptions',
        '5_Consultation_Notes'
    ]
    
    print("\n📋 Folder Verification:")
    for folder in expected_folders:
        if folder in result:
            print(f"   ✅ {folder}")
        else:
            print(f"   ❌ {folder} - MISSING!")
    
except Exception as e:
    print(f"❌ Error: {e}")
    import traceback
    traceback.print_exc()

print("\n" + "="*70)
