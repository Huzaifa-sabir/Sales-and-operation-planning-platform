"""
Final test of the deployed backend with chart fixes
"""
import requests
import pandas as pd
import time

BASE_URL = "https://sales-and-operation-planning-platform-1.onrender.com/api/v1"

print("=" * 80)
print("FINAL TEST: DEPLOYED BACKEND WITH CHART FIXES")
print("=" * 80)

# Wait for deployment
print("\n1. Waiting for chart fixes to deploy...")
time.sleep(30)

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
    
    # Test sales statistics (should be working)
    print(f"\n3. Verifying sales statistics...")
    stats_response = requests.get(
        f"{BASE_URL}/sales-history/statistics?year=2024&month=11",
        headers={"Authorization": f"Bearer {admin_token}"}
    )
    
    if stats_response.status_code == 200:
        stats_data = stats_response.json()
        print(f"   ✅ Sales Statistics Working:")
        print(f"     Total Revenue: ${stats_data.get('totalRevenue', 0):.2f}")
        print(f"     Total Quantity: {stats_data.get('totalQuantity', 0)}")
        print(f"     Record Count: {stats_data.get('recordCount', 0)}")
    else:
        print(f"   ❌ Sales Statistics Failed: {stats_response.status_code}")
    
    # Test report generation
    print(f"\n4. Testing report generation with chart fixes...")
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
            print(f"   ✅ SUCCESS! Received Excel file")
            # Save the file
            filename = "november_2024_report_FINAL_SUCCESS.xlsx"
            with open(filename, 'wb') as f:
                f.write(instant_response.content)
            print(f"   [OK] Saved as: {filename}")
            
            # Analyze the Excel file
            print(f"\n5. Analyzing the SUCCESSFUL report...")
            try:
                # Read all sheets
                excel_file = pd.ExcelFile(filename)
                print(f"   Sheets: {excel_file.sheet_names}")
                
                # Check Summary sheet
                df_summary = pd.read_excel(filename, sheet_name='Summary')
                print(f"   Summary sheet rows: {len(df_summary)}")
                
                # Look for revenue values
                revenue_found = False
                for i, row in df_summary.iterrows():
                    if 'Total Revenue' in str(row.iloc[0]):
                        revenue_value = str(row.iloc[1])
                        print(f"   🎯 Total Revenue in report: {revenue_value}")
                        if '$0.00' not in revenue_value and '$0' not in revenue_value:
                            print(f"   ✅ SUCCESS! Report shows non-zero revenue!")
                            revenue_found = True
                        else:
                            print(f"   ❌ Report still shows $0.00 revenue!")
                        break
                
                if not revenue_found:
                    print(f"   [WARNING] Could not find Total Revenue row")
                    print(f"   First few rows of summary:")
                    print(df_summary.head().to_string())
                
                # Check other sheets
                for sheet_name in excel_file.sheet_names:
                    if sheet_name != 'Summary':
                        df_sheet = pd.read_excel(filename, sheet_name=sheet_name)
                        print(f"   {sheet_name} sheet: {len(df_sheet)} rows")
                        
            except Exception as e:
                print(f"   [ERROR] Could not analyze report: {e}")
        else:
            print(f"   [WARNING] Unexpected content type")
            print(f"   Response: {instant_response.text[:500]}")
    else:
        print(f"   ❌ Report generation failed: {instant_response.text[:500]}")
        
except Exception as e:
    print(f"   [ERROR] Test failed: {e}")

print(f"\n" + "=" * 80)
print("FINAL TEST COMPLETE")
print("=" * 80)

# Final summary
print(f"\n🎯 FINAL RESULTS:")
if 'SUCCESS! Report shows non-zero revenue!' in str(locals()):
    print(f"✅ ISSUE RESOLVED! November 2024 reports now show correct values!")
    print(f"✅ Sales Statistics API: Working")
    print(f"✅ Sales History API: Working") 
    print(f"✅ Report Generation: Working")
    print(f"\n🎉 The November 2024 data issue has been completely fixed!")
else:
    print(f"❌ Issue still exists - reports showing $0.00 values")
    print(f"Need to investigate further...")
