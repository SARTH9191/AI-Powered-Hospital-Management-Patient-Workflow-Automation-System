"""
Project Cleanup Script
Removes unnecessary files to streamline the project
"""

import os
import shutil
from pathlib import Path

# Project root
PROJECT_ROOT = Path(__file__).parent

# Files to DELETE
DELETE_FILES = [
    # Demo files
    "demo_*.py",
    
    # Test files (keep integration tests)
    "test_phase1_simple.py",
    "test_langchain_twilio.py",
    "test_live_sms.py",
    
    # Old agent files
    "agent.py",
    "workflow_manager.py",
    
    # Temporary/state files
    "quick_test_*.py",
    "create_test_data.py",
    "create_patient_user.py",
    "check_twilio_numbers.py",
    "send_welcome_email.py",
    "add_state_saving.py",
]

# Documentation files to DELETE (keeping only essential)
DELETE_DOCS = [
    "ADMIN_PORTAL_COMPLETE.md",
    "ADMIN_TESTING_GUIDE.md",
    "AI_AGENT_EXPLAINED.md",
    "AI_CHAT_IMPLEMENTATION_COMPLETE.md",
    "AI_CHAT_INTEGRATION_STATUS.md",
    "AI_CHAT_TESTING_GUIDE.md",
    "BACKEND_100_PERCENT_COMPLETE.md",
    "BACKEND_IMPLEMENTATION_PLAN.md",
    "BACKEND_ROUTERS_COMPLETE.md",
    "BACKEND_TODO_STATUS.md",
    "CODEBASE_AUDIT_COMPLETE.md",
    "COMPLETE_PROJECT_PLAN.md",
    "CRITICAL_FIXES_APPLIED.md",
    "DATA_IMPORT_AND_NEXT_PLAN.md",
    "DOCTOR_DASHBOARD_COMPLETE.md",
    "DOCTOR_LAYOUT_FIXES_COMPLETE.md",
    "FINAL_TOOL_FIXES_COMPLETE.md",
    "FRONTEND_BUILD_FIX.md",
    "FRONTEND_PHASE1_COMPLETE.md",
    "FRONTEND_PLAN.md",
    "GOOGLE_TOOLS_ANALYSIS.md",
    "HOW_TO_REFLECT_CHANGES.md",
    "MANUAL_WORKFLOW_TEST_GUIDE.md",
    "NEXT_LEVEL_AI_AGENT_PLAN.md",
    "OPTION_B_COMPLETE.md",
    "PATIENT_CHATBOT_EXPLAINED.md",
    "PATIENT_PORTAL_COMPLETE.md",
    "PHASE1_COMPLETE.md",
    "PHASE1_NOTIFICATION_INTEGRATION_COMPLETE.md",
    "PHASE1_PATIENT_DASHBOARD_COMPLETE.md",
    "PHASE1_SUMMARY.md",
    "PHASE1A_PROGRESS.md",
    "PHASE2_COMPLETE.md",
    "PHASE2_SUMMARY.md",
    "PHASE2_TO_4_ROADMAP.md",
    "PHASE2B_SUMMARY.md",
    "PHASE3_SUMMARY.md",
    "PHASES_1_AND_2_COMPLETE.md",
    "QUICK_ANSWERS.md",
    "RAG_FIXES_COMPLETE.md",
    "REAL_TOOL_INTEGRATIONS_COMPLETE.md",
    "STATE_PERSISTENCE_COMPLETE.md",
    "STATE_PERSISTENCE_TESTING_PLAN.md",
]

# KEEP these essential files
KEEP_FILES = [
    "README.md",
    "PROJECT_STATUS.md",
    "ROADMAP.md",
    "API_README.md",
    "RESTART_PLAN_CHAT_DRIVEN_WORKFLOW.md",
    "COMPLETE_AI_AGENT_FIX_GUIDE.md",
    "requirements.txt",
    "main.py",
]


def cleanup_project():
    """Main cleanup function"""
    
    print("\n" + "="*60)
    print("🧹 PROJECT CLEANUP - Starting...")
    print("="*60)
    
    deleted_count = 0
    kept_count = 0
    
    # Delete demo files
    print("\n📂 Cleaning up demo files...")
    for pattern in DELETE_FILES:
        for file in PROJECT_ROOT.glob(pattern):
            if file.is_file():
                try:
                    file.unlink()
                    print(f"  ❌ Deleted: {file.name}")
                    deleted_count += 1
                except Exception as e:
                    print(f"  ⚠️ Failed to delete {file.name}: {e}")
    
    # Delete old documentation
    print("\n📄 Cleaning up old documentation...")
    for doc_file in DELETE_DOCS:
        file_path = PROJECT_ROOT / doc_file
        if file_path.exists():
            try:
                file_path.unlink()
                print(f"  ❌ Deleted: {doc_file}")
                deleted_count += 1
            except Exception as e:
                print(f"  ⚠️ Failed to delete {doc_file}: {e}")
    
    # Show kept files
    print("\n✅ Essential files kept:")
    for keep_file in KEEP_FILES:
        file_path = PROJECT_ROOT / keep_file
        if file_path.exists():
            print(f"  ✅ Kept: {keep_file}")
            kept_count += 1
    
    # Summary
    print("\n" + "="*60)
    print("🎉 CLEANUP COMPLETE!")
    print("="*60)
    print(f"  ❌ Deleted: {deleted_count} files")
    print(f"  ✅ Kept: {kept_count} essential files")
    print("\n📁 Clean project structure:")
    print("  • src/ - Core workflow and agent code")
    print("  • tools/ - 113 hospital management tools")
    print("  • api/ - FastAPI backend")
    print("  • frontend/ - React UI")
    print("  • data/ - JSON databases")
    print("="*60)
    
    # Show remaining structure
    print("\n📋 Current file structure:")
    essential_dirs = ["src", "tools", "api", "frontend", "data"]
    for dir_name in essential_dirs:
        dir_path = PROJECT_ROOT / dir_name
        if dir_path.exists() and dir_path.is_dir():
            file_count = len(list(dir_path.rglob("*.py")))
            print(f"  • {dir_name}/ - {file_count} Python files")
    
    print("\n✨ Project is now clean and focused!")
    print("   Next: Update API endpoint and test the chat agent\n")


if __name__ == "__main__":
    cleanup_project()
