"""
Database Configuration and Connection Manager
Handles PostgreSQL connections with connection pooling
"""

import os
from typing import Optional, Dict, Any, List
from contextlib import contextmanager
from datetime import datetime, date
import psycopg2
from psycopg2 import pool
from psycopg2.extras import RealDictCursor, Json
from dotenv import load_dotenv
import json

load_dotenv()

def convert_datetimes_to_iso(obj):
    """Recursively convert datetime objects to ISO format strings"""
    if isinstance(obj, (datetime, date)):
        return obj.isoformat()
    elif isinstance(obj, dict):
        return {key: convert_datetimes_to_iso(value) for key, value in obj.items()}
    elif isinstance(obj, list):
        return [convert_datetimes_to_iso(item) for item in obj]
    else:
        return obj

class DatabaseManager:
    """Singleton database connection manager with connection pooling"""
    
    _instance = None
    _connection_pool = None
    
    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(DatabaseManager, cls).__new__(cls)
        return cls._instance
    
    def __init__(self):
        if self._connection_pool is None:
            self._initialize_pool()
    
    def _initialize_pool(self):
        """Initialize connection pool"""
        try:
            self._connection_pool = psycopg2.pool.SimpleConnectionPool(
                minconn=1,
                maxconn=10,
                host=os.getenv("POSTGRES_HOST", "localhost"),
                port=os.getenv("POSTGRES_PORT", "5432"),
                database=os.getenv("POSTGRES_DB", "hospital_ai"),
                user=os.getenv("POSTGRES_USER", "postgres"),
                password=os.getenv("POSTGRES_PASSWORD", "postgres")
            )
            print("✅ Database connection pool initialized")
        except Exception as e:
            print(f"❌ Failed to initialize database pool: {e}")
            raise
    
    @contextmanager
    def get_connection(self):
        """Get connection from pool with automatic cleanup"""
        conn = self._connection_pool.getconn()
        try:
            yield conn
            conn.commit()
        except Exception as e:
            conn.rollback()
            raise e
        finally:
            self._connection_pool.putconn(conn)
    
    @contextmanager
    def get_cursor(self, dict_cursor=True):
        """Get cursor with automatic cleanup"""
        with self.get_connection() as conn:
            cursor_factory = RealDictCursor if dict_cursor else None
            cursor = conn.cursor(cursor_factory=cursor_factory)
            try:
                yield cursor
            finally:
                cursor.close()
    
    def execute_query(self, query: str, params: tuple = None, fetch: str = "all") -> Optional[List[Dict]]:
        """
        Execute SQL query and return results
        
        Args:
            query: SQL query string
            params: Query parameters
            fetch: "all", "one", or "none"
        """
        with self.get_cursor() as cursor:
            cursor.execute(query, params or ())
            
            if fetch == "all":
                return cursor.fetchall()
            elif fetch == "one":
                return cursor.fetchone()
            else:
                return None
    
    def execute_many(self, query: str, params_list: List[tuple]) -> int:
        """Execute query with multiple parameter sets"""
        with self.get_cursor() as cursor:
            cursor.executemany(query, params_list)
            return cursor.rowcount
    
    def close_all_connections(self):
        """Close all connections in pool"""
        if self._connection_pool:
            self._connection_pool.closeall()
            print("✅ All database connections closed")


# ============================================================================
# PATIENT DATABASE OPERATIONS
# ============================================================================

class PatientDB:
    """Database operations for patients table"""
    
    def __init__(self):
        self.db = DatabaseManager()
    
    def create_patient(self, patient_data: Dict[str, Any]) -> Optional[str]:
        """
        Create new patient record with duplicate handling
        
        Returns:
            patient_id if successful, None otherwise
        """
        
        # First, check if patient already exists by email or phone
        email = patient_data.get('email')
        phone = patient_data.get('phone')
        
        if email:
            existing_by_email = self.get_patient_by_email(email)
            if existing_by_email:
                print(f"ℹ️ Patient with email {email} already exists: {existing_by_email['patient_id']}")
                # Return existing patient ID instead of deleting
                return existing_by_email['patient_id']
        
        if phone:
            existing_by_phone = self.get_patient_by_phone(phone)
            if existing_by_phone:
                print(f"ℹ️ Patient with phone {phone} already exists: {existing_by_phone['patient_id']}")
                # Return existing patient ID instead of deleting
                return existing_by_phone['patient_id']
        
        query = """
        INSERT INTO patients (
            patient_id, first_name, last_name, email, phone,
            date_of_birth, gender, address, city, state, pincode,
            drive_folder_id, drive_folder_url, spreadsheet_id,
            emergency_contact_name, emergency_contact_phone, emergency_contact_relation
        ) VALUES (
            %(patient_id)s, %(first_name)s, %(last_name)s, %(email)s, %(phone)s,
            %(date_of_birth)s, %(gender)s, %(address)s, %(city)s, %(state)s, %(pincode)s,
            %(drive_folder_id)s, %(drive_folder_url)s, %(spreadsheet_id)s,
            %(emergency_contact_name)s, %(emergency_contact_phone)s, %(emergency_contact_relation)s
        )
        RETURNING patient_id
        """
        
        try:
            result = self.db.execute_query(query, patient_data, fetch="one")
            return result['patient_id'] if result else None
        except Exception as e:
            print(f"Error creating patient: {e}")
            return None
    
    def get_patient_by_id(self, patient_id: str) -> Optional[Dict]:
        """Get patient by patient_id"""
        query = "SELECT * FROM patients WHERE patient_id = %s"
        return self.db.execute_query(query, (patient_id,), fetch="one")
    
    def get_patient_by_email(self, email: str) -> Optional[Dict]:
        """Get patient by email"""
        query = "SELECT * FROM patients WHERE email = %s"
        return self.db.execute_query(query, (email,), fetch="one")
    
    def get_patient_by_phone(self, phone: str) -> Optional[Dict]:
        """Get patient by phone"""
        query = "SELECT * FROM patients WHERE phone = %s"
        return self.db.execute_query(query, (phone,), fetch="one")
    
    def search_patients(self, search_term: str) -> List[Dict]:
        """Search patients by name, email, or phone"""
        query = """
        SELECT * FROM patients 
        WHERE full_name ILIKE %s 
           OR email ILIKE %s 
           OR phone ILIKE %s
        ORDER BY registration_date DESC
        LIMIT 10
        """
        search_pattern = f"%{search_term}%"
        return self.db.execute_query(query, (search_pattern, search_pattern, search_pattern))
    
    def update_patient(self, patient_id: str, updates: Dict[str, Any]) -> bool:
        """Update patient record"""
        if not updates:
            return True
            
        # Build dynamic UPDATE query with named parameters
        set_clause = ", ".join([f"{k} = %({k})s" for k in updates.keys()])
        query = f"UPDATE patients SET {set_clause} WHERE patient_id = %(patient_id)s"
        
        # Merge updates with patient_id
        params = {**updates, 'patient_id': patient_id}
        
        try:
            self.db.execute_query(query, params, fetch="none")
            print(f"✅ Updated patient {patient_id}: {list(updates.keys())}")
            return True
        except Exception as e:
            print(f"❌ Error updating patient {patient_id}: {e}")
            return False
    
    def delete_patient(self, patient_id: str) -> bool:
        """
        Delete patient record and related data
        
        Returns:
            True if successful, False otherwise
        """
        try:
            # Delete workflow states first (foreign key dependency)
            workflow_query = "DELETE FROM workflow_states WHERE patient_id = %s"
            self.db.execute_query(workflow_query, (patient_id,), fetch="none")
            
            # Delete patient record
            patient_query = "DELETE FROM patients WHERE patient_id = %s"
            self.db.execute_query(patient_query, (patient_id,), fetch="none")
            
            print(f"✅ Successfully deleted patient: {patient_id}")
            return True
        except Exception as e:
            print(f"❌ Error deleting patient {patient_id}: {e}")
            return False


# ============================================================================
# WORKFLOW STATE DATABASE OPERATIONS
# ============================================================================

class WorkflowStateDB:
    """Database operations for workflow_states table"""
    
    def __init__(self):
        self.db = DatabaseManager()
    
    def save_state(self, patient_id: str, state_data: Dict[str, Any]) -> bool:
        """Save or update workflow state"""
        query = """
        INSERT INTO workflow_states (
            patient_id, current_stage, stage_name, stage_data,
            conversation_history, awaiting_confirmation, pending_actions,
            session_id, is_active
        ) VALUES (
            %(patient_id)s, %(current_stage)s, %(stage_name)s, %(stage_data)s,
            %(conversation_history)s, %(awaiting_confirmation)s, %(pending_actions)s,
            %(session_id)s, %(is_active)s
        )
        ON CONFLICT (patient_id) 
        DO UPDATE SET
            current_stage = EXCLUDED.current_stage,
            stage_name = EXCLUDED.stage_name,
            stage_data = EXCLUDED.stage_data,
            conversation_history = EXCLUDED.conversation_history,
            awaiting_confirmation = EXCLUDED.awaiting_confirmation,
            pending_actions = EXCLUDED.pending_actions,
            session_id = EXCLUDED.session_id,
            is_active = EXCLUDED.is_active,
            last_interaction_at = CURRENT_TIMESTAMP
        """
        
        # Prepare data - convert datetime objects to ISO strings before JSON serialization
        stage_data_clean = convert_datetimes_to_iso(state_data.get('stage_data', {}))
        conversation_history_clean = convert_datetimes_to_iso(state_data.get('conversation_history', []))
        pending_actions_clean = convert_datetimes_to_iso(state_data.get('pending_actions', []))
        
        data = {
            'patient_id': patient_id,
            'current_stage': state_data.get('current_stage', 1),
            'stage_name': state_data.get('stage_name', 'registration'),
            'stage_data': Json(stage_data_clean),
            'conversation_history': Json(conversation_history_clean),
            'awaiting_confirmation': state_data.get('awaiting_confirmation', False),
            'pending_actions': Json(pending_actions_clean),
            'session_id': state_data.get('session_id', ''),
            'is_active': state_data.get('is_active', True)
        }
        
        try:
            self.db.execute_query(query, data, fetch="none")
            return True
        except Exception as e:
            error_msg = str(e)
            if "foreign key constraint" in error_msg.lower():
                # This is expected during registration - patient record created first, then workflow state
                pass  # Silent - not an error
            else:
                print(f"Error saving workflow state: {e}")
            return False
    
    def load_state(self, patient_id: str) -> Optional[Dict]:
        """Load workflow state for patient"""
        query = """
        SELECT * FROM workflow_states 
        WHERE patient_id = %s AND is_active = TRUE
        ORDER BY last_interaction_at DESC
        LIMIT 1
        """
        return self.db.execute_query(query, (patient_id,), fetch="one")
    
    def get_active_workflows(self) -> List[Dict]:
        """Get all active workflow sessions"""
        query = """
        SELECT * FROM active_patient_workflows
        ORDER BY last_interaction_at DESC
        """
        return self.db.execute_query(query)


# ============================================================================
# OTP DATABASE OPERATIONS
# ============================================================================

class OTPDB:
    """Database operations for OTP verifications"""
    
    def __init__(self):
        self.db = DatabaseManager()
    
    def create_otp(self, phone: str, otp_code: str, otp_type: str = "sms", 
                   purpose: str = "registration", email: str = None, 
                   patient_id: str = None) -> bool:
        """Create new OTP record"""
        query = """
        INSERT INTO otp_verifications (
            patient_id, phone, email, otp_code, otp_type, purpose, expires_at
        ) VALUES (
            %s, %s, %s, %s, %s, %s, CURRENT_TIMESTAMP + INTERVAL '5 minutes'
        )
        """
        
        try:
            self.db.execute_query(
                query, 
                (patient_id, phone, email, otp_code, otp_type, purpose),
                fetch="none"
            )
            return True
        except Exception as e:
            print(f"Error creating OTP: {e}")
            return False
    
    def verify_otp(self, phone: str, otp_code: str) -> bool:
        """Verify OTP code"""
        # Check if OTP exists and is valid
        query = """
        SELECT * FROM otp_verifications
        WHERE phone = %s 
          AND otp_code = %s
          AND is_verified = FALSE
          AND expires_at > CURRENT_TIMESTAMP
          AND attempts < max_attempts
        ORDER BY created_at DESC
        LIMIT 1
        """
        
        result = self.db.execute_query(query, (phone, otp_code), fetch="one")
        
        if result:
            # Mark as verified
            update_query = """
            UPDATE otp_verifications
            SET is_verified = TRUE, verified_at = CURRENT_TIMESTAMP
            WHERE id = %s
            """
            self.db.execute_query(update_query, (result['id'],), fetch="none")
            return True
        else:
            # Increment attempts
            update_query = """
            UPDATE otp_verifications
            SET attempts = attempts + 1
            WHERE phone = %s AND is_verified = FALSE
            """
            self.db.execute_query(update_query, (phone,), fetch="none")
            return False
    
    def check_existing_otp(self, phone: str) -> Optional[Dict]:
        """Check if there's a valid OTP for this phone"""
        query = """
        SELECT * FROM otp_verifications
        WHERE phone = %s
          AND is_verified = FALSE
          AND expires_at > CURRENT_TIMESTAMP
        ORDER BY created_at DESC
        LIMIT 1
        """
        return self.db.execute_query(query, (phone,), fetch="one")
    
    def is_email_verified(self, email: str) -> bool:
        """Check if email is already verified (returning user)"""
        query = """
        SELECT * FROM otp_verifications
        WHERE email = %s
          AND is_verified = TRUE
        ORDER BY verified_at DESC
        LIMIT 1
        """
        result = self.db.execute_query(query, (email,), fetch="one")
        return result is not None
    
    def get_patient_by_verified_email(self, email: str) -> Optional[Dict]:
        """Get patient details for a verified email (returning user)"""
        # First check if email is verified
        if not self.is_email_verified(email):
            return None
        
        # Get the most recent patient record with this email
        query = """
        SELECT p.* FROM patients p
        WHERE p.email = %s
        ORDER BY p.created_at DESC
        LIMIT 1
        """
        return self.db.execute_query(query, (email,), fetch="one")


# ============================================================================
# HELPER FUNCTIONS
# ============================================================================

def init_database():
    """Initialize database with schema"""
    import subprocess
    
    print("Initializing database...")
    
    # Read schema file
    schema_file = "database/schema.sql"
    if not os.path.exists(schema_file):
        print(f"❌ Schema file not found: {schema_file}")
        return False
    
    try:
        # Execute schema
        db = DatabaseManager()
        with open(schema_file, 'r') as f:
            schema_sql = f.read()
        
        with db.get_cursor(dict_cursor=False) as cursor:
            cursor.execute(schema_sql)
        
        print("✅ Database initialized successfully!")
        return True
    except Exception as e:
        print(f"❌ Database initialization failed: {e}")
        return False


# ============================================================================
# EXPORTS
# ============================================================================

__all__ = [
    'DatabaseManager',
    'PatientDB',
    'WorkflowStateDB',
    'OTPDB',
    'init_database'
]
