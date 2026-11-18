"""
Update Redis cache with workflow_doc_id
"""
import json
from database.redis_cache import cache

PATIENT_ID = "REG2025055769"

# Load state from JSON
with open(f'data/workflow_states/{PATIENT_ID}.json', 'r') as f:
    state = json.load(f)

# Update Redis cache
cache.cache_workflow_state(PATIENT_ID, state)

print(f"✅ Updated Redis cache for patient {PATIENT_ID}")
print(f"📄 Workflow Doc ID: {state.get('workflow_doc_id')}")
print(f"🔗 Workflow Doc URL: {state.get('workflow_doc_url')}")
print(f"\n💡 Now restart the backend (Ctrl+C and run 'python main.py' again)")
