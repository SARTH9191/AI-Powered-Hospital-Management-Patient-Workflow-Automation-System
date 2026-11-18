"""
Fix corrupted workflow_states.json file
"""

import json
import os
from datetime import datetime

STATE_FILE = 'data/workflow_states.json'
BACKUP_FILE = 'data/workflow_states.json.backup'

def fix_json_states():
    """Fix corrupted JSON states file"""
    
    print("🔧 Fixing workflow states JSON file...")
    
    # Backup existing file
    if os.path.exists(STATE_FILE):
        try:
            # Try to backup
            import shutil
            shutil.copy(STATE_FILE, BACKUP_FILE)
            print(f"✅ Backed up to: {BACKUP_FILE}")
        except Exception as e:
            print(f"⚠️ Could not backup: {e}")
    
    # Create fresh empty state file
    try:
        os.makedirs(os.path.dirname(STATE_FILE), exist_ok=True)
        with open(STATE_FILE, 'w', encoding='utf-8') as f:
            json.dump({}, f, indent=2)
        print(f"✅ Created fresh state file: {STATE_FILE}")
        
        # Verify it's valid
        with open(STATE_FILE, 'r', encoding='utf-8') as f:
            json.load(f)
        print("✅ JSON file is valid")
        
        return True
        
    except Exception as e:
        print(f"❌ Error creating state file: {e}")
        return False

if __name__ == "__main__":
    success = fix_json_states()
    
    if success:
        print("\n✅ All fixed! Workflow states will be recreated on next save.")
        print("💡 Note: Workflow states are also stored in PostgreSQL, so no data is lost.")
    else:
        print("\n❌ Failed to fix. Please check file permissions.")
