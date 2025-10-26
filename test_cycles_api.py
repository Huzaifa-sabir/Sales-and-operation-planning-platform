"""
Test the cycles API to see what data format it returns
"""
import requests
import json

BASE_URL = "https://sales-and-operation-planning-platform-1.onrender.com/api/v1"

print("=" * 80)
print("TESTING CYCLES API RESPONSE FORMAT")
print("=" * 80)

# First, login as admin to get token
print("\n1. Logging in as admin...")
admin_response = requests.post(
    f"{BASE_URL}/auth/login",
    json={"email": "admin@heavygarlic.com", "password": "admin123"},
    headers={"Content-Type": "application/json"}
)

if admin_response.status_code != 200:
    print(f"   [X] Admin login failed: {admin_response.status_code}")
    print(f"   Response: {admin_response.text}")
    exit(1)

admin_data = admin_response.json()
admin_token = admin_data.get("access_token")
print(f"   [OK] Admin logged in successfully")

# Test cycles API
print("\n2. Testing cycles API...")
cycles_response = requests.get(
    f"{BASE_URL}/sop/cycles?limit=100",
    headers={
        "Authorization": f"Bearer {admin_token}",
        "Accept": "application/json"
    }
)

print(f"   Cycles API status: {cycles_response.status_code}")
print(f"   Response headers: {dict(cycles_response.headers)}")

if cycles_response.status_code == 200:
    cycles_data = cycles_response.json()
    print(f"\n   [OK] Cycles API response received")
    print(f"   Response structure: {type(cycles_data)}")
    print(f"   Response keys: {list(cycles_data.keys()) if isinstance(cycles_data, dict) else 'Not a dict'}")
    
    # Check if it has the expected structure
    if isinstance(cycles_data, dict):
        print(f"\n   Data structure analysis:")
        for key, value in cycles_data.items():
            print(f"   - {key}: {type(value)} (length: {len(value) if hasattr(value, '__len__') else 'N/A'})")
            if key == 'data' and isinstance(value, list) and len(value) > 0:
                print(f"     First item keys: {list(value[0].keys()) if isinstance(value[0], dict) else 'Not a dict'}")
    
    print(f"\n   Full response:")
    print(json.dumps(cycles_data, indent=2, default=str))
    
else:
    print(f"   [X] Cycles API failed: {cycles_response.status_code}")
    print(f"   Error: {cycles_response.text}")

print("\n" + "=" * 80)
print("CYCLES API TEST COMPLETE")
print("=" * 80)
