"""
Comprehensive test of all features after fixes
"""
import requests
import time

BASE_URL = "https://sales-and-operation-planning-platform-1.onrender.com/api/v1"

print("=" * 80)
print("COMPREHENSIVE TEST - ALL FEATURES")
print("=" * 80)

# Wait for deployment
print("\nWaiting 4 minutes for latest fixes to deploy...")
time.sleep(240)

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
    
    # Test 1: Year/Month filtering (should work)
    print(f"\n2. Testing Excel with year/month filter (Nov 2024)...")
    excel_ym_response = requests.post(
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
    
    ym_success = excel_ym_response.status_code == 200
    print(f"   Status: {excel_ym_response.status_code}")
    if ym_success:
        with open("test_year_month.xlsx", 'wb') as f:
            f.write(excel_ym_response.content)
        print(f"   ✅ Year/Month filtering working ({len(excel_ym_response.content)} bytes)")
    else:
        print(f"   ❌ Failed: {excel_ym_response.text[:200]}")
    
    # Test 2: Date range filtering (should now work with Normal style fix)
    print(f"\n3. Testing Excel with date range filter (Dec 2024 - Jan 2025)...")
    excel_dr_response = requests.post(
        f"{BASE_URL}/reports/generate-instant",
        json={
            "reportType": "sales_summary",
            "format": "excel",
            "startDate": "2024-12-10",
            "endDate": "2025-01-30",
            "includeCharts": False,
            "includeRawData": True
        },
        headers={"Authorization": f"Bearer {admin_token}", "Content-Type": "application/json"},
        timeout=60
    )
    
    dr_success = excel_dr_response.status_code == 200
    print(f"   Status: {excel_dr_response.status_code}")
    if dr_success:
        with open("test_date_range.xlsx", 'wb') as f:
            f.write(excel_dr_response.content)
        print(f"   ✅ Date range filtering working ({len(excel_dr_response.content)} bytes)")
    else:
        print(f"   ❌ Failed: {excel_dr_response.text[:200]}")
    
    # Test 3: PDF generation (should now work)
    print(f"\n4. Testing PDF generation...")
    pdf_response = requests.post(
        f"{BASE_URL}/reports/generate-instant",
        json={
            "reportType": "sales_summary",
            "format": "pdf",
            "year": 2024,
            "month": 11,
            "includeCharts": False,
            "includeRawData": True
        },
        headers={"Authorization": f"Bearer {admin_token}", "Content-Type": "application/json"},
        timeout=60
    )
    
    pdf_success = pdf_response.status_code == 200 and 'application/pdf' in pdf_response.headers.get('content-type', '')
    print(f"   Status: {pdf_response.status_code}")
    if pdf_success:
        with open("test_november_2024.pdf", 'wb') as f:
            f.write(pdf_response.content)
        print(f"   ✅ PDF generation working ({len(pdf_response.content)} bytes)")
    else:
        print(f"   ❌ Failed: {pdf_response.text[:200]}")
        
except Exception as e:
    print(f"   [ERROR] Test failed: {e}")

print(f"\n" + "=" * 80)
print("COMPREHENSIVE TEST COMPLETE")
print("=" * 80)

print(f"\n🎯 RESULTS:")
print(f"1. Year/Month Filtering: {'✅ WORKING' if ym_success else '❌ FAILING'}")
print(f"2. Date Range Filtering: {'✅ WORKING' if dr_success else '❌ FAILING'}")
print(f"3. PDF Generation: {'✅ WORKING' if pdf_success else '❌ FAILING'}")

if ym_success and dr_success and pdf_success:
    print(f"\n🎉🎉🎉 ALL FEATURES WORKING! 🎉🎉🎉")
else:
    print(f"\n⚠️  Some features still need work")

