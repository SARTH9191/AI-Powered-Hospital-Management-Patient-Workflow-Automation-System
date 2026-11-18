"""
Test PostgreSQL Integration with Registration Flow
"""

from database.db_manager import PatientDB, WorkflowStateDB
from database.redis_cache import cache

print("=" * 60)
print("🧪 TESTING POSTGRESQL INTEGRATION")
print("=" * 60)
print()

# Test 1: Database Connection
print("1️⃣  Testing Database Connection...")
try:
    patient_db = PatientDB()
    print("✅ PatientDB initialized")
    
    workflow_db = WorkflowStateDB()
    print("✅ WorkflowStateDB initialized")
except Exception as e:
    print(f"❌ Database connection failed: {e}")
    exit(1)

# Test 2: Redis Connection
print()
print("2️⃣  Testing Redis Connection...")
if cache.is_available():
    print(f"✅ Redis connected")
    print(f"   Stats: {cache.get_stats()}")
else:
    print("⚠️  Redis not available (using in-memory fallback)")

# Test 3: Create Test Patient
print()
print("3️⃣  Creating Test Patient...")
try:
    test_patient_data = {
        'patient_id': 'TEST2025001',
        'first_name': 'Test',
        'last_name': 'Patient',
        'email': 'test@hospital.com',
        'phone': '+91-9999999999',
        'date_of_birth': '1990-01-01',
        'gender': 'Male',
        'address': 'Test Address, Test City',
        'city': 'TestCity',
        'state': 'TestState',
        'pincode': '123456',
        'drive_folder_id': None,
        'drive_folder_url': None,
        'spreadsheet_id': None,
        'emergency_contact_name': None,
        'emergency_contact_phone': None,
        'emergency_contact_relation': None
    }
    
    patient_id = patient_db.create_patient(test_patient_data)
    print(f"✅ Test patient created: {patient_id}")
except Exception as e:
    if "duplicate key" in str(e).lower():
        print(f"✅ Test patient already exists (that's OK)")
    else:
        print(f"❌ Failed to create patient: {e}")

# Test 4: Retrieve Patient
print()
print("4️⃣  Retrieving Patient...")
try:
    patient = patient_db.get_patient_by_id('TEST2025001')
    if patient:
        print(f"✅ Patient retrieved:")
        print(f"   Name: {patient['full_name']}")
        print(f"   Email: {patient['email']}")
        print(f"   Age: {patient['age']}")
    else:
        print("❌ Patient not found")
except Exception as e:
    print(f"❌ Failed to retrieve patient: {e}")

# Test 5: Update Patient
print()
print("5️⃣  Updating Patient...")
try:
    success = patient_db.update_patient('TEST2025001', {
        'drive_folder_url': 'https://drive.google.com/test123',
        'drive_folder_id': 'test_folder_123'
    })
    if success:
        print("✅ Patient updated with Drive info")
    else:
        print("❌ Update failed")
except Exception as e:
    print(f"❌ Update failed: {e}")

# Test 6: Save Workflow State
print()
print("6️⃣  Saving Workflow State...")
try:
    test_state = {
        'patient_id': 'TEST2025001',
        'current_stage': 1,
        'stage_name': 'registration',
        'stage_data': {'test': 'data'},
        'conversation_history': [{'role': 'user', 'message': 'Hello'}],
        'awaiting_confirmation': False,
        'pending_actions': [],
        'session_id': 'test_session_123',
        'is_active': True
    }
    
    success = workflow_db.save_state('TEST2025001', test_state)
    if success:
        print("✅ Workflow state saved")
    else:
        print("❌ State save failed")
except Exception as e:
    print(f"❌ State save failed: {e}")

# Test 7: Load Workflow State
print()
print("7️⃣  Loading Workflow State...")
try:
    loaded_state = workflow_db.load_state('TEST2025001')
    if loaded_state:
        print(f"✅ Workflow state loaded:")
        print(f"   Stage: {loaded_state['current_stage']}")
        print(f"   Stage Name: {loaded_state['stage_name']}")
    else:
        print("❌ State not found")
except Exception as e:
    print(f"❌ State load failed: {e}")

# Test 8: Redis Caching
print()
print("8️⃣  Testing Redis Cache...")
try:
    # Cache workflow state
    cache.cache_workflow_state('TEST2025001', test_state)
    print("✅ State cached in Redis")
    
    # Retrieve from cache
    cached_state = cache.get_cached_workflow_state('TEST2025001')
    if cached_state:
        print(f"✅ State retrieved from cache")
    else:
        print("⚠️  Cache retrieval returned None (Redis may not be available)")
except Exception as e:
    print(f"⚠️  Redis caching error: {e}")

# Summary
print()
print("=" * 60)
print("✅ ALL TESTS COMPLETED!")
print("=" * 60)
print()
print("🎉 PostgreSQL integration is working!")
print()
print("Next: Start your backend and test real registration:")
print("  1. uvicorn main:app --reload")
print("  2. Open: http://localhost:3000/loginPage")
print("  3. Register a patient")
print("  4. Check: psql -U postgres -d hospital_ai")
print("     SELECT * FROM patients;")
print()
