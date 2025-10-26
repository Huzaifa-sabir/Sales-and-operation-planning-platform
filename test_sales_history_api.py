"""
Test the sales history API endpoint to find why it's not returning data
"""
import requests
import json

BASE_URL = "https://sales-and-operation-planning-platform-1.onrender.com/api/v1"

print("=" * 80)
print("INVESTIGATING SALES HISTORY API ENDPOINT ISSUE")
print("=" * 80)

# Login as admin
print("\n1. Logging in as admin...")
admin_response = requests.post(
    f"{BASE_URL}/auth/login",
    json={"email": "admin@heavygarlic.com", "password": "admin123"},
    headers={"Content-Type": "application/json"}
)

admin_data = admin_response.json()
admin_token = admin_data.get("access_token")
print(f"   [OK] Admin logged in successfully")

# Test different sales history API calls
test_cases = [
    {
        "name": "Sales history without filters",
        "url": f"{BASE_URL}/sales-history"
    },
    {
        "name": "Sales history with date range",
        "url": f"{BASE_URL}/sales-history?start_date=2024-11-01&end_date=2024-11-30"
    },
    {
        "name": "Sales history with year/month",
        "url": f"{BASE_URL}/sales-history?year=2024&month=11"
    },
    {
        "name": "Sales history with pagination",
        "url": f"{BASE_URL}/sales-history?page=1&limit=10"
    },
    {
        "name": "Sales history with year only",
        "url": f"{BASE_URL}/sales-history?year=2024"
    }
]

for test_case in test_cases:
    print(f"\n2. Testing: {test_case['name']}")
    try:
        response = requests.get(
            test_case['url'],
            headers={"Authorization": f"Bearer {admin_token}"}
        )
        
        print(f"   Status: {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            print(f"   Response structure: {type(data)}")
            print(f"   Keys: {list(data.keys()) if isinstance(data, dict) else 'Not a dict'}")
            
            if isinstance(data, dict):
                total = data.get('total', 0)
                data_list = data.get('data', [])
                print(f"   Total records: {total}")
                print(f"   Data array length: {len(data_list)}")
                
                if len(data_list) > 0:
                    print(f"   Sample record:")
                    sample = data_list[0]
                    print(f"     Customer: {sample.get('customerName', 'N/A')}")
                    print(f"     Product: {sample.get('productDescription', 'N/A')}")
                    print(f"     Year-Month: {sample.get('yearMonth', 'N/A')}")
                    print(f"     Quantity: {sample.get('quantity', 0)}")
                    print(f"     Total Sales: ${sample.get('totalSales', 0):.2f}")
                else:
                    print(f"   [WARNING] No data in response!")
            else:
                print(f"   [WARNING] Response is not a dict: {data}")
        else:
            print(f"   [ERROR] Request failed: {response.text[:200]}")
            
    except Exception as e:
        print(f"   [ERROR] Test failed: {e}")

# Test the reports endpoint directly
print(f"\n3. Testing reports endpoint...")
try:
    reports_response = requests.get(
        f"{BASE_URL}/reports",
        headers={"Authorization": f"Bearer {admin_token}"}
    )
    
    print(f"   Reports status: {reports_response.status_code}")
    if reports_response.status_code == 200:
        reports_data = reports_response.json()
        print(f"   Reports response: {reports_data}")
    else:
        print(f"   Reports error: {reports_response.text[:200]}")
        
except Exception as e:
    print(f"   [ERROR] Reports test failed: {e}")

# Test instant report generation
print(f"\n4. Testing instant report generation...")
try:
    instant_response = requests.post(
        f"{BASE_URL}/reports/generate-instant",
        json={
            "reportType": "sales_summary",
            "format": "excel",
            "startDate": "2024-11-01",
            "endDate": "2024-11-30",
            "includeCharts": True,
            "includeRawData": True
        },
        headers={
            "Authorization": f"Bearer {admin_token}",
            "Content-Type": "application/json"
        },
        timeout=60
    )
    
    print(f"   Instant report status: {instant_response.status_code}")
    print(f"   Content-Type: {instant_response.headers.get('content-type', 'N/A')}")
    
    if instant_response.status_code == 200:
        if 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet' in instant_response.headers.get('content-type', ''):
            print(f"   [SUCCESS] Received Excel file")
            # Save the file
            with open("november_2024_report.xlsx", 'wb') as f:
                f.write(instant_response.content)
            print(f"   [OK] Saved as: november_2024_report.xlsx")
            
            # Try to read the Excel file
            try:
                import pandas as pd
                df = pd.read_excel("november_2024_report.xlsx")
                print(f"   Excel contents:")
                print(f"     Rows: {len(df)}")
                print(f"     Columns: {list(df.columns)}")
                if len(df) > 0:
                    print(f"     First few rows:")
                    print(df.head().to_string())
                else:
                    print(f"     [WARNING] Excel file is empty!")
            except Exception as e:
                print(f"   [ERROR] Could not read Excel: {e}")
        else:
            print(f"   [WARNING] Unexpected content type")
            print(f"   Response: {instant_response.text[:500]}")
    else:
        print(f"   [ERROR] Instant report failed: {instant_response.text[:500]}")
        
except Exception as e:
    print(f"   [ERROR] Instant report test failed: {e}")

print(f"\n" + "=" * 80)
print("INVESTIGATION COMPLETE")
print("=" * 80)
