#!/usr/bin/env python3
"""
Debug the exact import error in document upload handler
"""

import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), 'src'))

# Test all the imports that should work
print("🔍 Testing imports...")

try:
    from database.db_manager import PatientDB
    print("✅ PatientDB imported successfully")
    
    # Test database connection
    patient_db = PatientDB()
    print("✅ PatientDB instance created successfully")
    
    # Test the specific patient
    patient_info = patient_db.get_patient_by_id("REG2025214740")
    print(f"✅ Patient info retrieved: {patient_info is not None}")
    
    if patient_info:
        print(f"   Drive Folder ID: {patient_info.get('drive_folder_id')}")
        print(f"   Drive Folder URL: {patient_info.get('drive_folder_url')}")
        
except Exception as e:
    print(f"❌ Database import/query failed: {e}")
    import traceback
    traceback.print_exc()

try:
    from tools.google_drive_tool import ListFilesTool
    print("✅ Google Drive tool imported successfully")
    
    list_tool = ListFilesTool()
    print("✅ ListFilesTool instance created successfully")
    
except Exception as e:
    print(f"❌ Google Drive tool import failed: {e}")
    import traceback
    traceback.print_exc()

# Test if there are any hidden imports
print("\n🔍 Checking for any 'patient_info_tool' references...")
import subprocess
result = subprocess.run(['grep', '-r', 'patient_info_tool', '.'], capture_output=True, text=True, shell=True)
if result.stdout:
    print(f"Found references:\n{result.stdout}")
else:
    print("No references to 'patient_info_tool' found in codebase")

print("\n🔍 Checking current working directory and Python path...")
print(f"Current directory: {os.getcwd()}")
print(f"Python path: {sys.path[:3]}...")  # First 3 entries

print("\n✅ Diagnostic complete!")