"""
Fix missing workflow_doc_id in patient state
"""
import json
from database.redis_cache import cache

PATIENT_ID = "REG2025055769"
WORKFLOW_DOC_ID = "1kHIPTWHG5F7F7fRL3HI19D4ELZIvOO-ALYX8GQ5YnAY"
WORKFLOW_DOC_URL = f"https://docs.google.com/document/d/{WORKFLOW_DOC_ID}/edit"

# Update JSON file
json_path = f"data/workflow_states/{PATIENT_ID}.json"
with open(json_path, 'r') as f:
    state = json.load(f)

state['workflow_doc_id'] = WORKFLOW_DOC_ID
state['workflow_doc_url'] = WORKFLOW_DOC_URL
state['stage_data']['registration']['workflow_doc_created'] = True

with open(json_path, 'w') as f:
    json.dump(state, f, indent=2)

print(f"✅ Updated JSON state with workflow_doc_id")

# Update Redis cache
cache.cache_workflow_state(PATIENT_ID, state)
print(f"✅ Updated Redis cache with workflow_doc_id")

print(f"\n📄 Workflow Document: {WORKFLOW_DOC_URL}")
