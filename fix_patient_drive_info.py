#!/usr/bin/env python3
"""
Fix existing patient REG2025214740 with missing Drive folder info
"""

import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), 'src'))

from database.db_manager import PatientDB

def fix_patient_drive_info():
    """Fix the existing patient with proper Drive folder info"""
    
    patient_id = "REG2025214740"
    drive_folder_id = "1I4lAAtrpD6MasIdULCySjr-9S8zzmJqW"
    drive_folder_url = "https://drive.google.com/drive/folders/1I4lAAtrpD6MasIdULCySjr-9S8zzmJqW"
    
    print(f"🔧 Fixing patient {patient_id} Drive folder info...")
    
    try:
        patient_db = PatientDB()
        
        # Check current patient info
        current_info = patient_db.get_patient_by_id(patient_id)
        print(f"📋 Current patient info: {current_info}")
        
        # Update with Drive folder info
        update_result = patient_db.update_patient(patient_id, {
            'drive_folder_id': drive_folder_id,
            'drive_folder_url': drive_folder_url
        })
        
        print(f"✅ Update result: {update_result}")
        
        # Verify the update
        updated_info = patient_db.get_patient_by_id(patient_id)
        print(f"📋 Updated patient info:")
        print(f"  - Drive Folder ID: {updated_info.get('drive_folder_id')}")
        print(f"  - Drive Folder URL: {updated_info.get('drive_folder_url')}")
        
        print(f"✅ Patient {patient_id} Drive folder info updated successfully!")
        
    except Exception as e:
        print(f"❌ ERROR: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    fix_patient_drive_info()