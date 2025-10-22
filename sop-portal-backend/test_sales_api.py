"""Test sales history API endpoint"""
import requests
import json

# Base URL
BASE_URL = "http://localhost:8000/api/v1"

# Login first
print("1. Logging in...")
login_response = requests.post(
    f"{BASE_URL}/auth/login",
    json={
        "username": "admin",
        "password": "admin123"
    }
)

if login_response.status_code != 200:
    print(f"Login failed: {login_response.status_code}")
    print(login_response.text)
    exit(1)

token = login_response.json()["access_token"]
print(f"   Login successful! Got token")

# Test sales history endpoint
print("\n2. Fetching sales history (page 1, 5 records)...")
headers = {"Authorization": f"Bearer {token}"}
sales_response = requests.get(
    f"{BASE_URL}/sales-history?page=1&pageSize=5",
    headers=headers
)

if sales_response.status_code != 200:
    print(f"Failed: {sales_response.status_code}")
    print(sales_response.text)
    exit(1)

sales_data = sales_response.json()
print(f"   Success! Got {len(sales_data.get('records', []))} records")
print(f"   Total records in DB: {sales_data.get('total', 0)}")

# Show first record
if sales_data.get('records'):
    first_record = sales_data['records'][0]
    print(f"\n   First record:")
    print(f"     Customer: {first_record.get('customerName')}")
    print(f"     Product: {first_record.get('productCode')} - {first_record.get('productDescription')}")
    print(f"     Year-Month: {first_record.get('yearMonth')}")
    print(f"     Quantity: {first_record.get('quantity')}")
    print(f"     Total Sales: ${first_record.get('totalSales'):,.2f}")

# Test statistics endpoint
print("\n3. Fetching sales statistics...")
stats_response = requests.get(
    f"{BASE_URL}/sales-history/statistics",
    headers=headers
)

if stats_response.status_code == 200:
    stats = stats_response.json()
    print(f"   Total Sales: ${stats.get('totalRevenue', 0):,.2f}")
    print(f"   Total Quantity: {stats.get('totalQuantity', 0):,}")
    print(f"   Average Price: ${stats.get('avgUnitPrice', 0):.2f}")
else:
    print(f"   Statistics endpoint returned: {stats_response.status_code}")

# Test monthly data
print("\n4. Fetching monthly sales data...")
monthly_response = requests.get(
    f"{BASE_URL}/sales-history/by-month?months=6",
    headers=headers
)

if monthly_response.status_code == 200:
    monthly_data = monthly_response.json()
    print(f"   Got {len(monthly_data)} months of data")
    if monthly_data:
        print(f"   Latest month: {monthly_data[0].get('yearMonth')} - ${monthly_data[0].get('totalSales', 0):,.2f}")
else:
    print(f"   Monthly endpoint returned: {monthly_response.status_code}")

print("\n✓ All tests completed!")
