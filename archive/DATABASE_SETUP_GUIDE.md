# 🚀 POSTGRESQL + REDIS SETUP GUIDE

## What We're Adding

✅ **PostgreSQL Database** - Replace JSON files with proper database
✅ **Redis Cache** - Fast caching for OTP, sessions, LLM responses  
✅ **Smart OTP System** - SMS (Twilio) + Email fallback
✅ **Session Persistence** - Survive page refresh
✅ **Context-aware Agent** - Answer questions beyond workflow

---

## 📦 Installation Steps

### Step 1: Install Dependencies

```powershell
# Install new packages
pip install psycopg2-binary redis python-dotenv

# Or install all requirements
pip install -r requirements.txt
```

### Step 2: Install PostgreSQL

**Option A: Download PostgreSQL (Recommended)**
1. Download: https://www.postgresql.org/download/windows/
2. Install with default settings
3. Remember the password you set for `postgres` user
4. Default port: 5432

**Option B: Use Docker (Advanced)**
```powershell
docker run --name hospital-postgres `
  -e POSTGRES_PASSWORD=postgres `
  -e POSTGRES_DB=hospital_ai `
  -p 5432:5432 `
  -d postgres:15
```

### Step 3: Install Redis

**Option A: Download Redis for Windows**
1. Download: https://github.com/microsoftarchive/redis/releases
2. Download `Redis-x64-3.0.504.msi`
3. Install with default settings
4. Default port: 6379

**Option B: Use Docker (Recommended)**
```powershell
docker run --name hospital-redis `
  -p 6379:6379 `
  -d redis:7-alpine
```

**Option C: Use Redis Cloud (Free Tier)**
- Sign up: https://redis.com/try-free/
- Get connection details
- Update `.env` with cloud Redis URL

### Step 4: Update .env File

Already updated! Verify these settings:

```properties
# PostgreSQL
POSTGRES_HOST=localhost
POSTGRES_PORT=5432
POSTGRES_DB=hospital_ai
POSTGRES_USER=postgres
POSTGRES_PASSWORD=Samp@786

# Redis
REDIS_HOST=localhost
REDIS_PORT=6379
REDIS_DB=0
REDIS_PASSWORD=  # Empty for local Redis
```

### Step 5: Initialize Database

```powershell
# Run database initialization
python -c "from database.db_manager import init_database; init_database()"
```

You should see:
```
✅ Database connection pool initialized
✅ Database initialized successfully!
```

### Step 6: Test Connections

```powershell
# Test PostgreSQL
python -c "from database.db_manager import DatabaseManager; db = DatabaseManager(); print('PostgreSQL OK!')"

# Test Redis
python -c "from database.redis_cache import cache; print(cache.get_stats())"
```

---

## 🎯 What Each Component Does

### PostgreSQL Database

**Tables Created:**
- `patients` - All patient information
- `workflow_states` - Current workflow progress
- `otp_verifications` - OTP codes and attempts
- `medical_records` - Medical history
- `appointments` - Scheduled appointments
- `lab_tests` - Lab test orders and results
- `payments` - Payment transactions
- `documents` - Uploaded documents metadata
- `notifications` - Sent notifications log

**Benefits:**
- ✅ ACID compliance (data integrity)
- ✅ Complex queries (JOIN, GROUP BY, etc.)
- ✅ Handles thousands of patients
- ✅ Automatic backups
- ✅ Concurrent access safe

### Redis Cache

**What It Caches:**
- ⚡ OTP codes (5 min expiry)
- ⚡ User sessions (1 hour expiry)
- ⚡ LLM responses (30 min expiry)
- ⚡ Workflow states (2 hour expiry)
- ⚡ Rate limiting counters

**Benefits:**
- ✅ Super fast (< 1ms response time)
- ✅ Reduces database load
- ✅ Reduces LLM API calls (saves money!)
- ✅ Automatic TTL (Time To Live)

---

## 🔧 How It Works

### Smart OTP System

```python
# Stage 1: Phone number collected
# Check if phone is NEW (not in database)
existing_patient = PatientDB().get_patient_by_phone(phone)

if not existing_patient:
    # NEW patient → Send SMS OTP (uses Twilio credit)
    send_sms_otp(phone)
else:
    # EXISTING patient → Send EMAIL OTP (FREE!)
    send_email_otp(email)

# OTP cached in Redis for 5 minutes
# Max 3 attempts, then invalidate
```

**Twilio Credits Saved:**
- Only send SMS for NEW registrations
- Existing patients use email OTP
- Typical usage: ~1 SMS per patient (₹0.50)
- Your $10 credit = ~600 new patient registrations!

### Session Persistence

```python
# On login
session_id = f"{email}_{timestamp}"
cache.set_session(session_id, {
    "patient_id": "REG2025123456",
    "current_stage": 3,
    "conversation_history": [...]
}, ttl=3600)  # 1 hour

# On page refresh
state = cache.get_session(session_id)
if state:
    # Restore workflow exactly where user left off
    agent = WorkflowChatAgent(email, patient_id=state["patient_id"])
    agent.state = state
```

### Context-aware Agent

```python
# User asks: "What are my lab test results?"
# Even if currently in Stage 1 (Registration)

# Agent can:
1. Search patient history in PostgreSQL
2. Retrieve lab results from database
3. Answer using RAG (ChromaDB medical knowledge)
4. Return to workflow conversation

# No longer stuck in linear flow!
```

---

## 📊 Database Schema Overview

```
patients
├── patient_id (PK)
├── email, phone, name, DOB
├── drive_folder_url
├── spreadsheet_id
└── emergency_contact

workflow_states
├── patient_id (FK)
├── current_stage
├── stage_data (JSONB)
└── conversation_history (JSONB)

otp_verifications
├── phone
├── otp_code
├── expires_at
└── attempts

medical_records
├── patient_id (FK)
├── allergies, medications
├── chief_complaint
└── risk_analysis

appointments
├── patient_id (FK)
├── appointment_date
├── doctor_name
└── status

lab_tests
├── patient_id (FK)
├── test_name
├── result_value
└── status

payments
├── patient_id (FK)
├── amount
├── gateway_transaction_id
└── status
```

---

## 🧪 Testing Everything

### Test 1: Database Connection

```powershell
python
```

```python
from database.db_manager import PatientDB, WorkflowStateDB, OTPDB

# Test patient creation
patient_db = PatientDB()
patient_id = patient_db.create_patient({
    'patient_id': 'TEST001',
    'first_name': 'Test',
    'last_name': 'Patient',
    'email': 'test@example.com',
    'phone': '+91-9999999999',
    'date_of_birth': '1990-01-01',
    'gender': 'Male',
    'address': 'Test Address',
    'city': None,
    'state': None,
    'pincode': None,
    'drive_folder_id': None,
    'drive_folder_url': None,
    'spreadsheet_id': None,
    'emergency_contact_name': None,
    'emergency_contact_phone': None,
    'emergency_contact_relation': None
})

print(f"✅ Created patient: {patient_id}")

# Retrieve patient
patient = patient_db.get_patient_by_email('test@example.com')
print(f"✅ Retrieved: {patient['full_name']}")
```

### Test 2: Redis Cache

```python
from database.redis_cache import cache

# Test OTP caching
cache.set_otp('+91-9999999999', '123456')
print(f"✅ OTP cached")

# Verify OTP
valid = cache.verify_otp('+91-9999999999', '123456')
print(f"✅ OTP verified: {valid}")

# Test session caching
cache.set_session('test_session', {'user': 'test', 'stage': 1})
session = cache.get_session('test_session')
print(f"✅ Session retrieved: {session}")

# Get stats
stats = cache.get_stats()
print(f"✅ Redis stats: {stats}")
```

### Test 3: Complete Registration Flow

```powershell
# Start backend
uvicorn main:app --reload

# Open frontend
# http://localhost:3000/loginPage

# Register new patient:
# 1. Name, phone, DOB, etc.
# 2. Get OTP (SMS for new, Email for existing)
# 3. Verify OTP
# 4. Complete registration
# 5. Refresh page
# 6. Login again
# 7. ✅ Should restore to exact stage!
```

---

## 🎁 What's Next

Once PostgreSQL and Redis are working:

1. ✅ Implement OTP verification in Stage 1
2. ✅ Add Google Maps address validation
3. ✅ Add context-aware Q&A (beyond workflow)
4. ✅ Add payment gateway (Razorpay)
5. ✅ Complete Stages 5-11

---

## 🐛 Troubleshooting

### PostgreSQL Won't Connect

```powershell
# Check if PostgreSQL is running
Get-Service postgresql*

# If not running
Start-Service postgresql-x64-15  # Or your version

# Test connection
psql -U postgres -d hospital_ai
# Password: your_password
```

### Redis Won't Connect

```powershell
# Check if Redis is running (Windows Service)
Get-Service redis*

# If using Docker
docker ps
docker start hospital-redis

# Test connection
redis-cli ping
# Should return: PONG
```

### Database Already Exists Error

```powershell
# Drop and recreate
psql -U postgres
DROP DATABASE hospital_ai;
CREATE DATABASE hospital_ai;
\q

# Re-run initialization
python -c "from database.db_manager import init_database; init_database()"
```

### Redis Not Available (Non-Critical)

Don't worry! The system falls back to in-memory cache.
Redis is optional but recommended for production.

---

## 📝 Environment Variables Summary

```properties
# PostgreSQL (REQUIRED for database migration)
POSTGRES_HOST=localhost
POSTGRES_PORT=5432
POSTGRES_DB=hospital_ai
POSTGRES_USER=postgres
POSTGRES_PASSWORD=your_password

# Redis (OPTIONAL - will fallback to in-memory)
REDIS_HOST=localhost
REDIS_PORT=6379
REDIS_DB=0
REDIS_PASSWORD=

# Twilio (for SMS OTP)
TWILIO_ACCOUNT_SID=your_sid
TWILIO_AUTH_TOKEN=your_token
TWILIO_FROM_NUMBER=+14067809945

# Google Services (already configured)
PATIENT_TRACKING_SHEET_ID=1pt6e8BF3QHp2-YAUyHAQZt9SDS9KmMwpH434fMMOoW4
```

---

## ✅ Ready to Proceed?

Run these commands in order:

```powershell
# 1. Install dependencies
pip install -r requirements.txt

# 2. Verify PostgreSQL installed and running
Get-Service postgresql*

# 3. Initialize database
python -c "from database.db_manager import init_database; init_database()"

# 4. Test connections
python -c "from database.db_manager import DatabaseManager; DatabaseManager()"
python -c "from database.redis_cache import cache; print(cache.is_available())"

# 5. Ready!
```

**Status**: Infrastructure ready for next features! 🎉
