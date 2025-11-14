"""
Wait and test with correct collection name
"""
import requests
import pandas as pd
import time
from datetime import datetime

BASE_URL = "https://sales-and-operation-planning-platform-1.onrender.com/api/v1"

print("=" * 80)
print("WAITING 4 MINUTES FOR COLLECTION NAME FIX TO DEPLOY")
print("=" * 80)

print("\nWaiting 4 minutes for deployment...")
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
    
    print(f"\n2. Generating Excel report for November 2024...")
    excel_response = requests.post(
        f"{BASE_URL}/reports/generate-instant",
        json={
            "reportType": "sales_summary",
            "format": "excel",
            "year": 2024,
            "month": 11,
            "includeCharts": False,
            "includeRawData": True
        },
        headers={"Authorization": f"Bearer {admin_token}", "Content-Type": "application/json"},
        timeout=60
    )
    
    if excel_response.status_code == 200:
        filename = f"FINAL_REPORT_WITH_DATA_{datetime.now().strftime('%Y%m%d_%H%M%S')}.xlsx"
        with open(filename, 'wb') as f:
            f.write(excel_response.content)
        print(f"   ✅ Report saved: {filename} ({len(excel_response.content)} bytes)")
        
        print(f"\n3. Analyzing report contents...")
        try:
            # Summary sheet
            print(f"\n   === SUMMARY SHEET ===")
            df_summary = pd.read_excel(filename, sheet_name='Summary')
            print(df_summary.to_string())
            
            # Check if we have actual data now
            for i, row in df_summary.iterrows():
                if 'Total Revenue' in str(row.iloc[0]):
                    revenue_value = str(row.iloc[1])
                    print(f"\n   🎯 KEY FINDING: Total Revenue = {revenue_value}")
                    if '$0.00' not in revenue_value:
                        print(f"   ✅ SUCCESS! Report now has actual data!")
                    else:
                        print(f"   ❌ Still showing \$0.00 - issue persists")
                    break
            
            # Monthly Trends
            if 'Monthly Trends' in pd.ExcelFile(filename).sheet_names:
                print(f"\n   === MONTHLY TRENDS SHEET (First 5 rows) ===")
                df_trends = pd.read_excel(filename, sheet_name='Monthly Trends')
                print(df_trends.head(6).to_string())
            
            # Top Customers
            if 'Top Customers' in pd.ExcelFile(filename).sheet_names:
                print(f"\n   === TOP CUSTOMERS SHEET (First 5 rows) ===")
                df_customers = pd.read_excel(filename, sheet_name='Top Customers')
                print(df_customers.head(6).to_string())
                
        except Exception as e:
            print(f"   [ERROR] Could not analyze report: {e}")
            
    else:
        print(f"   ❌ Failed: {excel_response.text[:200]}")
        
except Exception as e:
    print(f"   [ERROR] Test failed: {e}")

print(f"\n" + "=" * 80)
print("TEST COMPLETE")
print("=" * 80)

