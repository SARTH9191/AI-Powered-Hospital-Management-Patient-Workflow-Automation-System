"""
Startup Cleanup Script
Ensures data consistency across PostgreSQL, JSON, and Redis
Runs automatically when backend starts
"""

import json
from pathlib import Path
from database.db_manager import DatabaseManager
from database.redis_cache import RedisCache

def sync_patient_data():
    """
    Synchronize patient data across all storage layers
    Priority: JSON > PostgreSQL > Redis
    JSON is source of truth for patient records
    """
    
    print("\n" + "="*70)
    print("🔄 STARTUP: Synchronizing patient data across storage layers...")
    print("="*70)
    
    db = DatabaseManager()
    cache = RedisCache()
    
    # Step 1: Load patients from JSON (source of truth)
    json_file = Path("data/patients_database.json")
    json_patients = {}
    
    if json_file.exists():
        with open(json_file, 'r', encoding='utf-8') as f:
            json_patients = json.load(f)
        print(f"📄 Found {len(json_patients)} patients in JSON")
    else:
        print("⚠️ No patients_database.json found")
        return
    
    # Step 2: Get all patients from PostgreSQL
    conn = db._connection_pool.getconn()
    cur = conn.cursor()
    cur.execute("SELECT patient_id, email FROM patients")
    pg_patients = {row[1]: row[0] for row in cur.fetchall()}  # email -> patient_id
    print(f"🗄️ Found {len(pg_patients)} patients in PostgreSQL")
    
    # Step 3: Sync from JSON to PostgreSQL
    added_count = 0
    updated_count = 0
    deleted_count = 0
    
    # Add/Update patients from JSON to PostgreSQL
    for patient_id, patient in json_patients.items():
        email = patient.get('email')
        if not email:
            continue
        
        # Check if patient exists in PostgreSQL
        if email in pg_patients:
            # Patient exists - check if ID matches
            if pg_patients[email] != patient_id:
                # ID mismatch - delete old record and add new one
                print(f"🔄 Updating patient: {email} (old ID: {pg_patients[email]}, new ID: {patient_id})")
                cur.execute("DELETE FROM patients WHERE email = %s", (email,))
                cur.execute("DELETE FROM workflow_states WHERE patient_id = %s", (pg_patients[email],))
                
                # Insert new record
                name_parts = patient.get('full_name', '').split()
                first_name = name_parts[0] if name_parts else ''
                last_name = ' '.join(name_parts[1:]) if len(name_parts) > 1 else ''
                
                cur.execute("""
                    INSERT INTO patients (
                        patient_id, first_name, last_name, email, phone,
                        date_of_birth, gender, address,
                        drive_folder_id, drive_folder_url, spreadsheet_id
                    ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
                """, (
                    patient_id, first_name, last_name, email, patient.get('phone'),
                    patient.get('date_of_birth'), patient.get('gender'), patient.get('address'),
                    patient.get('drive_folder_id'), patient.get('drive_folder_url'), patient.get('spreadsheet_id')
                ))
                updated_count += 1
        else:
            # Patient doesn't exist - add new record
            print(f"➕ Adding new patient: {email} ({patient_id})")
            name_parts = patient.get('full_name', '').split()
            first_name = name_parts[0] if name_parts else ''
            last_name = ' '.join(name_parts[1:]) if len(name_parts) > 1 else ''
            
            cur.execute("""
                INSERT INTO patients (
                    patient_id, first_name, last_name, email, phone,
                    date_of_birth, gender, address,
                    drive_folder_id, drive_folder_url, spreadsheet_id
                ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
            """, (
                patient_id, first_name, last_name, email, patient.get('phone'),
                patient.get('date_of_birth'), patient.get('gender'), patient.get('address'),
                patient.get('drive_folder_id'), patient.get('drive_folder_url'), patient.get('spreadsheet_id')
            ))
            added_count += 1
    
    # Delete patients from PostgreSQL that are not in JSON
    json_emails = {p.get('email') for p in json_patients.values() if p.get('email')}
    for pg_email, pg_id in pg_patients.items():
        if pg_email not in json_emails:
            print(f"🗑️ Removing orphaned patient from PostgreSQL: {pg_email} ({pg_id})")
            cur.execute("DELETE FROM patients WHERE patient_id = %s", (pg_id,))
            cur.execute("DELETE FROM workflow_states WHERE patient_id = %s", (pg_id,))
            deleted_count += 1
    
    conn.commit()
    cur.close()
    db._connection_pool.putconn(conn)
    
    # Step 4: Clear Redis cache to force fresh loads
    try:
        cache.redis_client.flushdb()
        print("🧹 Cleared Redis cache")
    except Exception as e:
        print(f"⚠️ Could not clear Redis: {e}")
    
    print("\n✅ SYNC COMPLETE:")
    print(f"   • Added: {added_count} patients")
    print(f"   • Updated: {updated_count} patients")
    print(f"   • Deleted: {deleted_count} patients")
    print(f"   • Total in sync: {len(json_patients)} patients")
    print("="*70 + "\n")


if __name__ == "__main__":
    sync_patient_data()
