"""
Quick Import Test - Check if all routers can be imported
"""

import sys

def test_router_import(module_path, router_name):
    """Test if a router can be imported"""
    try:
        print(f"Testing {router_name}...", end=" ")
        exec(f"from {module_path} import router")
        print("✅ SUCCESS")
        return True
    except Exception as e:
        print(f"❌ FAILED: {str(e)[:100]}")
        return False

def main():
    print("="*60)
    print("🧪 ROUTER IMPORT TESTING")
    print("="*60 + "\n")
    
    routers = [
        ("api.patients_router", "Patients Router"),
        ("api.appointments_router", "Appointments Router"),
        ("api.labs_router", "Labs Router"),
        ("api.billing_router", "Billing Router"),
        ("api.pharmacy_router", "Pharmacy Router"),
        ("api.approvals_router", "Approvals Router"),
    ]
    
    results = []
    
    for module_path, name in routers:
        passed = test_router_import(module_path, name)
        results.append((name, passed))
    
    print("\n" + "="*60)
    print("📋 SUMMARY")
    print("="*60)
    
    passed_count = sum(1 for _, p in results if p)
    total_count = len(results)
    
    for name, passed in results:
        status = "✅" if passed else "❌"
        print(f"{status} {name}")
    
    print(f"\n🎯 Result: {passed_count}/{total_count} routers can be imported")
    
    if passed_count == total_count:
        print("\n✅ All routers ready for server startup!")
        return 0
    else:
        print(f"\n❌ {total_count - passed_count} router(s) have import errors")
        return 1

if __name__ == "__main__":
    sys.exit(main())
