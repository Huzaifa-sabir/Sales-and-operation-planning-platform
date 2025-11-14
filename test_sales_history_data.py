"""
Test sales history API to verify data is correct
"""
import requests

BASE_URL = "https://sales-and-operation-planning-platform-1.onrender.com/api/v1"

print("=" * 80)
print("TESTING SALES HISTORY API TO VERIFY DATA")
print("=" * 80)

# Login as admin
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
    
    # Test sales statistics for November 2024
    print(f"\n2. Checking sales statistics for November 2024...")
    stats_response = requests.get(
        f"{BASE_URL}/sales-history/statistics?year=2024&month=11",
        headers={"Authorization": f"Bearer {admin_token}"}
    )
    
    if stats_response.status_code == 200:
        stats_data = stats_response.json()
        print(f"   Status: {stats_response.status_code}")
        print(f"   Total Revenue: ${stats_data.get('totalRevenue', 0):,.2f}")
        print(f"   Total Quantity: {stats_data.get('totalQuantity', 0):,.2f}")
        print(f"   Record Count: {stats_data.get('recordCount', 0)}")
        print(f"   Avg Quantity: {stats_data.get('avgQuantity', 0):,.2f}")
        print(f"   Avg Unit Price: ${stats_data.get('avgUnitPrice', 0):,.2f}")
    
    # Test sales history records for November 2024
    print(f"\n3. Checking sales history records for November 2024...")
    history_response = requests.get(
        f"{BASE_URL}/sales-history?year=2024&month=11&limit=10",
        headers={"Authorization": f"Bearer {admin_token}"}
    )
    
    if history_response.status_code == 200:
        history_data = history_response.json()
        print(f"   Status: {history_response.status_code}")
        print(f"   Total records: {history_data.get('total', 0)}")
        print(f"   Records returned: {len(history_data.get('records', []))}")
        
        if history_data.get('records'):
            print(f"\n   Sample records:")
            for i, record in enumerate(history_data['records'][:3], 1):
                print(f"\n   Record {i}:")
                print(f"     Customer: {record.get('customerName', 'N/A')}")
                print(f"     Product: {record.get('productDescription', 'N/A')}")
                print(f"     Quantity: {record.get('quantity', 0):.2f}")
                print(f"     Total Sales: ${record.get('totalSales', 0):,.2f}")
                print(f"     Year-Month: {record.get('yearMonth', 'N/A')}")
        
except Exception as e:
    print(f"   [ERROR] Test failed: {e}")

print(f"\n" + "=" * 80)
print("SALES HISTORY API TEST COMPLETE")
print("=" * 80)

print(f"\n🔍 ANALYSIS:")
print(f"If sales statistics show $1,004,189.55 but reports show $0.00,")
print(f"then there's a mismatch between report generation and statistics API.")
print(f"The report service may be using different query logic.")

