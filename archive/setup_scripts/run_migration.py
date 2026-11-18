"""
Database Migration Script - Add Missing Columns
Fixes schema issues discovered during Q&A integration testing
"""

import psycopg2
from psycopg2.extensions import ISOLATION_LEVEL_AUTOCOMMIT
import os
from dotenv import load_dotenv

load_dotenv()

def run_migration():
    """Execute database migration to add missing columns"""
    
    print("=" * 80)
    print("  DATABASE MIGRATION: Add Missing Columns")
    print("=" * 80)
    print()
    
    # Database credentials
    DB_CONFIG = {
        'host': os.getenv('POSTGRES_HOST', 'localhost'),
        'user': os.getenv('POSTGRES_USER', 'postgres'),
        'password': os.getenv('POSTGRES_PASSWORD', 'Samp@786'),
        'database': os.getenv('POSTGRES_DB', 'hospital_ai'),
        'port': os.getenv('POSTGRES_PORT', '5432')
    }
    
    try:
        # Connect to database
        print(f"🔌 Connecting to database: {DB_CONFIG['database']}...")
        conn = psycopg2.connect(**DB_CONFIG)
        conn.set_isolation_level(ISOLATION_LEVEL_AUTOCOMMIT)
        cur = conn.cursor()
        print("✅ Connected successfully!")
        print()
        
        # ========================================================================
        # Step 1: Add missing columns to appointments table
        # ========================================================================
        print("📝 Step 1: Adding missing columns to 'appointments' table...")
        
        try:
            cur.execute("""
                ALTER TABLE appointments 
                ADD COLUMN IF NOT EXISTS notes TEXT;
            """)
            print("   ✅ Added column: notes (TEXT)")
        except Exception as e:
            print(f"   ⚠️ Column 'notes' may already exist: {e}")
        
        # ========================================================================
        # Step 2: Add missing columns to lab_tests table
        # ========================================================================
        print()
        print("🧪 Step 2: Adding missing columns to 'lab_tests' table...")
        
        try:
            cur.execute("""
                ALTER TABLE lab_tests
                ADD COLUMN IF NOT EXISTS test_date DATE;
            """)
            print("   ✅ Added column: test_date (DATE)")
        except Exception as e:
            print(f"   ⚠️ Column 'test_date' may already exist: {e}")
        
        try:
            cur.execute("""
                ALTER TABLE lab_tests
                ADD COLUMN IF NOT EXISTS unit VARCHAR(50);
            """)
            print("   ✅ Added column: unit (VARCHAR(50))")
        except Exception as e:
            print(f"   ⚠️ Column 'unit' may already exist: {e}")
        
        try:
            cur.execute("""
                ALTER TABLE lab_tests
                ADD COLUMN IF NOT EXISTS normal_range VARCHAR(100);
            """)
            print("   ✅ Added column: normal_range (VARCHAR(100))")
        except Exception as e:
            print(f"   ⚠️ Column 'normal_range' may already exist: {e}")
        
        # ========================================================================
        # Step 3: Copy data from result_date to test_date
        # ========================================================================
        print()
        print("📊 Step 3: Migrating data from result_date to test_date...")
        
        cur.execute("""
            UPDATE lab_tests 
            SET test_date = result_date 
            WHERE test_date IS NULL AND result_date IS NOT NULL;
        """)
        rows_updated = cur.rowcount
        print(f"   ✅ Updated {rows_updated} records")
        
        # ========================================================================
        # Step 4: Create indexes
        # ========================================================================
        print()
        print("🔍 Step 4: Creating indexes for faster queries...")
        
        try:
            cur.execute("""
                CREATE INDEX IF NOT EXISTS idx_lab_test_date ON lab_tests(test_date);
            """)
            print("   ✅ Created index: idx_lab_test_date")
        except Exception as e:
            print(f"   ⚠️ Index may already exist: {e}")
        
        try:
            cur.execute("""
                CREATE INDEX IF NOT EXISTS idx_lab_ordered_date ON lab_tests(ordered_date);
            """)
            print("   ✅ Created index: idx_lab_ordered_date")
        except Exception as e:
            print(f"   ⚠️ Index may already exist: {e}")
        
        # ========================================================================
        # Step 5: Set default values for existing records
        # ========================================================================
        print()
        print("🔧 Step 5: Setting default values for existing records...")
        
        cur.execute("""
            UPDATE appointments 
            SET notes = 'No notes provided' 
            WHERE notes IS NULL;
        """)
        appointments_updated = cur.rowcount
        print(f"   ✅ Updated {appointments_updated} appointment records")
        
        cur.execute("""
            UPDATE lab_tests 
            SET unit = 'N/A' 
            WHERE unit IS NULL AND result_value IS NOT NULL;
        """)
        unit_updated = cur.rowcount
        print(f"   ✅ Updated {unit_updated} lab test records (unit)")
        
        cur.execute("""
            UPDATE lab_tests 
            SET normal_range = reference_range 
            WHERE normal_range IS NULL AND reference_range IS NOT NULL;
        """)
        range_updated = cur.rowcount
        print(f"   ✅ Updated {range_updated} lab test records (normal_range)")
        
        # ========================================================================
        # Step 6: Verify changes
        # ========================================================================
        print()
        print("✅ Step 6: Verifying table structures...")
        print()
        
        # Check appointments table
        print("📋 APPOINTMENTS TABLE STRUCTURE:")
        cur.execute("""
            SELECT 
                column_name, 
                data_type, 
                is_nullable,
                column_default
            FROM information_schema.columns
            WHERE table_name = 'appointments'
            ORDER BY ordinal_position;
        """)
        
        appointments_columns = cur.fetchall()
        for col in appointments_columns:
            nullable = "NULL" if col[2] == 'YES' else "NOT NULL"
            default = f" DEFAULT {col[3]}" if col[3] else ""
            print(f"   • {col[0]:<30} {col[1]:<20} {nullable}{default}")
        
        print()
        print("🧪 LAB_TESTS TABLE STRUCTURE:")
        cur.execute("""
            SELECT 
                column_name, 
                data_type, 
                is_nullable,
                column_default
            FROM information_schema.columns
            WHERE table_name = 'lab_tests'
            ORDER BY ordinal_position;
        """)
        
        lab_columns = cur.fetchall()
        for col in lab_columns:
            nullable = "NULL" if col[2] == 'YES' else "NOT NULL"
            default = f" DEFAULT {col[3]}" if col[3] else ""
            print(f"   • {col[0]:<30} {col[1]:<20} {nullable}{default}")
        
        # Close connection
        cur.close()
        conn.close()
        
        print()
        print("=" * 80)
        print("  ✅ MIGRATION COMPLETED SUCCESSFULLY!")
        print("=" * 80)
        print()
        print("📊 Summary:")
        print(f"   • Added 'notes' column to appointments table")
        print(f"   • Added 'test_date', 'unit', 'normal_range' columns to lab_tests table")
        print(f"   • Created indexes for faster queries")
        print(f"   • Updated {appointments_updated + unit_updated + range_updated} existing records")
        print()
        print("✨ Q&A tools (GetMyAppointmentsTool, GetMyLabResultsTool) should now work!")
        print()
        
    except Exception as e:
        print(f"❌ Migration failed: {e}")
        print()
        import traceback
        traceback.print_exc()
        return False
    
    return True

if __name__ == "__main__":
    success = run_migration()
    
    if success:
        print("✅ Ready to test Q&A integration!")
        print()
        print("Run: python test_qa_integration.py")
    else:
        print("❌ Migration failed. Please check errors above.")
