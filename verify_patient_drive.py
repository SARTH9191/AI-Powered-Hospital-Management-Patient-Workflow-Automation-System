from database.db_manager import PatientDB

db = PatientDB()
patient = db.get_patient_by_email('iamsamarth786@gmail.com')
print(f"✅ Patient: {patient['patient_id']}")
print(f"📁 Drive Folder ID: {patient.get('drive_folder_id')}")
print(f"🔗 Drive Folder URL: {patient.get('drive_folder_url')}")
