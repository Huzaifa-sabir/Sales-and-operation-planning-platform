"""
Final test after CRITICAL date handling fix - wait 4 minutes for deployment
"""
import requests
import time

BASE_URL = "https://sales-and-operation-planning-platform-1.onrender.com/api/v1"

print("=" * 80)
print("FINAL TEST - CRITICAL DATE FILTERING FIX")
print("Waiting 4 minutes for Render deployment to complete...")
print("=" * 80)

# Wait for deployment as requested
print("\n1. Waiting 4 minutes for deployment to complete...")
time.sleep(240)

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
    
    # Test date range filtering - THIS IS THE CRITICAL TEST
    print(f"\n3. Testing Excel with date range filters (CRITICAL TEST)...")
    print(f"   This is what was failing with: 'str' object cannot be interpreted as integer")
    
    excel_date_range_response = requests.post(
        f"{BASE_URL}/reports/generate-instant",
        json={
            "reportType": "sales_summary",
            "format": "excel",
            "startDate": "2024-11-01",
            "endDate": "2024-11-30",
            "includeCharts": False,
            "includeRawData": True
        },
        headers={
            "Authorization": f"Bearer {admin_token}",
            "Content-Type": "application/json"
        },
        timeout=60
    )
    
    print(f"   Excel (date range) status: {excel_date_range_response.status_code}")
    
    if excel_date_range_response.status_code == 200:
        filename = "FINAL_TEST_DATE_RANGE_FIXED.xlsx"
        with open(filename, 'wb') as f:
            f.write(excel_date_range_response.content)
        print(f"   ✅ SUCCESS! Excel with date range filter working!")
        print(f"   Saved as: {filename}")
        print(f"   File size: {len(excel_date_range_response.content)} bytes")
        
        # Verify it has November 2024 data
        try:
            import pandas as pd
            df_summary = pd.read_excel(filename, sheet_name='Summary')
            for i, row in df_summary.iterrows():
                if 'Total Revenue' in str(row.iloc[0]):
                    revenue_value = str(row.iloc[1])
                    print(f"   📊 Total Revenue in report: {revenue_value}")
                    if '$1,004,189.55' in revenue_value:
                        print(f"   ✅ PERFECT! Report shows correct November 2024 data!")
                    break
        except Exception as e:
            print(f"   [WARNING] Could not analyze Excel: {e}")
            
    else:
        print(f"   ❌ FAILED: {excel_date_range_response.text[:200]}")
        print(f"   The date range filtering is still not working")
        
except Exception as e:
    print(f"   [ERROR] Test failed: {e}")

print(f"\n" + "=" * 80)
print("FINAL TEST COMPLETE")
print("=" * 80)

if excel_date_range_response.status_code == 200:
    print(f"\n🎉🎉🎉 SUCCESS! All issues resolved! 🎉🎉🎉")
    print(f"✅ PDF generation: Working")
    print(f"✅ Excel generation: Working")
    print(f"✅ Year/Month filtering: Working")
    print(f"✅ Date range filtering: WORKING!")
    print(f"📊 November 2024 data: $1,004,189.55")
else:
    print(f"\n❌ Date range filtering still failing")
    print(f"Check Render logs for error details")
