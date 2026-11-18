"""
Database Migration: Add visit tracking columns
Adds support for multiple patient visits and workflow loops
"""

import os
import sys
from dotenv import load_dotenv
import psycopg2

load_dotenv()

def add_visit_tracking_columns():
    """Add visit_number, last_visit_date, visit_complete columns to workflow_states"""
    
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
        
        print("🔄 Adding visit tracking columns to workflow_states table...")
        
        # Add columns if they don't exist
        cursor.execute("""
            ALTER TABLE workflow_states
            ADD COLUMN IF NOT EXISTS visit_number INTEGER DEFAULT 1,
            ADD COLUMN IF NOT EXISTS last_visit_date TIMESTAMP,
            ADD COLUMN IF NOT EXISTS visit_complete BOOLEAN DEFAULT FALSE;
        """)
        
        conn.commit()
        
        print("✅ Successfully added columns:")
        print("   - visit_number (INTEGER, default: 1)")
        print("   - last_visit_date (TIMESTAMP)")
        print("   - visit_complete (BOOLEAN, default: false)")
        
        # Verify columns were added
        cursor.execute("""
            SELECT column_name, data_type, column_default
            FROM information_schema.columns
            WHERE table_name = 'workflow_states'
            AND column_name IN ('visit_number', 'last_visit_date', 'visit_complete')
            ORDER BY column_name;
        """)
        
        columns = cursor.fetchall()
        print(f"\n✅ Verified {len(columns)} columns exist in database")
        
        cursor.close()
        conn.close()
        
        return True
        
    except Exception as e:
        print(f"❌ Error: {e}")
        return False

if __name__ == "__main__":
    print("=" * 60)
    print("DATABASE MIGRATION: Visit Tracking for Workflow Loop")
    print("=" * 60)
    
    success = add_visit_tracking_columns()
    
    if success:
        print("\n🎉 Migration complete! Stage 12→2 workflow loop ready!")
    else:
        print("\n❌ Migration failed. Please check error messages above.")
        sys.exit(1)
