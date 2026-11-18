"""
Fix existing patient PAT20251113001842 with Drive folder info
"""
from database.db_manager import PatientDB

def fix_patient_drive_info():
    """Update existing patient with Drive folder info from logs"""
    patient_id = "PAT20251113001842"
    drive_folder_id = "1TNk1j1PE9pVnTv4069Jy-4fj4Rkhu5Tl"
    drive_url = f"https://drive.google.com/drive/folders/{drive_folder_id}"
    
    patient_db = PatientDB()
    
    print(f"🔧 Fixing patient {patient_id} Drive folder info...")
    
    success = patient_db.update_patient(patient_id, {
        'drive_folder_id': drive_folder_id,
        'drive_folder_url': drive_url
    })
    
    if success:
        print(f"✅ Successfully updated patient {patient_id}")
        print(f"📁 Drive Folder ID: {drive_folder_id}")
        print(f"🔗 Drive URL: {drive_url}")
        
        # Verify the update
        patient = patient_db.get_patient(patient_id)
        if patient:
            print(f"\n📊 Verified patient data:")
            print(f"   Drive Folder ID: {patient.get('drive_folder_id')}")
            print(f"   Drive Folder URL: {patient.get('drive_folder_url')}")
    else:
        print(f"❌ Failed to update patient {patient_id}")

if __name__ == "__main__":
    fix_patient_drive_info()
