"""Check patients table schema"""
from database.db_manager import DatabaseManager
import json

db = DatabaseManager()

# Get table schema
query = """
SELECT column_name, data_type, is_nullable 
FROM information_schema.columns 
WHERE table_name = 'patients' 
ORDER BY ordinal_position
"""

result = db.execute_query(query, fetch='all')
print("\n📋 Patients Table Schema:")
print(json.dumps(result, indent=2))

# Check if any patients exist
count_query = "SELECT COUNT(*) as count FROM patients"
count_result = db.execute_query(count_query, fetch='one')
print(f"\n📊 Total patients in database: {count_result['count']}")

# Check for our specific email
email_query = "SELECT * FROM patients WHERE email = %s"
email_result = db.execute_query(email_query, ('samarth.pawar243@vit.edu',), fetch='all')
print(f"\n🔍 Patients with email 'samarth.pawar243@vit.edu': {len(email_result)}")
if email_result:
    print(json.dumps(email_result, indent=2, default=str))
