"""
Database Tool for Hospital Management System
PostgreSQL CRUD operations + ChromaDB for vector search
"""

import os
import json
from typing import Optional, Type, List, Dict, Any
from datetime import datetime
from pydantic import BaseModel, Field
from langchain.tools import BaseTool

# For now, we'll use JSON as fallback until PostgreSQL is set up
# Will integrate PostgreSQL + ChromaDB in production

PATIENTS_DB_FILE = 'data/patients_database.json'
APPOINTMENTS_DB_FILE = 'data/appointments_database.json'
MEDICAL_RECORDS_DB_FILE = 'data/medical_records_database.json'
LAB_TESTS_DB_FILE = 'data/lab_tests_database.json'
PRESCRIPTIONS_DB_FILE = 'data/prescriptions_database.json'


# ==================== DATABASE HELPERS ====================

def load_db(file_path):
    """Load database from JSON file"""
    if not os.path.exists(file_path):
        os.makedirs(os.path.dirname(file_path), exist_ok=True)
        # Different databases use different structures
        # patients_database.json uses dict (patient_id as keys)
        # Other databases might use lists
        return {}
    
    try:
        with open(file_path, 'r') as f:
            data = json.load(f)
            return data if data else {}
    except:
        # Return empty list for list-based databases, dict for others
        if 'patients' in file_path or 'appointments' in file_path or 'medical_records' in file_path:
            return []
        return {}


def save_db(file_path, db):
    """Save database to JSON file"""
    os.makedirs(os.path.dirname(file_path), exist_ok=True)
    with open(file_path, 'w') as f:
        json.dump(db, f, indent=2)


# ==================== INPUT SCHEMAS ====================

class CreateRecordInput(BaseModel):
    """Input for creating database records."""
    table_name: str = Field(description="Table name: patients, appointments, medical_records, lab_tests, prescriptions")
    record_data: Dict[str, Any] = Field(description="Dictionary containing record data")


class ReadRecordInput(BaseModel):
    """Input for reading records."""
    table_name: str = Field(description="Table name to read from")
    record_id: str = Field(description="Record ID to retrieve")


class UpdateRecordInput(BaseModel):
    """Input for updating records."""
    table_name: str = Field(description="Table name to update")
    record_id: str = Field(description="Record ID to update")
    update_data: Dict[str, Any] = Field(description="Dictionary containing fields to update")


class DeleteRecordInput(BaseModel):
    """Input for deleting records."""
    table_name: str = Field(description="Table name to delete from")
    record_id: str = Field(description="Record ID to delete")


class SearchRecordsInput(BaseModel):
    """Input for searching records."""
    table_name: str = Field(description="Table name to search in")
    search_field: str = Field(description="Field name to search in")
    search_value: str = Field(description="Value to search for")


class QueryRecordsInput(BaseModel):
    """Input for querying records with filters."""
    table_name: str = Field(description="Table name to query")
    filters: Dict[str, Any] = Field(description="Dictionary of field:value pairs to filter by")


# ==================== DATABASE TOOLS ====================

class CreateRecordTool(BaseTool):
    """Tool for creating database records."""
    
    name: str = "create_database_record"
    description: str = """Create a new record in specified database table. 
    Supports: patients, appointments, medical_records, lab_tests, prescriptions.
    Provide table name and record data as dictionary."""
    args_schema: Type[BaseModel] = CreateRecordInput
    
    def _run(self, table_name: str, record_data: Dict[str, Any]) -> str:
        try:
            # Map table names to file paths
            table_files = {
                'patients': PATIENTS_DB_FILE,
                'appointments': APPOINTMENTS_DB_FILE,
                'medical_records': MEDICAL_RECORDS_DB_FILE,
                'lab_tests': LAB_TESTS_DB_FILE,
                'prescriptions': PRESCRIPTIONS_DB_FILE
            }
            
            if table_name not in table_files:
                return f"❌ Invalid table name. Valid tables: {', '.join(table_files.keys())}"
            
            # Load database
            db = load_db(table_files[table_name])
            
            # Get record ID based on table
            id_field_map = {
                'patients': 'patient_id',
                'appointments': 'appointment_id',
                'medical_records': 'record_id',
                'lab_tests': 'test_id',
                'prescriptions': 'prescription_id'
            }
            
            id_field = id_field_map[table_name]
            
            if id_field not in record_data:
                return f"❌ Record must include '{id_field}' field"
            
            record_id = record_data[id_field]
            
            # Check if record already exists
            if record_id in db:
                return f"❌ Record with {id_field} '{record_id}' already exists. Use update_database_record to modify."
            
            # Add timestamps
            record_data['created_at'] = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
            record_data['updated_at'] = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
            
            # Save record
            db[record_id] = record_data
            save_db(table_files[table_name], db)
            
            return f"""✅ Record Created Successfully!

📊 Table: {table_name}
🆔 Record ID: {record_id}
📅 Created: {record_data['created_at']}

📝 Record Data:
{json.dumps(record_data, indent=2)}

✅ Record has been saved to database.
"""
        
        except Exception as e:
            return f"❌ Error creating record: {str(e)}"
    
    async def _arun(self, table_name: str, record_data: Dict[str, Any]) -> str:
        return self._run(table_name, record_data)


class ReadRecordTool(BaseTool):
    """Tool for reading database records."""
    
    name: str = "read_database_record"
    description: str = """Read a specific record from database by ID. 
    Provide table name and record ID to retrieve complete record."""
    args_schema: Type[BaseModel] = ReadRecordInput
    
    def _run(self, table_name: str, record_id: str) -> str:
        try:
            table_files = {
                'patients': PATIENTS_DB_FILE,
                'appointments': APPOINTMENTS_DB_FILE,
                'medical_records': MEDICAL_RECORDS_DB_FILE,
                'lab_tests': LAB_TESTS_DB_FILE,
                'prescriptions': PRESCRIPTIONS_DB_FILE
            }
            
            if table_name not in table_files:
                return f"❌ Invalid table name. Valid tables: {', '.join(table_files.keys())}"
            
            db = load_db(table_files[table_name])
            
            if record_id not in db:
                return f"❌ Record not found with ID: {record_id} in table: {table_name}"
            
            record = db[record_id]
            
            return f"""✅ Record Retrieved Successfully!

📊 Table: {table_name}
🆔 Record ID: {record_id}

📝 Record Data:
{json.dumps(record, indent=2)}
"""
        
        except Exception as e:
            return f"❌ Error reading record: {str(e)}"
    
    async def _arun(self, table_name: str, record_id: str) -> str:
        return self._run(table_name, record_id)


class UpdateRecordTool(BaseTool):
    """Tool for updating database records."""
    
    name: str = "update_database_record"
    description: str = """Update existing database record. 
    Provide table name, record ID, and dictionary of fields to update."""
    args_schema: Type[BaseModel] = UpdateRecordInput
    
    def _run(self, table_name: str, record_id: str, update_data: Dict[str, Any]) -> str:
        try:
            table_files = {
                'patients': PATIENTS_DB_FILE,
                'appointments': APPOINTMENTS_DB_FILE,
                'medical_records': MEDICAL_RECORDS_DB_FILE,
                'lab_tests': LAB_TESTS_DB_FILE,
                'prescriptions': PRESCRIPTIONS_DB_FILE
            }
            
            if table_name not in table_files:
                return f"❌ Invalid table name. Valid tables: {', '.join(table_files.keys())}"
            
            db = load_db(table_files[table_name])
            
            if record_id not in db:
                return f"❌ Record not found with ID: {record_id} in table: {table_name}"
            
            # Store old values for comparison
            old_record = db[record_id].copy()
            
            # Update fields
            for field, value in update_data.items():
                db[record_id][field] = value
            
            # Update timestamp
            db[record_id]['updated_at'] = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
            
            # Save database
            save_db(table_files[table_name], db)
            
            # Show what changed
            changes = []
            for field in update_data.keys():
                old_val = old_record.get(field, 'Not set')
                new_val = update_data[field]
                changes.append(f"  • {field}: {old_val} → {new_val}")
            
            return f"""✅ Record Updated Successfully!

📊 Table: {table_name}
🆔 Record ID: {record_id}
📅 Updated: {db[record_id]['updated_at']}

🔄 Changes Made:
{chr(10).join(changes)}

✅ Database has been updated.
"""
        
        except Exception as e:
            return f"❌ Error updating record: {str(e)}"
    
    async def _arun(self, table_name: str, record_id: str, update_data: Dict[str, Any]) -> str:
        return self._run(table_name, record_id, update_data)


class DeleteRecordTool(BaseTool):
    """Tool for deleting database records."""
    
    name: str = "delete_database_record"
    description: str = """Delete a record from database. 
    Provide table name and record ID. Use with caution - deletion is permanent!"""
    args_schema: Type[BaseModel] = DeleteRecordInput
    
    def _run(self, table_name: str, record_id: str) -> str:
        try:
            table_files = {
                'patients': PATIENTS_DB_FILE,
                'appointments': APPOINTMENTS_DB_FILE,
                'medical_records': MEDICAL_RECORDS_DB_FILE,
                'lab_tests': LAB_TESTS_DB_FILE,
                'prescriptions': PRESCRIPTIONS_DB_FILE
            }
            
            if table_name not in table_files:
                return f"❌ Invalid table name. Valid tables: {', '.join(table_files.keys())}"
            
            db = load_db(table_files[table_name])
            
            if record_id not in db:
                return f"❌ Record not found with ID: {record_id} in table: {table_name}"
            
            # Store record info before deletion
            deleted_record = db[record_id]
            
            # Delete record
            del db[record_id]
            
            # Save database
            save_db(table_files[table_name], db)
            
            return f"""✅ Record Deleted Successfully!

📊 Table: {table_name}
🆔 Deleted Record ID: {record_id}

⚠️ Deleted Record:
{json.dumps(deleted_record, indent=2)}

✅ Record has been permanently removed from database.
"""
        
        except Exception as e:
            return f"❌ Error deleting record: {str(e)}"
    
    async def _arun(self, table_name: str, record_id: str) -> str:
        return self._run(table_name, record_id)


class SearchRecordsTool(BaseTool):
    """Tool for searching database records."""
    
    name: str = "search_database_records"
    description: str = """Search records by field value. 
    Provide table name, field name, and search value. Returns all matching records."""
    args_schema: Type[BaseModel] = SearchRecordsInput
    
    def _run(self, table_name: str, search_field: str, search_value: str) -> str:
        try:
            table_files = {
                'patients': PATIENTS_DB_FILE,
                'appointments': APPOINTMENTS_DB_FILE,
                'medical_records': MEDICAL_RECORDS_DB_FILE,
                'lab_tests': LAB_TESTS_DB_FILE,
                'prescriptions': PRESCRIPTIONS_DB_FILE
            }
            
            if table_name not in table_files:
                return f"❌ Invalid table name. Valid tables: {', '.join(table_files.keys())}"
            
            db = load_db(table_files[table_name])
            
            if not db:
                return f"📭 No records found in table: {table_name}"
            
            # Search for matching records
            matches = []
            search_lower = str(search_value).lower()
            
            for record_id, record in db.items():
                if search_field in record:
                    field_value = str(record[search_field]).lower()
                    if search_lower in field_value:
                        matches.append((record_id, record))
            
            if not matches:
                return f"❌ No records found with {search_field}='{search_value}' in table: {table_name}"
            
            result = f"""✅ Found {len(matches)} matching record(s)!

📊 Table: {table_name}
🔍 Search: {search_field} contains '{search_value}'

"""
            
            for i, (record_id, record) in enumerate(matches, 1):
                result += f"""{'='*70}
Record {i}: ID = {record_id}
{json.dumps(record, indent=2)}

"""
            
            return result
        
        except Exception as e:
            return f"❌ Error searching records: {str(e)}"
    
    async def _arun(self, table_name: str, search_field: str, search_value: str) -> str:
        return self._run(table_name, search_field, search_value)


class QueryRecordsTool(BaseTool):
    """Tool for querying records with multiple filters."""
    
    name: str = "query_database_records"
    description: str = """Query records with multiple filter conditions. 
    Provide table name and dictionary of field:value pairs. Returns records matching ALL filters."""
    args_schema: Type[BaseModel] = QueryRecordsInput
    
    def _run(self, table_name: str, filters: Dict[str, Any]) -> str:
        try:
            table_files = {
                'patients': PATIENTS_DB_FILE,
                'appointments': APPOINTMENTS_DB_FILE,
                'medical_records': MEDICAL_RECORDS_DB_FILE,
                'lab_tests': LAB_TESTS_DB_FILE,
                'prescriptions': PRESCRIPTIONS_DB_FILE
            }
            
            if table_name not in table_files:
                return f"❌ Invalid table name. Valid tables: {', '.join(table_files.keys())}"
            
            db = load_db(table_files[table_name])
            
            if not db:
                return f"📭 No records found in table: {table_name}"
            
            # Query with filters
            matches = []
            
            for record_id, record in db.items():
                match = True
                for field, value in filters.items():
                    if field not in record or str(record[field]).lower() != str(value).lower():
                        match = False
                        break
                
                if match:
                    matches.append((record_id, record))
            
            if not matches:
                return f"""❌ No records found matching filters in table: {table_name}

Filters applied:
{json.dumps(filters, indent=2)}
"""
            
            result = f"""✅ Found {len(matches)} matching record(s)!

📊 Table: {table_name}
🔍 Filters: {json.dumps(filters, indent=2)}

"""
            
            for i, (record_id, record) in enumerate(matches, 1):
                result += f"""{'='*70}
Record {i}: ID = {record_id}
{json.dumps(record, indent=2)}

"""
            
            return result
        
        except Exception as e:
            return f"❌ Error querying records: {str(e)}"
    
    async def _arun(self, table_name: str, filters: Dict[str, Any]) -> str:
        return self._run(table_name, filters)


class ListAllRecordsTool(BaseTool):
    """Tool for listing all records in a table."""
    
    name: str = "list_all_records"
    description: str = """List all records from a database table. 
    Provide table name to see all records."""
    args_schema: Type[BaseModel] = BaseModel
    
    def _run(self, table_name: str = "patients") -> str:
        try:
            table_files = {
                'patients': PATIENTS_DB_FILE,
                'appointments': APPOINTMENTS_DB_FILE,
                'medical_records': MEDICAL_RECORDS_DB_FILE,
                'lab_tests': LAB_TESTS_DB_FILE,
                'prescriptions': PRESCRIPTIONS_DB_FILE
            }
            
            if table_name not in table_files:
                return f"❌ Invalid table name. Valid tables: {', '.join(table_files.keys())}"
            
            db = load_db(table_files[table_name])
            
            if not db:
                return f"📭 No records found in table: {table_name}"
            
            result = f"""✅ Total Records in {table_name}: {len(db)}

{'='*70}
"""
            
            for i, (record_id, record) in enumerate(db.items(), 1):
                result += f"""
Record {i}: ID = {record_id}
{json.dumps(record, indent=2)}
{'='*70}
"""
            
            return result
        
        except Exception as e:
            return f"❌ Error listing records: {str(e)}"
    
    async def _arun(self, table_name: str = "patients") -> str:
        return self._run(table_name)


# ==================== HELPER FUNCTION ====================

def get_all_database_tools():
    """Get all database tools for the agent"""
    return [
        CreateRecordTool(),
        ReadRecordTool(),
        UpdateRecordTool(),
        DeleteRecordTool(),
        SearchRecordsTool(),
        QueryRecordsTool(),
        ListAllRecordsTool()
    ]


# ==================== USAGE EXAMPLE ====================

if __name__ == "__main__":
    print("\n" + "="*70)
    print("🗄️ DATABASE TOOLS - Hospital Management System")
    print("="*70)
    
    print("\n📋 Available Tools:")
    print("  1. create_database_record - Create new records")
    print("  2. read_database_record - Read specific record by ID")
    print("  3. update_database_record - Update existing record")
    print("  4. delete_database_record - Delete record")
    print("  5. search_database_records - Search by field value")
    print("  6. query_database_records - Query with multiple filters")
    print("  7. list_all_records - List all records in table")
    
    print("\n🗄️ Supported Tables:")
    print("  • patients - Patient information")
    print("  • appointments - Appointment scheduling")
    print("  • medical_records - Medical history")
    print("  • lab_tests - Laboratory tests")
    print("  • prescriptions - Medication prescriptions")
    
    print("\n💡 Current: Using JSON database")
    print("   Production: Will migrate to PostgreSQL + ChromaDB")
    
    print("\n" + "="*70)
