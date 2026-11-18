"""
Test Lab Results Reader Tool
Tests reading lab results from Google Sheets

Usage:
    1. First run: python scripts/create_lab_results_sheet.py
    2. Add LAB_RESULTS_SHEET_ID to .env
    3. Then run: python test_lab_results_reader.py
"""

import os
import sys
from dotenv import load_dotenv

sys.path.append(os.path.dirname(os.path.abspath(__file__)))

load_dotenv()

from tools.lab_results_reader_tool import (
    ReadLabResultsFromSheetTool,
    CheckLabResultStatusTool,
    GetLatestLabResultTool
)

def print_section(title):
    """Print section header"""
    print("\n" + "=" * 70)
    print(f"  {title}")
    print("=" * 70)

def test_read_lab_results():
    """Test reading lab results"""
    print_section("TEST 1: Read Lab Results from Sheet")
    
    # Check if sheet is configured
    sheet_id = os.getenv('LAB_RESULTS_SHEET_ID')
    if not sheet_id:
        print("❌ LAB_RESULTS_SHEET_ID not found in .env")
        print("   Please run: python scripts/create_lab_results_sheet.py")
        return False
    
    print(f"✅ Sheet ID configured: {sheet_id[:20]}...")
    
    # Test with sample patient
    tool = ReadLabResultsFromSheetTool()
    
    print("\n📋 Testing with sample patient: REG2025SAMPLE")
    result = tool._run("REG2025SAMPLE")
    
    if result['success']:
        print(f"✅ Successfully read results!")
        print(f"   Patient: {result.get('patient_name', 'N/A')}")
        print(f"   Total Tests: {result['total_tests']}")
        print(f"   Completed: {result['completed_count']}")
        print(f"   Pending: {result['pending_count']}")
        
        if result['results']:
            print("\n📊 Test Results:")
            for i, test in enumerate(result['results'], 1):
                print(f"\n   {i}. {test['test_name']}")
                print(f"      Result: {test['result']} {test['unit']}")
                print(f"      Normal Range: {test['normal_range']}")
                print(f"      Status: {test['status']}")
                if test['notes']:
                    print(f"      Notes: {test['notes']}")
        
        return True
    else:
        print(f"❌ Error: {result.get('message', 'Unknown error')}")
        return False

def test_check_status():
    """Test quick status check"""
    print_section("TEST 2: Quick Status Check")
    
    tool = CheckLabResultStatusTool()
    
    print("📋 Checking status for: REG2025SAMPLE")
    result = tool._run("REG2025SAMPLE")
    
    if result['success']:
        print(f"✅ Status: {result['status']}")
        print(f"   {result['message']}")
        print(f"   All Ready: {result['all_ready']}")
        return True
    else:
        print(f"❌ Error: {result.get('message')}")
        return False

def test_latest_result():
    """Test getting latest result"""
    print_section("TEST 3: Get Latest Result")
    
    tool = GetLatestLabResultTool()
    
    print("📋 Getting latest result for: REG2025SAMPLE")
    result = tool._run("REG2025SAMPLE")
    
    if result['success']:
        latest = result['latest_result']
        print(f"✅ Latest Result:")
        print(f"   Test: {latest['test_name']}")
        print(f"   Result: {latest['result']} {latest['unit']}")
        print(f"   Status: {latest['status']}")
        print(f"   Date: {latest['test_date']}")
        return True
    else:
        print(f"❌ Error: {result.get('message')}")
        return False

def test_no_results():
    """Test patient with no results"""
    print_section("TEST 4: Patient with No Results")
    
    tool = ReadLabResultsFromSheetTool()
    
    print("📋 Testing with non-existent patient: REG2025NOTFOUND")
    result = tool._run("REG2025NOTFOUND")
    
    if result['success'] and result['total_tests'] == 0:
        print("✅ Correctly handled patient with no results")
        print(f"   Message: {result['message']}")
        return True
    else:
        print("❌ Unexpected result")
        return False

def main():
    """Run all tests"""
    print("\n" + "🔬" * 35)
    print("LAB RESULTS READER TOOL - TEST SUITE")
    print("🔬" * 35)
    
    tests = [
        ("Read Lab Results", test_read_lab_results),
        ("Quick Status Check", test_check_status),
        ("Latest Result", test_latest_result),
        ("No Results Handling", test_no_results)
    ]
    
    results = []
    for test_name, test_func in tests:
        try:
            passed = test_func()
            results.append((test_name, passed))
        except Exception as e:
            print(f"\n❌ Test '{test_name}' failed with exception: {e}")
            import traceback
            traceback.print_exc()
            results.append((test_name, False))
    
    # Summary
    print_section("TEST SUMMARY")
    
    passed_count = sum(1 for _, passed in results if passed)
    total_count = len(results)
    
    for test_name, passed in results:
        status = "✅ PASSED" if passed else "❌ FAILED"
        print(f"{status} - {test_name}")
    
    print(f"\n{'=' * 70}")
    if passed_count == total_count:
        print(f"🎉 ALL TESTS PASSED! ({passed_count}/{total_count})")
        print("=" * 70)
        print("\n✅ Lab Results Reader Tool is working perfectly!")
        print("\n📋 Next Steps:")
        print("   1. Integrate tool into Stage 6 (Results Analysis)")
        print("   2. Test with real patient flow")
        print("   3. Train staff on filling the sheet")
    else:
        print(f"⚠️ SOME TESTS FAILED ({passed_count}/{total_count} passed)")
        print("=" * 70)
        print("\n🔧 Please check the errors above and:")
        print("   1. Ensure LAB_RESULTS_SHEET_ID is in .env")
        print("   2. Verify Google credentials are valid")
        print("   3. Check sheet has sample data")

if __name__ == "__main__":
    main()
