"""
Export PostgreSQL Database Schema for IEEE Paper
Generates detailed schema information for screenshot
"""

from database.db_manager import DatabaseManager
import json

def export_schema():
    db = DatabaseManager()
    conn = db._connection_pool.getconn()
    cur = conn.cursor()
    
    print("\n" + "="*80)
    print("POSTGRESQL DATABASE SCHEMA - HOSPITAL MANAGEMENT SYSTEM")
    print("="*80)
    
    # Get list of tables
    cur.execute("""
        SELECT table_name 
        FROM information_schema.tables 
        WHERE table_schema = 'public' 
        AND table_type = 'BASE TABLE'
        ORDER BY table_name
    """)
    tables = [row[0] for row in cur.fetchall()]
    
    print(f"\n📊 TOTAL TABLES: {len(tables)}")
    print(f"Tables: {', '.join(tables)}\n")
    
    # For each table, get detailed schema
    for table_name in ['patients', 'workflow_states', 'otp_verifications']:
        print("\n" + "-"*80)
        print(f"TABLE: {table_name}")
        print("-"*80)
        
        # Get columns with details
        cur.execute(f"""
            SELECT 
                column_name, 
                data_type, 
                character_maximum_length,
                is_nullable,
                column_default
            FROM information_schema.columns
            WHERE table_name = '{table_name}'
            ORDER BY ordinal_position
        """)
        
        columns = cur.fetchall()
        
        print(f"\n{'COLUMN NAME':<30} {'DATA TYPE':<20} {'NULLABLE':<10} {'DEFAULT'}")
        print("-"*80)
        for col in columns:
            col_name, data_type, max_len, nullable, default = col
            type_str = f"{data_type}({max_len})" if max_len else data_type
            default_str = str(default)[:20] if default else ''
            print(f"{col_name:<30} {type_str:<20} {nullable:<10} {default_str}")
        
        # Get primary key
        cur.execute(f"""
            SELECT kcu.column_name
            FROM information_schema.table_constraints tc
            JOIN information_schema.key_column_usage kcu
                ON tc.constraint_name = kcu.constraint_name
            WHERE tc.table_name = '{table_name}' AND tc.constraint_type = 'PRIMARY KEY'
        """)
        pk = cur.fetchone()
        if pk:
            print(f"\n🔑 PRIMARY KEY: {pk[0]}")
        
        # Get foreign keys
        cur.execute(f"""
            SELECT
                kcu.column_name,
                ccu.table_name AS foreign_table_name,
                ccu.column_name AS foreign_column_name
            FROM information_schema.table_constraints AS tc
            JOIN information_schema.key_column_usage AS kcu
                ON tc.constraint_name = kcu.constraint_name
            JOIN information_schema.constraint_column_usage AS ccu
                ON ccu.constraint_name = tc.constraint_name
            WHERE tc.table_name = '{table_name}' AND tc.constraint_type = 'FOREIGN KEY'
        """)
        fks = cur.fetchall()
        if fks:
            print(f"\n🔗 FOREIGN KEYS:")
            for fk in fks:
                print(f"   • {fk[0]} → {fk[1]}.{fk[2]}")
        
        # Get sample data count
        cur.execute(f"SELECT COUNT(*) FROM {table_name}")
        count = cur.fetchone()[0]
        print(f"\n📊 TOTAL ROWS: {count}")
        
        # Show sample data
        if count > 0:
            cur.execute(f"SELECT * FROM {table_name} LIMIT 3")
            sample_rows = cur.fetchall()
            
            # Get column names
            cur.execute(f"""
                SELECT column_name 
                FROM information_schema.columns
                WHERE table_name = '{table_name}'
                ORDER BY ordinal_position
            """)
            col_names = [row[0] for row in cur.fetchall()]
            
            print(f"\n📄 SAMPLE DATA (first 3 rows):")
            for row in sample_rows:
                print(f"\n   Row:")
                for col_name, value in zip(col_names, row):
                    val_str = str(value)[:50] if value else 'NULL'
                    print(f"      {col_name}: {val_str}")
    
    cur.close()
    db._connection_pool.putconn(conn)
    
    print("\n" + "="*80)
    print("✅ SCHEMA EXPORT COMPLETE")
    print("="*80 + "\n")

if __name__ == "__main__":
    export_schema()
