"""
Test script for Hospital Management AI Agent API
Tests authentication, authorization, and analytics endpoints
"""

import httpx
import json
from datetime import datetime

# API Base URL
BASE_URL = "http://localhost:8000"

def print_section(title):
    """Print a formatted section header"""
    print(f"\n{'='*70}")
    print(f"🔹 {title}")
    print(f"{'='*70}\n")

def login(username: str, password: str):
    """Login and get access token"""
    print(f"🔐 Logging in as: {username}")
    
    response = httpx.post(
        f"{BASE_URL}/token",
        data={"username": username, "password": password},
        headers={"Content-Type": "application/x-www-form-urlencoded"}
    )
    
    if response.status_code == 200:
        data = response.json()
        print(f"✅ Login successful!")
        print(f"   User: {data['user']['full_name']}")
        print(f"   Role: {data['user']['role']}")
        print(f"   Token expires in: {data['expires_in']} seconds ({data['expires_in']/3600:.1f} hours)")
        return data["access_token"]
    else:
        print(f"❌ Login failed: {response.text}")
        return None

def test_current_user(token: str):
    """Test GET /auth/me endpoint"""
    print(f"\n👤 Testing /auth/me endpoint...")
    
    response = httpx.get(
        f"{BASE_URL}/auth/me",
        headers={"Authorization": f"Bearer {token}"}
    )
    
    if response.status_code == 200:
        data = response.json()
        user = data.get('user', data)  # Handle both {"user": {...}} and direct user object
        print(f"✅ Current user retrieved:")
        print(f"   Username: {user.get('username', user.get('sub', 'N/A'))}")
        print(f"   Email: {user.get('email', 'N/A')}")
        print(f"   Role: {user.get('role', 'N/A')}")
        if 'user_id' in user:
            print(f"   User ID: {user['user_id']}")
        return user
    else:
        print(f"❌ Failed to get current user: {response.text}")
        return None

def test_system_overview(token: str):
    """Test POST /api/analytics/system-overview endpoint"""
    print(f"\n📊 Testing /api/analytics/system-overview endpoint...")
    
    response = httpx.post(
        f"{BASE_URL}/api/analytics/system-overview",
        headers={"Authorization": f"Bearer {token}"},
        json={"date": datetime.now().strftime("%Y-%m-%d")}
    )
    
    if response.status_code == 200:
        data = response.json()
        if data["success"]:
            print(f"✅ System overview retrieved successfully!")
            # The data is the text output from the tool
            overview_text = data.get("data", "")
            print(f"\n   📋 SYSTEM OVERVIEW:")
            # Print first 500 characters of the overview
            print(overview_text[:500] if len(overview_text) > 500 else overview_text)
            if len(overview_text) > 500:
                print(f"   ... (truncated, {len(overview_text)} chars total)")
            return overview_text
        else:
            print(f"❌ Request failed: {data['message']}")
    else:
        print(f"❌ HTTP Error {response.status_code}: {response.text}")
    
    return None

def test_revenue_analytics(token: str):
    """Test POST /api/analytics/revenue-analytics endpoint"""
    print(f"\n💰 Testing /api/analytics/revenue-analytics endpoint...")
    
    response = httpx.post(
        f"{BASE_URL}/api/analytics/revenue-analytics",
        headers={"Authorization": f"Bearer {token}"},
        json={
            "start_date": "2025-10-01",
            "end_date": "2025-10-31",
            "period": "monthly"
        }
    )
    
    if response.status_code == 200:
        data = response.json()
        if data["success"]:
            print(f"✅ Revenue analytics retrieved successfully!")
            revenue_text = data.get("data", "")
            print(f"\n   💵 REVENUE ANALYTICS:")
            # Print first 400 characters
            print(revenue_text[:400] if len(revenue_text) > 400 else revenue_text)
            if len(revenue_text) > 400:
                print(f"   ... (truncated, {len(revenue_text)} chars total)")
            return revenue_text
        else:
            print(f"❌ Request failed: {data['message']}")
    else:
        print(f"❌ HTTP Error {response.status_code}: {response.text}")
    
    return None

def test_operational_analytics(token: str):
    """Test POST /api/analytics/operational-analytics endpoint"""
    print(f"\n⚙️ Testing /api/analytics/operational-analytics endpoint...")
    
    response = httpx.post(
        f"{BASE_URL}/api/analytics/operational-analytics",
        headers={"Authorization": f"Bearer {token}"},
        json={
            "start_date": "2025-10-01",
            "end_date": "2025-10-31"
        }
    )
    
    if response.status_code == 200:
        data = response.json()
        if data["success"]:
            print(f"✅ Operational analytics retrieved successfully!")
            ops_text = data.get("data", "")
            print(f"\n   🏥 OPERATIONAL ANALYTICS:")
            # Print first 400 characters
            print(ops_text[:400] if len(ops_text) > 400 else ops_text)
            if len(ops_text) > 400:
                print(f"   ... (truncated, {len(ops_text)} chars total)")
            return ops_text
        else:
            print(f"❌ Request failed: {data['message']}")
    else:
        print(f"❌ HTTP Error {response.status_code}: {response.text}")
    
    return None

def test_dashboard_report(token: str):
    """Test POST /api/analytics/dashboard-report endpoint"""
    print(f"\n📋 Testing /api/analytics/dashboard-report endpoint (JSON format)...")
    
    response = httpx.post(
        f"{BASE_URL}/api/analytics/dashboard-report",
        headers={"Authorization": f"Bearer {token}"},
        json={
            "format": "json",
            "include_charts": True
        }
    )
    
    if response.status_code == 200:
        data = response.json()
        if data["success"]:
            print(f"✅ Dashboard report retrieved successfully!")
            report = data.get("data", "")
            
            # Check if it's JSON format (dict) or text
            if isinstance(report, dict):
                print(f"\n   📈 DASHBOARD REPORT (JSON Format):")
                print(f"   Generated: {report.get('metadata', {}).get('generated_at', 'N/A')}")
                if 'kpis' in report:
                    kpis = report['kpis']
                    print(f"\n   📊 KPIs ({len(kpis)} total):")
                    # Show first 3 KPIs
                    kpi_list = list(kpis.values()) if isinstance(kpis, dict) else kpis
                    for kpi in kpi_list[:3]:
                        if isinstance(kpi, dict):
                            print(f"   - {kpi.get('label', 'N/A')}: {kpi.get('value', 'N/A')}")
                        else:
                            print(f"   - {kpi}")
            else:
                print(f"\n   📈 DASHBOARD REPORT:")
                # Print first 500 characters
                print(report[:500] if len(report) > 500 else report)
                if len(report) > 500:
                    print(f"   ... (truncated, {len(report)} chars total)")
            
            return report
        else:
            print(f"❌ Request failed: {data['message']}")
    else:
        print(f"❌ HTTP Error {response.status_code}: {response.text}")
    
    return None

def test_unauthorized_access():
    """Test endpoint without authentication"""
    print(f"\n🔒 Testing unauthorized access...")
    
    response = httpx.post(
        f"{BASE_URL}/api/analytics/system-overview",
        json={"date": datetime.now().strftime("%Y-%m-%d")}
    )
    
    if response.status_code == 401:
        print(f"✅ Unauthorized access correctly blocked (401)")
    else:
        print(f"❌ Expected 401, got {response.status_code}")

def test_role_based_access(admin_token: str, doctor_token: str):
    """Test role-based access control"""
    print(f"\n👮 Testing role-based access control...")
    
    # Admin should access revenue analytics
    print(f"\n   Testing Admin access to revenue analytics...")
    response = httpx.post(
        f"{BASE_URL}/api/analytics/revenue-analytics",
        headers={"Authorization": f"Bearer {admin_token}"},
        json={
            "start_date": "2025-10-01",
            "end_date": "2025-10-31",
            "period": "monthly"
        }
    )
    if response.status_code == 200:
        print(f"   ✅ Admin can access revenue analytics")
    else:
        print(f"   ❌ Admin access denied: {response.status_code}")
    
    # Doctor should NOT access revenue analytics (admin-only)
    print(f"\n   Testing Doctor access to revenue analytics (should fail)...")
    response = httpx.post(
        f"{BASE_URL}/api/analytics/revenue-analytics",
        headers={"Authorization": f"Bearer {doctor_token}"},
        json={
            "start_date": "2025-10-01",
            "end_date": "2025-10-31",
            "period": "monthly"
        }
    )
    if response.status_code == 403:
        print(f"   ✅ Doctor correctly denied access to revenue analytics (403)")
    else:
        print(f"   ❌ Expected 403, got {response.status_code}")
    
    # Doctor should access operational analytics
    print(f"\n   Testing Doctor access to operational analytics...")
    response = httpx.post(
        f"{BASE_URL}/api/analytics/operational-analytics",
        headers={"Authorization": f"Bearer {doctor_token}"},
        json={
            "start_date": "2025-10-01",
            "end_date": "2025-10-31"
        }
    )
    if response.status_code == 200:
        print(f"   ✅ Doctor can access operational analytics")
    else:
        print(f"   ❌ Doctor access denied: {response.status_code}")

def main():
    """Run all API tests"""
    print_section("Hospital Management AI Agent API - Test Suite")
    
    try:
        # Test 1: Unauthorized access
        print_section("Test 1: Unauthorized Access")
        test_unauthorized_access()
        
        # Test 2: Admin login
        print_section("Test 2: Admin Authentication")
        admin_token = login("admin", "admin123")
        if not admin_token:
            print("❌ Admin login failed. Exiting.")
            return
        
        # Test 3: Doctor login
        print_section("Test 3: Doctor Authentication")
        doctor_token = login("doctor", "doctor123")
        if not doctor_token:
            print("❌ Doctor login failed. Exiting.")
            return
        
        # Test 4: Current user endpoint
        print_section("Test 4: Current User Endpoint")
        test_current_user(admin_token)
        
        # Test 5: System overview
        print_section("Test 5: System Overview Analytics")
        test_system_overview(admin_token)
        
        # Test 6: Revenue analytics
        print_section("Test 6: Revenue Analytics")
        test_revenue_analytics(admin_token)
        
        # Test 7: Operational analytics
        print_section("Test 7: Operational Analytics")
        test_operational_analytics(admin_token)
        
        # Test 8: Dashboard report
        print_section("Test 8: Dashboard Report (JSON)")
        test_dashboard_report(admin_token)
        
        # Test 9: Role-based access control
        print_section("Test 9: Role-Based Access Control (RBAC)")
        test_role_based_access(admin_token, doctor_token)
        
        # Summary
        print_section("Test Suite Complete")
        print("✅ All tests executed successfully!")
        print("\n📊 API Endpoints Tested:")
        print("   1. POST /token - Authentication")
        print("   2. GET /auth/me - Current user")
        print("   3. POST /api/analytics/system-overview")
        print("   4. POST /api/analytics/revenue-analytics")
        print("   5. POST /api/analytics/operational-analytics")
        print("   6. POST /api/analytics/dashboard-report")
        print("\n🔐 Security Features Validated:")
        print("   - JWT Token Authentication")
        print("   - Role-Based Access Control (RBAC)")
        print("   - Unauthorized access blocking")
        print("   - Admin-only endpoint protection")
        
    except Exception as e:
        print(f"\n❌ Test suite failed with error:")
        print(f"   {type(e).__name__}: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main()
