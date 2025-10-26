"""
Test the deployed backend after fixes
"""
import requests
import time

BASE_URL = "https://sales-and-operation-planning-platform-1.onrender.com/api/v1"

print("=" * 80)
print("TESTING DEPLOYED BACKEND AFTER FIXES")
print("=" * 80)

# Wait for deployment to complete
print("\n1. Waiting for deployment to complete...")
time.sleep(30)  # Wait 30 seconds for deployment

# Login as admin
print("\n2. Logging in as admin...")
try:
    admin_response = requests.post(
        f"{BASE_URL}/auth/login",
        json={"email": "admin@heavygarlic.com", "password": "admin123"},
        headers={"Content-Type": "application/json"}
    )
    
    admin_data = admin_response.json()
    admin_token = admin_data.get("access_token")
    print(f"   [OK] Admin logged in successfully")
    
    # Test sales statistics with November 2024 filter
    print(f"\n3. Testing sales statistics with November 2024 filter...")
    stats_response = requests.get(
        f"{BASE_URL}/sales-history/statistics?year=2024&month=11",
        headers={"Authorization": f"Bearer {admin_token}"}
    )
    
    print(f"   Stats status: {stats_response.status_code}")
    if stats_response.status_code == 200:
        stats_data = stats_response.json()
        print(f"   November 2024 Stats:")
        print(f"     Total Quantity: {stats_data.get('totalQuantity', 0)}")
        print(f"     Total Revenue: ${stats_data.get('totalRevenue', 0):.2f}")
        print(f"     Record Count: {stats_data.get('recordCount', 0)}")
        print(f"     Avg Quantity: {stats_data.get('avgQuantity', 0):.2f}")
        print(f"     Avg Unit Price: ${stats_data.get('avgUnitPrice', 0):.2f}")
        
        # Check if the values are correct
        expected_revenue = 1004189.55
        expected_quantity = 3920
        expected_count = 7
        
        if abs(stats_data.get('totalRevenue', 0) - expected_revenue) < 1:
            print(f"   ✅ Revenue is correct!")
        else:
            print(f"   ❌ Revenue is wrong! Expected: ${expected_revenue:.2f}, Got: ${stats_data.get('totalRevenue', 0):.2f}")
            
        if abs(stats_data.get('totalQuantity', 0) - expected_quantity) < 1:
            print(f"   ✅ Quantity is correct!")
        else:
            print(f"   ❌ Quantity is wrong! Expected: {expected_quantity}, Got: {stats_data.get('totalQuantity', 0)}")
            
        if stats_data.get('recordCount', 0) == expected_count:
            print(f"   ✅ Record count is correct!")
        else:
            print(f"   ❌ Record count is wrong! Expected: {expected_count}, Got: {stats_data.get('recordCount', 0)}")
    else:
        print(f"   [ERROR] Stats request failed: {stats_response.text[:200]}")
    
    # Test report generation
    print(f"\n4. Testing report generation...")
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
    
    if instant_response.status_code == 200:
        if 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet' in instant_response.headers.get('content-type', ''):
            print(f"   [SUCCESS] Received Excel file")
            # Save the file
            filename = "november_2024_report_deployed.xlsx"
            with open(filename, 'wb') as f:
                f.write(instant_response.content)
            print(f"   [OK] Saved as: {filename}")
            
            # Quick analysis
            try:
                import pandas as pd
                df = pd.read_excel(filename, sheet_name='Summary')
                print(f"   Report analysis:")
                print(f"     Rows: {len(df)}")
                
                # Look for revenue values
                for i, row in df.iterrows():
                    if 'Total Revenue' in str(row.iloc[0]):
                        revenue_value = str(row.iloc[1])
                        print(f"     Total Revenue in report: {revenue_value}")
                        if '$0.00' not in revenue_value:
                            print(f"   ✅ Report shows non-zero revenue!")
                        else:
                            print(f"   ❌ Report still shows $0.00 revenue!")
                        break
                        
            except Exception as e:
                print(f"   [ERROR] Could not analyze report: {e}")
        else:
            print(f"   [WARNING] Unexpected content type")
    else:
        print(f"   [ERROR] Report generation failed: {instant_response.text[:200]}")
        
except Exception as e:
    print(f"   [ERROR] Test failed: {e}")

print(f"\n" + "=" * 80)
print("DEPLOYED BACKEND TEST COMPLETE")
print("=" * 80)
