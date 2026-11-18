"""
Quick Router Testing Script
============================

This script validates that all new router files are properly structured
without starting the FastAPI server.
"""

import os
import sys
from pathlib import Path

def test_router_structure(router_file):
    """Test if a router file has proper structure"""
    print(f"\n{'='*60}")
    print(f"Testing: {router_file}")
    print('='*60)
    
    file_path = Path(router_file)
    
    if not file_path.exists():
        print(f"❌ File not found: {router_file}")
        return False
    
    with open(file_path, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Check for key components
    checks = {
        "Router import": "from fastapi import APIRouter",
        "Router instance": "router = APIRouter()",
        "Auth imports": "from api.auth import",
        "Pydantic models": "class.*BaseModel",
        "APIResponse model": "class APIResponse",
        "Tool imports": "from tools.",
        "GET endpoints": "@router.get(",
        "POST endpoints": "@router.post(",
        "Error handling": "HTTPException",
        "Try-except blocks": "try:",
        "Status codes": "status_code",
    }
    
    results = {}
    for check_name, pattern in checks.items():
        if pattern in content:
            results[check_name] = "✅"
        else:
            results[check_name] = "❌"
    
    # Count endpoints
    get_count = content.count("@router.get(")
    post_count = content.count("@router.post(")
    put_count = content.count("@router.put(")
    delete_count = content.count("@router.delete(")
    total_endpoints = get_count + post_count + put_count + delete_count
    
    # Count tool initializations
    tool_count = content.count("_tool = ")
    
    # Print results
    print(f"\n📊 Structure Checks:")
    for check, result in results.items():
        print(f"  {result} {check}")
    
    print(f"\n📈 Statistics:")
    print(f"  • Lines of code: {len(content.splitlines())}")
    print(f"  • Total endpoints: {total_endpoints}")
    print(f"    - GET: {get_count}")
    print(f"    - POST: {post_count}")
    print(f"    - PUT: {put_count}")
    print(f"    - DELETE: {delete_count}")
    print(f"  • Tools initialized: {tool_count}")
    
    # Overall status
    passed = sum(1 for r in results.values() if r == "✅")
    total = len(results)
    percentage = (passed / total) * 100
    
    print(f"\n🎯 Overall: {passed}/{total} checks passed ({percentage:.0f}%)")
    
    if percentage >= 90:
        print("✅ EXCELLENT - Router is production-ready!")
        return True
    elif percentage >= 70:
        print("⚠️  GOOD - Minor improvements needed")
        return True
    else:
        print("❌ NEEDS WORK - Major issues detected")
        return False

def main():
    """Test all new routers"""
    print("="*60)
    print("🧪 BACKEND ROUTERS TESTING")
    print("="*60)
    
    routers = [
        ("Patients Router", "api/patients_router.py"),
        ("Appointments Router", "api/appointments_router.py"),
        ("Labs Router", "api/labs_router.py"),
        ("Billing Router", "api/billing_router.py"),
        ("Pharmacy Router", "api/pharmacy_router.py"),
        ("Approvals Router", "api/approvals_router.py"),
    ]
    
    results = {}
    
    for name, file_path in routers:
        passed = test_router_structure(file_path)
        results[name] = passed
    
    # Summary
    print("\n" + "="*60)
    print("📋 FINAL SUMMARY")
    print("="*60)
    
    for name, passed in results.items():
        status = "✅ PASS" if passed else "❌ FAIL"
        print(f"{status} - {name}")
    
    total_passed = sum(1 for p in results.values() if p)
    total_routers = len(results)
    
    print("\n" + "="*60)
    print(f"🎯 Overall Results: {total_passed}/{total_routers} routers passed")
    print("="*60)
    
    if total_passed == total_routers:
        print("\n🎉 SUCCESS! All routers are properly structured!")
        print("\n📌 Next Steps:")
        print("  1. Start FastAPI server: python main.py")
        print("  2. Open Swagger UI: http://localhost:8000/docs")
        print("  3. Test endpoints with different user roles")
        print("  4. Verify authentication and authorization")
        return 0
    else:
        print(f"\n⚠️  WARNING: {total_routers - total_passed} router(s) need attention")
        return 1

if __name__ == "__main__":
    sys.exit(main())
