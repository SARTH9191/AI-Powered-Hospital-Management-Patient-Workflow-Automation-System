"""
Create Google Drive folder for manually reset patient
"""
import sys
import os
sys.path.insert(0, os.path.dirname(__file__))

from tools.google_drive_tool import CreatePatientFolderTool
from database.db_manager import PatientDB
import re

PATIENT_ID = "REG2025055769"
PATIENT_NAME = "Samarth Pawar"
PATIENT_EMAIL = "samarth.pawar243@vit.edu"

def create_drive_folder():
    """Create Drive folder and update patient record"""
    
    print(f"\n📁 Creating Google Drive folder for {PATIENT_NAME}...\n")
    
    # Create Drive folder
    try:
        drive_tool = CreatePatientFolderTool()
        folder_result = drive_tool._run(
            folder_name=f"Patient_{PATIENT_ID}_{PATIENT_NAME}"
        )
        
        print(f"Result:\n{folder_result}\n")
        
        # Extract URL and folder ID
        url_match = re.search(r'- Link: (https://[^\s\n]+)', folder_result)
        folder_id_match = re.search(r'- Folder ID: ([^\s\n]+)', folder_result)
        
        if not url_match:
            url_match = re.search(r'URL: (https://[^\s\n]+)', folder_result)
        if not folder_id_match:
            folder_id_match = re.search(r'Folder ID: ([^\s\n]+)', folder_result)
        
        if url_match and folder_id_match:
            drive_url = url_match.group(1)
            folder_id = folder_id_match.group(1)
            
            print(f"✅ Extracted Drive URL: {drive_url}")
            print(f"✅ Extracted Folder ID: {folder_id}")
            
            # Update PostgreSQL
            patient_db = PatientDB()
            patient_db.update_patient(PATIENT_ID, {
                'drive_folder_url': drive_url,
                'drive_folder_id': folder_id
            })
            
            print(f"\n✅ Updated patient record in PostgreSQL")
            print(f"\n🎉 Drive folder created successfully!")
            print(f"   Folder URL: {drive_url}")
            print(f"   Folder ID: {folder_id}")
        else:
            print(f"❌ Could not extract Drive folder info")
            print(f"   URL match: {url_match}")
            print(f"   Folder ID match: {folder_id_match}")
            
    except Exception as e:
        print(f"❌ Error creating Drive folder: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    create_drive_folder()
