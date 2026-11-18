"""Check workflow_states table schema"""
from database.db_manager import DatabaseManager
import json

db = DatabaseManager()
result = db.execute_query(
    "SELECT column_name, data_type FROM information_schema.columns WHERE table_name = 'workflow_states' ORDER BY ordinal_position",
    fetch='all'
)
print(json.dumps(result, indent=2))
