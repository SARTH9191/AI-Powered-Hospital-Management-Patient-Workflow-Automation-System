# Database Setup Guide - Hospital Management System

## 🗄️ Database Architecture

The system uses a **hybrid database approach**:

### 1. **PostgreSQL** (Relational Database)
- **Purpose:** Store structured data (patients, appointments, billing, etc.)
- **Why:** ACID compliance, complex queries, relationships, data integrity
- **Tables:** 8 main tables (patients, appointments, medical_records, lab_tests, prescriptions, billing, doctors, beds)

### 2. **ChromaDB** (Vector Database)
- **Purpose:** Semantic search of medical records and documents
- **Why:** Enable natural language queries, similarity search, AI-powered retrieval
- **Use Cases:** 
  - "Find patients with similar symptoms"
  - "Search medical history for diabetes treatments"
  - "Find related lab test results"

### 3. **JSON Files** (Current Implementation)
- **Purpose:** Temporary storage during development
- **Files:** `data/patients_database.json`, `data/appointments_database.json`, etc.
- **Note:** Will migrate to PostgreSQL in production

---

## 📦 Installation Steps

### Step 1: Install PostgreSQL

**Windows:**
```powershell
# Download from: https://www.postgresql.org/download/windows/
# Or use Chocolatey:
choco install postgresql

# Start PostgreSQL service
net start postgresql-x64-14
```

**Verify Installation:**
```powershell
psql --version
```

### Step 2: Create Database

```powershell
# Login to PostgreSQL
psql -U postgres

# In PostgreSQL prompt:
CREATE DATABASE hospital_db;
\c hospital_db
\q
```

### Step 3: Install Python Dependencies

```powershell
pip install sqlalchemy psycopg2-binary chromadb sentence-transformers
```

**Package Details:**
- `sqlalchemy` - ORM for PostgreSQL
- `psycopg2-binary` - PostgreSQL adapter
- `chromadb` - Vector database
- `sentence-transformers` - Embeddings for semantic search

### Step 4: Create Database Schema

```powershell
cd "d:\ai agent by myself\ai agent"
python src/database_schema.py
```

This will create all 8 tables in PostgreSQL.

### Step 5: Verify Database

```powershell
# Login to PostgreSQL
psql -U postgres -d hospital_db

# List tables
\dt

# Should show:
# patients, appointments, medical_records, lab_tests, 
# prescriptions, billing, doctors, beds
```

---

## 🔧 Configuration

### Database Connection

Edit `src/database_schema.py` or create `.env` file:

```env
DB_HOST=localhost
DB_PORT=5432
DB_NAME=hospital_db
DB_USER=postgres
DB_PASSWORD=your_password
```

### ChromaDB Setup

ChromaDB will store data in local directory:
```
data/chroma_db/
```

No additional configuration needed for development.

---

## 📊 Database Schema Overview

### 1. **patients** Table
- Primary Key: `patient_id` (e.g., REG2025123456)
- Fields: Demographics, contact info, insurance, emergency contact
- Relationships: Has many appointments, medical records, lab tests, prescriptions, billing

### 2. **appointments** Table
- Primary Key: `appointment_id`
- Foreign Key: `patient_id` → patients
- Fields: Date, time, doctor, department, status, calendar_event_id
- Status: Scheduled, Confirmed, Completed, Cancelled, No-Show

### 3. **medical_records** Table
- Primary Key: `record_id`
- Foreign Key: `patient_id` → patients
- Fields: Visit date, diagnosis, treatment plan, vitals, doctor notes
- JSON Fields: allergies, chronic_conditions, past_surgeries

### 4. **lab_tests** Table
- Primary Key: `test_id`
- Foreign Key: `patient_id` → patients
- Fields: Test name, category, results, reference range, status
- Status: Ordered, Collected, Processing, Completed, Cancelled

### 5. **prescriptions** Table
- Primary Key: `prescription_id`
- Foreign Key: `patient_id` → patients
- Fields: Doctor, medications (JSON), instructions, validity
- Status: Active, Completed, Cancelled, Expired

### 6. **billing** Table
- Primary Key: `bill_id`
- Foreign Key: `patient_id` → patients
- Fields: Charges breakdown, totals, payment status, insurance claim
- Payment Status: Pending, Partial, Paid, Overdue

### 7. **doctors** Table
- Primary Key: `doctor_id`
- Fields: Name, specialization, qualification, schedule (JSON)
- Status: Active, On Leave, Inactive

### 8. **beds** Table
- Primary Key: `bed_id`
- Fields: Ward, room, bed number, type, occupancy, daily rate
- Status: Available, Occupied, Under Maintenance, Reserved

---

## 🚀 Migration from JSON to PostgreSQL

Once PostgreSQL is set up, we'll create a migration script:

```python
# tools/migrate_to_postgres.py
from src.database_schema import *
from tools.database_tool import load_db

def migrate_patients():
    """Migrate patients from JSON to PostgreSQL"""
    json_db = load_db('data/patients_database.json')
    engine = create_database_engine()
    session = get_session(engine)
    
    for patient_id, data in json_db.items():
        patient = Patient(
            patient_id=data['patient_id'],
            first_name=data['first_name'],
            last_name=data['last_name'],
            # ... map all fields
        )
        session.add(patient)
    
    session.commit()
    print(f"✅ Migrated {len(json_db)} patients")
```

---

## 🔍 Vector Search with ChromaDB

### Setup ChromaDB Collection

```python
import chromadb
from chromadb.config import Settings

# Initialize ChromaDB
client = chromadb.Client(Settings(
    chroma_db_impl="duckdb+parquet",
    persist_directory="data/chroma_db"
))

# Create collection for medical records
collection = client.create_collection(
    name="medical_records",
    metadata={"description": "Patient medical records for semantic search"}
)
```

### Add Medical Records

```python
# Add medical records with embeddings
collection.add(
    documents=["Patient diagnosed with diabetes type 2..."],
    metadatas=[{"patient_id": "REG2025123456", "date": "2025-10-15"}],
    ids=["record_001"]
)
```

### Semantic Search

```python
# Search for similar medical records
results = collection.query(
    query_texts=["symptoms of diabetes"],
    n_results=5
)
```

---

## 🧪 Testing Database Tools

### Test CRUD Operations

```powershell
cd "d:\ai agent by myself\ai agent"
python tools/database_tool.py
```

### Test Individual Tools

```python
from tools.database_tool import *

# Create record
tool = CreateRecordTool()
result = tool._run(
    table_name="appointments",
    record_data={
        "appointment_id": "APT2025001",
        "patient_id": "REG2025123456",
        "appointment_date": "2025-10-20",
        "appointment_time": "10:00 AM",
        "doctor_name": "Dr. Smith",
        "status": "Scheduled"
    }
)
print(result)
```

---

## 📊 Current Status

✅ **Completed:**
- Database schema designed (8 tables)
- JSON-based database tools (7 CRUD tools)
- SQLAlchemy models defined
- Tool interfaces created

🔄 **In Progress:**
- PostgreSQL setup and testing
- ChromaDB integration
- Migration scripts

⏳ **Pending:**
- Database backups and recovery
- Performance optimization
- Connection pooling
- Query optimization

---

## 🔐 Security Considerations

### For Production:

1. **Use Environment Variables**
   ```python
   import os
   DB_PASSWORD = os.getenv('DB_PASSWORD')
   ```

2. **Enable SSL for PostgreSQL**
   ```python
   engine = create_engine(database_url, connect_args={'sslmode': 'require'})
   ```

3. **Implement Row-Level Security**
   ```sql
   CREATE POLICY patient_access ON patients
   FOR ALL TO hospital_staff
   USING (patient_id = current_user_patient_id());
   ```

4. **Regular Backups**
   ```powershell
   pg_dump -U postgres hospital_db > backup.sql
   ```

---

## 💡 Tips

1. **Development:** Use JSON database (current implementation)
2. **Testing:** Set up local PostgreSQL
3. **Production:** Use managed PostgreSQL (AWS RDS, Azure Database, etc.)
4. **Scaling:** Add read replicas for heavy queries
5. **Monitoring:** Use pg_stat_statements for query analysis

---

## 📚 Resources

- PostgreSQL Documentation: https://www.postgresql.org/docs/
- SQLAlchemy Tutorial: https://docs.sqlalchemy.org/
- ChromaDB Documentation: https://docs.trychroma.com/
- Database Design Best Practices: https://www.postgresql.org/docs/current/ddl.html

---

**Last Updated:** October 16, 2025  
**Status:** JSON Database ✅ | PostgreSQL Setup ⏳ | ChromaDB Integration ⏳
