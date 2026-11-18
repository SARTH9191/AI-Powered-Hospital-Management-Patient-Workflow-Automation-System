"""
Reset a patient's workflow stage to start fresh
"""

import os
import sys
from dotenv import load_dotenv
import psycopg2

load_dotenv()

def reset_patient_to_stage_1(patient_email: str):
    """Reset patient's workflow to Stage 1"""
    
    try:
        # Connect to database
        conn = psycopg2.connect(
            host=os.getenv("POSTGRES_HOST", "localhost"),
            port=os.getenv("POSTGRES_PORT", "5432"),
            database=os.getenv("POSTGRES_DB", "hospital_ai"),
            user=os.getenv("POSTGRES_USER", "postgres"),
            password=os.getenv("POSTGRES_PASSWORD", "postgres")
        )
        cursor = conn.cursor()
        
        # Find patient by email
        cursor.execute("SELECT patient_id FROM patients WHERE email = %s", (patient_email,))
        result = cursor.fetchone()
        
        if not result:
            print(f"❌ Patient not found with email: {patient_email}")
            return False
        
        patient_id = result[0]
        print(f"✅ Found patient: {patient_id}")
        
        # Delete workflow state to force fresh start
        cursor.execute("DELETE FROM workflow_states WHERE patient_id = %s", (patient_id,))
        deleted_count = cursor.rowcount
        
        conn.commit()
        
        if deleted_count > 0:
            print(f"✅ Deleted workflow state for {patient_email}")
            print(f"✅ Patient will start fresh at Stage 1 on next login")
        else:
            print(f"⚠️ No workflow state found (patient already at Stage 1)")
        
        cursor.close()
        conn.close()
        
        return True
        
    except Exception as e:
        print(f"❌ Error: {e}")
        return False

if __name__ == "__main__":
    # Reset iamsamarth786@gmail.com to Stage 1
    email = "iamsamarth786@gmail.com"
    
    if len(sys.argv) > 1:
        email = sys.argv[1]
    
    print(f"🔄 Resetting workflow for: {email}")
    reset_patient_to_stage_1(email)
