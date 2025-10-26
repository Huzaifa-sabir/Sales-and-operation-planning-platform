"""
Test the deployed backend after Render deployment
"""
import requests
import pandas as pd

BASE_URL = "https://sales-and-operation-planning-platform-1.onrender.com/api/v1"

print("=" * 80)
print("TESTING DEPLOYED BACKEND AFTER RENDER DEPLOYMENT")
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
    
    # Test sales statistics with November 2024 filter
    print(f"\n2. Testing sales statistics with November 2024 filter...")
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
        
        print(f"\n   Validation:")
        if abs(stats_data.get('totalRevenue', 0) - expected_revenue) < 1:
            print(f"   ✅ Revenue is correct! ${stats_data.get('totalRevenue', 0):.2f}")
        else:
            print(f"   ❌ Revenue is wrong! Expected: ${expected_revenue:.2f}, Got: ${stats_data.get('totalRevenue', 0):.2f}")
            
        if abs(stats_data.get('totalQuantity', 0) - expected_quantity) < 1:
            print(f"   ✅ Quantity is correct! {stats_data.get('totalQuantity', 0)}")
        else:
            print(f"   ❌ Quantity is wrong! Expected: {expected_quantity}, Got: {stats_data.get('totalQuantity', 0)}")
            
        if stats_data.get('recordCount', 0) == expected_count:
            print(f"   ✅ Record count is correct! {stats_data.get('recordCount', 0)}")
        else:
            print(f"   ❌ Record count is wrong! Expected: {expected_count}, Got: {stats_data.get('recordCount', 0)}")
    else:
        print(f"   [ERROR] Stats request failed: {stats_response.text[:200]}")
    
    # Test sales history API
    print(f"\n3. Testing sales history API...")
    sales_response = requests.get(
        f"{BASE_URL}/sales-history?year=2024&month=11&limit=5",
        headers={"Authorization": f"Bearer {admin_token}"}
    )
    
    print(f"   Sales history status: {sales_response.status_code}")
    if sales_response.status_code == 200:
        sales_data = sales_response.json()
        print(f"   Sales history response:")
        print(f"     Total records: {sales_data.get('total', 0)}")
        print(f"     Data array length: {len(sales_data.get('records', []))}")
        
        if sales_data.get('records'):
            print(f"     Sample record:")
            sample = sales_data['records'][0]
            print(f"       Customer: {sample.get('customerName', 'N/A')}")
            print(f"       Product: {sample.get('productDescription', 'N/A')}")
            print(f"       Quantity: {sample.get('quantity', 0)}")
            print(f"       Total Sales: ${sample.get('totalSales', 0):.2f}")
            print(f"       Year-Month: {sample.get('yearMonth', 'N/A')}")
    else:
        print(f"   [ERROR] Sales history request failed: {sales_response.text[:200]}")
    
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
            filename = "november_2024_report_final_test.xlsx"
            with open(filename, 'wb') as f:
                f.write(instant_response.content)
            print(f"   [OK] Saved as: {filename}")
            
            # Analyze the Excel file
            print(f"\n5. Analyzing the report...")
            try:
                # Read all sheets
                excel_file = pd.ExcelFile(filename)
                print(f"   Sheets: {excel_file.sheet_names}")
                
                for sheet_name in excel_file.sheet_names:
                    print(f"\n   Sheet: {sheet_name}")
                    df = pd.read_excel(filename, sheet_name=sheet_name)
                    print(f"     Rows: {len(df)}")
                    print(f"     Columns: {list(df.columns)}")
                    
                    if len(df) > 0:
                        print(f"     First 10 rows:")
                        print(df.head(10).to_string())
                        
                        # Look for revenue values
                        for i, row in df.iterrows():
                            if 'Total Revenue' in str(row.iloc[0]):
                                revenue_value = str(row.iloc[1])
                                print(f"     🎯 Total Revenue in report: {revenue_value}")
                                if '$0.00' not in revenue_value and '$0' not in revenue_value:
                                    print(f"   ✅ SUCCESS! Report shows non-zero revenue!")
                                else:
                                    print(f"   ❌ Report still shows $0.00 revenue!")
                                break
                    else:
                        print(f"     [WARNING] Sheet is empty!")
                        
            except Exception as e:
                print(f"   [ERROR] Could not analyze report: {e}")
        else:
            print(f"   [WARNING] Unexpected content type")
            print(f"   Response: {instant_response.text[:500]}")
    else:
        print(f"   [ERROR] Report generation failed: {instant_response.text[:500]}")
        
except Exception as e:
    print(f"   [ERROR] Test failed: {e}")

print(f"\n" + "=" * 80)
print("DEPLOYED BACKEND TEST COMPLETE")
print("=" * 80)

# Final summary
print(f"\n🎯 FINAL SUMMARY:")
print(f"1. Sales Statistics API: {'✅ FIXED' if '✅ Revenue is correct!' in str(locals()) else '❌ STILL BROKEN'}")
print(f"2. Sales History API: {'✅ FIXED' if 'Data array length: 5' in str(locals()) else '❌ STILL BROKEN'}")
print(f"3. Report Generation: {'✅ FIXED' if 'SUCCESS! Report shows non-zero revenue!' in str(locals()) else '❌ STILL BROKEN'}")
print(f"\nIf all three show ✅ FIXED, then the November 2024 report issue is resolved!")
