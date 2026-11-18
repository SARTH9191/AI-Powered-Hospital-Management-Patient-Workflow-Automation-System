from database.db_manager import DatabaseManager
import json
from pathlib import Path

db = DatabaseManager()

# Step 1: Delete old patient from PostgreSQL
old_patient_id = "PAT20251113001842"
email = "iamsamarth786@gmail.com"

try:
    conn = db._connection_pool.getconn()
    cur = conn.cursor()
    
    # Delete from patients table
    print(f"Deleting old patient {old_patient_id} from PostgreSQL...")
    cur.execute("DELETE FROM patients WHERE patient_id = %s", (old_patient_id,))
    
    # Delete from workflow_states table
    cur.execute("DELETE FROM workflow_states WHERE patient_id = %s", (old_patient_id,))
    
    # Delete from otp_verifications table
    cur.execute("DELETE FROM otp_verifications WHERE email = %s", (email,))
    
    conn.commit()
    print(f"✅ Deleted {old_patient_id} from PostgreSQL")
    
    cur.close()
    db._connection_pool.putconn(conn)
    
except Exception as e:
    print(f"❌ Error: {e}")
    import traceback
    traceback.print_exc()

# Step 2: Read new patient data from JSON
new_patient_id = "REG2025635227"
json_file = Path("data/patients_database.json")

if json_file.exists():
    with open(json_file, 'r', encoding='utf-8') as f:
        patients_data = json.load(f)
    
    if new_patient_id in patients_data:
        patient = patients_data[new_patient_id]
        print(f"\n✅ Found {new_patient_id} in JSON")
        print(f"   Name: {patient.get('full_name')}")
        print(f"   Email: {patient.get('email')}")
        
        # Step 3: Insert into PostgreSQL
        try:
            conn = db._connection_pool.getconn()
            cur = conn.cursor()
            
            # Split full name into first and last
            name_parts = patient['full_name'].split()
            first_name = name_parts[0] if name_parts else ''
            last_name = ' '.join(name_parts[1:]) if len(name_parts) > 1 else ''
            
            insert_query = """
            INSERT INTO patients (
                patient_id, first_name, last_name, email, phone,
                date_of_birth, gender, address,
                drive_folder_id, drive_folder_url, spreadsheet_id
            ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
            """
            
            cur.execute(insert_query, (
                patient['patient_id'],
                first_name,
                last_name,
                patient['email'],
                patient['phone'],
                patient.get('date_of_birth'),
                patient.get('gender'),
                patient.get('address'),
                patient.get('drive_folder_id'),
                patient.get('drive_folder_url'),
                patient.get('spreadsheet_id')
            ))
            
            conn.commit()
            cur.close()
            db._connection_pool.putconn(conn)
            
            print(f"✅ Added {new_patient_id} to PostgreSQL")
        except Exception as e:
            print(f"❌ Failed to add to PostgreSQL: {e}")
            import traceback
            traceback.print_exc()
    else:
        print(f"❌ {new_patient_id} not found in JSON")
else:
    print("❌ patients_database.json not found")

print("\n" + "="*70)
print("✅ CLEANUP COMPLETE - iamsamarth786@gmail.com now maps to REG2025635227")
print("="*70)
