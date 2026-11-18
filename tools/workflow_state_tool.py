"""
Workflow State Persistence Tool
Saves and retrieves patient workflow state for resume functionality
"""

import json
import os
from typing import Optional, Type, Dict, Any
from datetime import datetime
from pydantic import BaseModel, Field
from langchain.tools import BaseTool


# ==================== CUSTOM JSON ENCODER ====================

class DateTimeEncoder(json.JSONEncoder):
    """Custom JSON encoder that handles datetime objects"""
    def default(self, obj):
        if isinstance(obj, datetime):
            return obj.isoformat()
        return super().default(obj)


# ==================== STATE DATABASE FILE ====================
STATE_DB_FILE = 'data/workflow_states.json'


# ==================== INPUT SCHEMAS ====================

class SaveWorkflowStateInput(BaseModel):
    """Input for saving workflow state."""
    patient_id: str = Field(description="Patient ID to save state for")
    state_data: dict = Field(description="Complete workflow state dictionary")


class LoadWorkflowStateInput(BaseModel):
    """Input for loading workflow state."""
    patient_id: str = Field(description="Patient ID to load state for")


class DeleteWorkflowStateInput(BaseModel):
    """Input for deleting workflow state."""
    patient_id: str = Field(description="Patient ID to delete state for")


class GetAllWorkflowStatesInput(BaseModel):
    """Input for getting all workflow states."""
    status_filter: Optional[str] = Field(default=None, description="Filter by status: running, paused, completed")


# ==================== HELPER FUNCTIONS ====================

def _ensure_state_file_exists():
    """Ensure the state database file exists"""
    os.makedirs(os.path.dirname(STATE_DB_FILE), exist_ok=True)
    
    if not os.path.exists(STATE_DB_FILE):
        with open(STATE_DB_FILE, 'w') as f:
            json.dump({}, f, indent=2)


def _load_all_states() -> dict:
    """Load all workflow states from database"""
    _ensure_state_file_exists()
    
    try:
        with open(STATE_DB_FILE, 'r', encoding='utf-8') as f:
            return json.load(f)
    except Exception as e:
        print(f"⚠️ Error loading states: {e}")
        return {}


def _save_all_states(states: dict) -> bool:
    """Save all workflow states to database"""
    try:
        with open(STATE_DB_FILE, 'w', encoding='utf-8') as f:
            json.dump(states, f, indent=2, ensure_ascii=False, cls=DateTimeEncoder)
        return True
    except Exception as e:
        print(f"❌ Error saving states: {e}")
        return False


# ==================== STATE PERSISTENCE TOOLS ====================

class SaveWorkflowStateTool(BaseTool):
    """Tool for saving patient workflow state with dual-database support."""
    
    name: str = "save_workflow_state"
    description: str = """Save patient's current workflow state to database (JSON + PostgreSQL). 
    Allows workflow to be resumed later from the same point."""
    args_schema: Type[BaseModel] = SaveWorkflowStateInput
    
    def _run(self, patient_id: str, state_data: dict) -> str:
        try:
            # Try dual-database manager first (if available)
            try:
                from src.dual_database import db_manager
                result = db_manager.save_workflow_state(patient_id, state_data)
                
                if result["success"]:
                    current_stage = state_data.get('current_stage', 'unknown')
                    next_action = state_data.get('next_action', 'unknown')
                    
                    db_status = []
                    if result["json_saved"]:
                        db_status.append("✅ JSON")
                    if result.get("postgresql_saved"):
                        db_status.append("✅ PostgreSQL")
                    
                    return f"""✅ Workflow State Saved Successfully!

💾 State Details:
- Patient ID: {patient_id}
- Current Stage: {current_stage}
- Next Action: {next_action}
- Last Saved: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
- Databases: {', '.join(db_status)}

📊 State includes:
  • Patient information
  • Workflow progress
  • Medical history
  • Test results
  • Billing information
  • All agent outputs

🔄 Patient can now resume workflow from this point.
"""
                else:
                    return f"❌ Failed to save workflow state: {result.get('errors', [])}"
                    
            except ImportError:
                # Fallback to JSON-only if dual-database not available
                states = _load_all_states()
                workflow_state = {
                    **state_data,
                    "last_saved": datetime.now().isoformat(),
                    "last_updated": datetime.now().isoformat(),
                    "state_version": "1.0"
                }
                states[patient_id] = workflow_state
                
                if _save_all_states(states):
                    current_stage = state_data.get('current_stage', 'unknown')
                    return f"✅ State saved (JSON only): {patient_id} - Stage: {current_stage}"
                else:
                    return f"❌ Failed to save workflow state for patient {patient_id}"
        
        except Exception as e:
            return f"❌ Error saving workflow state: {str(e)}"
    
    async def _arun(self, patient_id: str, state_data: dict) -> str:
        return self._run(patient_id, state_data)


class LoadWorkflowStateTool(BaseTool):
    """Tool for loading patient workflow state."""
    
    name: str = "load_workflow_state"
    description: str = """Load patient's saved workflow state from database. 
    Returns complete state to resume workflow."""
    args_schema: Type[BaseModel] = LoadWorkflowStateInput
    
    def _run(self, patient_id: str) -> dict:
        try:
            state_data = None
            
            # PRIORITY 1: Try Redis cache first (fastest)
            try:
                from database.redis_cache import cache
                state_data = cache.get_cached_workflow_state(patient_id)
                if state_data:
                    print(f"✅ Loaded state from Redis cache for {patient_id}")
            except Exception as cache_err:
                print(f"⚠️ Redis cache failed: {cache_err}")
            
            # PRIORITY 2: Try individual patient file (created by reset scripts)
            if not state_data:
                individual_file = f'data/workflow_states/{patient_id}.json'
                if os.path.exists(individual_file):
                    try:
                        with open(individual_file, 'r', encoding='utf-8') as f:
                            state_data = json.load(f)
                            print(f"✅ Loaded state from individual file: {individual_file}")
                    except Exception as file_err:
                        print(f"⚠️ Individual file load failed: {file_err}")
            
            # PRIORITY 3: Try old combined states file (backward compatibility)
            if not state_data:
                states = _load_all_states()
                if patient_id in states:
                    state_data = states[patient_id]
                    print(f"✅ Loaded state from combined states file")
            
            # No state found anywhere
            if not state_data:
                return {
                    "success": False,
                    "message": f"❌ No saved workflow state found for patient {patient_id}",
                    "patient_id": patient_id
                }
            
            # Return state with success flag
            return {
                "success": True,
                "message": f"✅ Workflow state loaded successfully for patient {patient_id}",
                "patient_id": patient_id,
                "state": state_data,
                "current_stage": state_data.get('current_stage', 'unknown'),
                "next_action": state_data.get('next_action', 'unknown'),
                "last_saved": state_data.get('last_saved', 'unknown'),
                "can_resume": True
            }
        
        except Exception as e:
            return {
                "success": False,
                "message": f"❌ Error loading workflow state: {str(e)}",
                "patient_id": patient_id
            }
    
    async def _arun(self, patient_id: str) -> dict:
        return self._run(patient_id)


class DeleteWorkflowStateTool(BaseTool):
    """Tool for deleting workflow state."""
    
    name: str = "delete_workflow_state"
    description: str = """Delete patient's workflow state from database. 
    Use when workflow is completed or cancelled."""
    args_schema: Type[BaseModel] = DeleteWorkflowStateInput
    
    def _run(self, patient_id: str) -> str:
        try:
            # Load all states
            states = _load_all_states()
            
            # Check if state exists
            if patient_id not in states:
                return f"⚠️ No workflow state found for patient {patient_id}"
            
            # Delete state
            deleted_state = states.pop(patient_id)
            
            # Save updated states
            if _save_all_states(states):
                return f"""✅ Workflow State Deleted Successfully!

🗑️ Deleted State:
- Patient ID: {patient_id}
- Last Stage: {deleted_state.get('current_stage', 'unknown')}
- Last Saved: {deleted_state.get('last_saved', 'unknown')}

💡 Workflow state has been permanently removed from database.
"""
            else:
                return f"❌ Failed to delete workflow state for patient {patient_id}"
        
        except Exception as e:
            return f"❌ Error deleting workflow state: {str(e)}"
    
    async def _arun(self, patient_id: str) -> str:
        return self._run(patient_id)


class GetAllWorkflowStatesTool(BaseTool):
    """Tool for getting all workflow states."""
    
    name: str = "get_all_workflow_states"
    description: str = """Get all saved workflow states. 
    Optionally filter by status (running, paused, completed)."""
    args_schema: Type[BaseModel] = GetAllWorkflowStatesInput
    
    def _run(self, status_filter: Optional[str] = None) -> dict:
        try:
            # Load all states
            states = _load_all_states()
            
            if not states:
                return {
                    "success": True,
                    "message": "📭 No saved workflow states found.",
                    "count": 0,
                    "states": []
                }
            
            # Filter by status if provided
            filtered_states = []
            for patient_id, state_data in states.items():
                if status_filter:
                    workflow_status = state_data.get('workflow_status', 'running')
                    if workflow_status != status_filter:
                        continue
                
                filtered_states.append({
                    "patient_id": patient_id,
                    "patient_name": state_data.get('name', 'Unknown'),
                    "current_stage": state_data.get('current_stage', 'unknown'),
                    "next_action": state_data.get('next_action', 'unknown'),
                    "last_saved": state_data.get('last_saved', 'unknown'),
                    "workflow_status": state_data.get('workflow_status', 'running')
                })
            
            return {
                "success": True,
                "message": f"✅ Retrieved {len(filtered_states)} workflow states",
                "count": len(filtered_states),
                "filter": status_filter or "none",
                "states": filtered_states
            }
        
        except Exception as e:
            return {
                "success": False,
                "message": f"❌ Error retrieving workflow states: {str(e)}",
                "count": 0,
                "states": []
            }
    
    async def _arun(self, status_filter: Optional[str] = None) -> dict:
        return self._run(status_filter)


# ==================== STANDALONE FUNCTIONS (For Direct Use) ====================

def save_workflow_state(patient_id: str, state: dict) -> bool:
    """
    Direct function to save workflow state (no tool wrapper)
    Use this in agents: save_workflow_state(state["patient_id"], state)
    """
    try:
        states = _load_all_states()
        
        workflow_state = {
            **state,
            "last_saved": datetime.now().isoformat(),
            "last_updated": datetime.now().isoformat(),
            "state_version": "1.0"
        }
        
        states[patient_id] = workflow_state
        
        return _save_all_states(states)
    except Exception as e:
        print(f"❌ Error in save_workflow_state: {e}")
        return False


def load_workflow_state(patient_id: str) -> Optional[dict]:
    """
    Direct function to load workflow state (no tool wrapper)
    Returns state dict or None if not found
    """
    try:
        states = _load_all_states()
        return states.get(patient_id)
    except Exception as e:
        print(f"❌ Error in load_workflow_state: {e}")
        return None


def delete_workflow_state(patient_id: str) -> bool:
    """
    Direct function to delete workflow state (no tool wrapper)
    """
    try:
        states = _load_all_states()
        
        if patient_id in states:
            states.pop(patient_id)
            return _save_all_states(states)
        
        return False
    except Exception as e:
        print(f"❌ Error in delete_workflow_state: {e}")
        return False


def get_all_workflow_states(status_filter: Optional[str] = None) -> list:
    """
    Direct function to get all workflow states (no tool wrapper)
    Returns list of workflow states
    """
    try:
        states = _load_all_states()
        
        result = []
        for patient_id, state_data in states.items():
            if status_filter:
                workflow_status = state_data.get('workflow_status', 'running')
                if workflow_status != status_filter:
                    continue
            
            result.append({
                "patient_id": patient_id,
                "patient_name": state_data.get('name', 'Unknown'),
                "current_stage": state_data.get('current_stage', 'unknown'),
                "next_action": state_data.get('next_action', 'unknown'),
                "last_saved": state_data.get('last_saved', 'unknown'),
                "workflow_status": state_data.get('workflow_status', 'running'),
                "state": state_data
            })
        
        return result
    except Exception as e:
        print(f"❌ Error in get_all_workflow_states: {e}")
        return []


# ==================== HELPER FUNCTION ====================

def get_all_state_tools():
    """Get all workflow state tools for the agent"""
    return [
        SaveWorkflowStateTool(),
        LoadWorkflowStateTool(),
        DeleteWorkflowStateTool(),
        GetAllWorkflowStatesTool()
    ]


# ==================== USAGE EXAMPLE ====================

if __name__ == "__main__":
    print("\n" + "="*70)
    print("💾 WORKFLOW STATE PERSISTENCE TOOLS - Testing")
    print("="*70)
    
    # Example 1: Save workflow state
    print("\n1️⃣ Saving Workflow State...")
    test_state = {
        "patient_id": "REG2025001",
        "name": "Test Patient",
        "age": 45,
        "current_stage": "lab_coordination",
        "next_action": "results_analysis",
        "workflow_status": "running",
        "test_results": [
            {"test_name": "Blood Sugar", "value": "120 mg/dL"}
        ]
    }
    
    result1 = save_workflow_state("REG2025001", test_state)
    print(f"Save Result: {'✅ Success' if result1 else '❌ Failed'}")
    
    # Example 2: Load workflow state
    print("\n2️⃣ Loading Workflow State...")
    loaded_state = load_workflow_state("REG2025001")
    
    if loaded_state:
        print(f"✅ State Loaded Successfully!")
        print(f"   Current Stage: {loaded_state.get('current_stage')}")
        print(f"   Next Action: {loaded_state.get('next_action')}")
        print(f"   Last Saved: {loaded_state.get('last_saved')}")
    else:
        print("❌ No state found")
    
    # Example 3: Get all states
    print("\n3️⃣ Getting All Workflow States...")
    all_states = get_all_workflow_states()
    print(f"Found {len(all_states)} saved workflow(s)")
    
    for state_info in all_states:
        print(f"   • {state_info['patient_name']} ({state_info['patient_id']}) - Stage: {state_info['current_stage']}")
    
    # Example 4: Delete workflow state
    print("\n4️⃣ Deleting Workflow State...")
    delete_result = delete_workflow_state("REG2025001")
    print(f"Delete Result: {'✅ Success' if delete_result else '❌ Failed'}")
    
    print("\n" + "="*70)
    print("✅ State Persistence Test Complete!")
    print("="*70)
    
    print("\n💡 Integration Instructions:")
    print("1. Import in workflow: from tools.workflow_state_tool import save_workflow_state, load_workflow_state")
    print("2. Save after each agent: save_workflow_state(state['patient_id'], state)")
    print("3. Resume workflow: loaded_state = load_workflow_state(patient_id)")
    print("4. Delete on completion: delete_workflow_state(patient_id)")
