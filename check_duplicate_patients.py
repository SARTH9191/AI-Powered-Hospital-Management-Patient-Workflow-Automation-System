from database.db_manager import DatabaseManager

db = DatabaseManager()

# Query all patients with the specific email
email = "iamsamarth786@gmail.com"
query = "SELECT patient_id, email, full_name, created_at FROM patients WHERE email = %s ORDER BY created_at DESC"

try:
    conn = db._connection_pool.getconn()
    cur = conn.cursor()
    cur.execute(query, (email,))
    matches = cur.fetchall()
    
    print(f"\nFound {len(matches)} patient records with email: {email}\n")
    print("Patient IDs (newest first):")
    for row in matches:
        patient_id, email_val, name, created_at = row
        print(f"  - {patient_id} | {name} | Created: {created_at}")
    
    cur.close()
    db._connection_pool.putconn(conn)
    
    print("\n" + "="*70)
    print("SOLUTION: Delete PAT20251113001842, keep only REG2025635227")
    print("="*70)
    
except Exception as e:
    print(f"Error: {e}")
    import traceback
    traceback.print_exc()


