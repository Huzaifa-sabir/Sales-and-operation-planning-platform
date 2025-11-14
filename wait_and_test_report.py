import time
import requests
import json
from datetime import datetime, timedelta

print("=" * 80)
print("WAITING FOR RENDER DEPLOYMENT AND TESTING REPORT GENERATION")
print("=" * 80)

# Wait 4 minutes for deployment
wait_time = 240  # 4 minutes in seconds
print(f"\n[*] Waiting {wait_time} seconds (4 minutes) for Render to deploy...")
for i in range(wait_time // 10):
    time.sleep(10)
    remaining = wait_time - (i + 1) * 10
    print(f"   {remaining} seconds remaining...")

print("\n[OK] Wait complete! Starting tests...\n")

# Configuration
BASE_URL = "https://sop-portal-backend.onrender.com/api/v1"
ADMIN_EMAIL = "admin@heavygarlic.com"
ADMIN_PASSWORD = "admin123"

# Step 1: Login
print("=" * 80)
print("STEP 1: LOGIN")
print("=" * 80)
login_url = f"{BASE_URL}/auth/login"
login_payload = {"email": ADMIN_EMAIL, "password": ADMIN_PASSWORD}

print(f"POST {login_url}")
print(f"Payload: {json.dumps(login_payload, indent=2)}")

try:
    response = requests.post(login_url, json=login_payload)
    print(f"Status: {response.status_code}")

    if response.status_code == 200:
        login_data = response.json()
        token = login_data.get("accessToken")
        print("[OK] Login successful!")
        print(f"Token: {token[:50]}...")
    else:
        print(f"[FAIL] Login failed: {response.text}")
        exit(1)
except Exception as e:
    print(f"[FAIL] Login error: {e}")
    exit(1)

# Set up headers with token
headers = {
    "Authorization": f"Bearer {token}",
    "Content-Type": "application/json"
}

# Step 2: Generate report without date filters (all data)
print("\n" + "=" * 80)
print("STEP 2: GENERATE REPORT - ALL DATA (NO FILTERS)")
print("=" * 80)
report_url = f"{BASE_URL}/reports/generate-instant"
report_payload = {
    "reportType": "sales_summary",
    "format": "excel"
}

print(f"POST {report_url}")
print(f"Payload: {json.dumps(report_payload, indent=2)}")

try:
    response = requests.post(report_url, json=report_payload, headers=headers)
    print(f"Status: {response.status_code}")

    if response.status_code == 200:
        filename = "test_all_data_after_fix.xlsx"
        with open(filename, 'wb') as f:
            f.write(response.content)
        print(f"[OK] Report generated successfully!")
        print(f"File saved: {filename}")
        print(f"File size: {len(response.content)} bytes")
    else:
        print(f"[FAIL] Report generation failed: {response.text}")
except Exception as e:
    print(f"[FAIL] Report generation error: {e}")

# Step 3: Generate report with year/month filters
print("\n" + "=" * 80)
print("STEP 3: GENERATE REPORT - WITH YEAR/MONTH FILTERS (November 2025)")
print("=" * 80)
report_payload = {
    "reportType": "sales_summary",
    "format": "excel",
    "year": 2025,
    "month": 11
}

print(f"POST {report_url}")
print(f"Payload: {json.dumps(report_payload, indent=2)}")

try:
    response = requests.post(report_url, json=report_payload, headers=headers)
    print(f"Status: {response.status_code}")

    if response.status_code == 200:
        filename = "test_november_2025_after_fix.xlsx"
        with open(filename, 'wb') as f:
            f.write(response.content)
        print(f"[OK] Report generated successfully!")
        print(f"File saved: {filename}")
        print(f"File size: {len(response.content)} bytes")
    else:
        print(f"[FAIL] Report generation failed: {response.text}")
except Exception as e:
    print(f"[FAIL] Report generation error: {e}")

# Step 4: Generate report with date range filters (should trigger the 'str' error before fix)
print("\n" + "=" * 80)
print("STEP 4: GENERATE REPORT - WITH DATE RANGE FILTERS")
print("=" * 80)

# Date range from April 2025 to October 2025
start_date = datetime.now() - timedelta(days=180)
end_date = datetime.now()

report_payload = {
    "reportType": "sales_summary",
    "format": "excel",
    "startDate": start_date.isoformat() + "Z",
    "endDate": end_date.isoformat() + "Z"
}

print(f"POST {report_url}")
print(f"Payload: {json.dumps(report_payload, indent=2)}")

try:
    response = requests.post(report_url, json=report_payload, headers=headers)
    print(f"Status: {response.status_code}")

    if response.status_code == 200:
        filename = "test_date_range_after_fix.xlsx"
        with open(filename, 'wb') as f:
            f.write(response.content)
        print(f"[OK] Report generated successfully! (This would have failed before the fix)")
        print(f"File saved: {filename}")
        print(f"File size: {len(response.content)} bytes")
    else:
        print(f"[FAIL] Report generation failed: {response.text}")
except Exception as e:
    print(f"[FAIL] Report generation error: {e}")

print("\n" + "=" * 80)
print("TEST COMPLETE")
print("=" * 80)
print("\n[OK] All tests completed!")
print("\nNOTE: Reports will show $0.00 because MongoDB Atlas has no sales data.")
print("The important thing is that the 'str' object error should be GONE!")
print("\nYou can check the generated Excel files to verify they downloaded successfully.")
