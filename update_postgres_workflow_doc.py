"""
Update PostgreSQL workflow state with workflow_doc_id
"""
import json
from database.db_manager import WorkflowStateDB

PATIENT_ID = "REG2025055769"

# Load state from JSON (which has workflow_doc_id)
with open(f'data/workflow_states/{PATIENT_ID}.json', 'r') as f:
    state = json.load(f)

print(f"📄 Loaded state from JSON:")
print(f"   workflow_doc_id: {state.get('workflow_doc_id')}")
print(f"   workflow_doc_url: {state.get('workflow_doc_url')}")
print(f"   current_stage: {state.get('current_stage')}")

# Save to PostgreSQL
workflow_db = WorkflowStateDB()
success = workflow_db.save_state(PATIENT_ID, state)

if success:
    print(f"\n✅ Updated PostgreSQL with workflow_doc_id")
else:
    print(f"\n❌ Failed to update PostgreSQL")

# Verify
loaded_state = workflow_db.load_state(PATIENT_ID)
if loaded_state:
    print(f"\n✅ Verified - PostgreSQL now has:")
    print(f"   workflow_doc_id: {loaded_state.get('workflow_doc_id')}")
    print(f"   workflow_doc_url: {loaded_state.get('workflow_doc_url')}")
else:
    print(f"\n❌ Could not verify")
