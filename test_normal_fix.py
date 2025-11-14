"""
Test after Normal style fix
"""
import requests
import time

BASE_URL = "https://sales-and-operation-planning-platform-1.onrender.com/api/v1"

print("=" * 80)
print("TESTING AFTER NORMAL STYLE FIX")
print("Waiting 4 minutes for deployment...")
print("=" * 80)

time.sleep(240)

print("\n1. Logging in as admin...")
try:
    admin_response = requests.post(
        f"{BASE_URL}/auth/login",
        json={"email": "admin@heavygarlic.com", "password": "admin123"},
        headers={"Content-Type": "application/json"}
    )
    
    admin_data = admin_response.json()
    admin_token = admin_data.get("access_token")
    print(f"   [OK] Admin logged in successfully")
    
    # Test the exact scenario from the logs
    print(f"\n2. Testing date range filtering (Dec 2024 - Jan 2025)...")
    excel_response = requests.post(
        f"{BASE_URL}/reports/generate-instant",
        json={
            "reportType": "sales_summary",
            "format": "excel",
            "startDate": "2024-12-10",
            "endDate": "2025-01-30",
            "includeCharts": False,
            "includeRawData": True
        },
        headers={
            "Authorization": f"Bearer {admin_token}",
            "Content-Type": "application/json"
        },
        timeout=60
    )
    
    print(f"   Status: {excel_response.status_code}")
    if excel_response.status_code == 200:
        print(f"   ✅ SUCCESS! Report generated successfully")
        print(f"   File size: {len(excel_response.content)} bytes")
    else:
        print(f"   ❌ FAILED: {excel_response.text[:300]}")
        
except Exception as e:
    print(f"   [ERROR] Test failed: {e}")

print(f"\n" + "=" * 80)

