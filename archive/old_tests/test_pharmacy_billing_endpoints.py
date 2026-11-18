"""
Test script for new pharmacy and billing endpoints
Tests the GET /api/pharmacy/patient/{patient_id}/prescriptions endpoint
Tests the GET /api/billing/patient/{patient_id}/invoices endpoint
"""

import requests
import json

BASE_URL = "http://localhost:8000"

# Login to get auth token
print("=" * 60)
print("1. Logging in as patient...")
print("=" * 60)

login_data = {
    "username": "patient",
    "password": "patient123"
}

response = requests.post(f"{BASE_URL}/token", data=login_data)
if response.status_code == 200:
    token_data = response.json()
    access_token = token_data["access_token"]
    print(f"✅ Login successful!")
    print(f"Token: {access_token[:50]}...")
else:
    print(f"❌ Login failed: {response.status_code}")
    print(response.text)
    exit(1)

headers = {
    "Authorization": f"Bearer {access_token}"
}

# Test pharmacy endpoint
print("\n" + "=" * 60)
print("2. Testing GET /api/pharmacy/patient/patient001/prescriptions")
print("=" * 60)

response = requests.get(
    f"{BASE_URL}/api/pharmacy/patient/patient001/prescriptions",
    headers=headers
)

print(f"Status Code: {response.status_code}")

if response.status_code == 200:
    data = response.json()
    print(f"✅ Success!")
    print(f"\nResponse structure:")
    print(f"  - success: {data.get('success')}")
    print(f"  - message: {data.get('message')}")
    print(f"  - data keys: {list(data.get('data', {}).keys())}")
    
    prescriptions = data.get('data', {}).get('prescriptions', [])
    print(f"\nPrescriptions found: {len(prescriptions)}")
    
    if prescriptions:
        print("\nFirst prescription:")
        first = prescriptions[0]
        print(f"  - prescription_id: {first.get('prescription_id')}")
        print(f"  - medication_name: {first.get('medication_name')}")
        print(f"  - status: {first.get('status')}")
        print(f"  - dosage: {first.get('dosage')}")
        print(f"  - refills_remaining: {first.get('refills_remaining')}")
    
    print(f"\nFull response:")
    print(json.dumps(data, indent=2))
else:
    print(f"❌ Failed!")
    print(response.text)


# Test billing endpoint
print("\n" + "=" * 60)
print("3. Testing GET /api/billing/patient/patient001/invoices")
print("=" * 60)

response = requests.get(
    f"{BASE_URL}/api/billing/patient/patient001/invoices",
    headers=headers
)

print(f"Status Code: {response.status_code}")

if response.status_code == 200:
    data = response.json()
    print(f"✅ Success!")
    print(f"\nResponse structure:")
    print(f"  - success: {data.get('success')}")
    print(f"  - message: {data.get('message')}")
    print(f"  - data keys: {list(data.get('data', {}).keys())}")
    
    invoices = data.get('data', {}).get('invoices', [])
    total_balance = data.get('data', {}).get('total_balance', 0)
    
    print(f"\nInvoices found: {len(invoices)}")
    print(f"Total balance: ${total_balance:.2f}")
    
    if invoices:
        print("\nFirst invoice:")
        first = invoices[0]
        print(f"  - invoice_id: {first.get('invoice_id')}")
        print(f"  - status: {first.get('status')}")
        print(f"  - total_amount: ${first.get('total_amount', 0):.2f}")
        print(f"  - balance: ${first.get('balance', 0):.2f}")
        print(f"  - items: {len(first.get('items', []))} items")
    
    print(f"\nFull response:")
    print(json.dumps(data, indent=2))
else:
    print(f"❌ Failed!")
    print(response.text)


print("\n" + "=" * 60)
print("Summary:")
print("=" * 60)
print("✅ Both endpoints should return 200 OK")
print("✅ Prescriptions: Should find 3 active prescriptions")
print("✅ Invoices: Should find 2 invoices totaling $530.00")
print("=" * 60)
