"""
Test the storage directory fix and check debugging output
"""
import requests
import time

BASE_URL = "https://sales-and-operation-planning-platform-1.onrender.com/api/v1"

print("=" * 80)
print("TESTING STORAGE DIRECTORY FIX AND DEBUGGING")
print("=" * 80)

# Wait for deployment
print("\n1. Waiting for storage directory fix to deploy...")
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
    
    # Test PDF generation (no filters) - should work now with storage directory fix
    print(f"\n3. Testing PDF generation (no filters)...")
    pdf_response = requests.post(
        f"{BASE_URL}/reports/generate-instant",
        json={
            "reportType": "sales_summary",
            "format": "pdf",
            "includeCharts": False,
            "includeRawData": True
        },
        headers={
            "Authorization": f"Bearer {admin_token}",
            "Content-Type": "application/json"
        },
        timeout=60
    )
    
    print(f"   PDF report status: {pdf_response.status_code}")
    print(f"   Content-Type: {pdf_response.headers.get('content-type', 'N/A')}")
    
    if pdf_response.status_code == 200:
        if 'application/pdf' in pdf_response.headers.get('content-type', ''):
            print(f"   ✅ PDF generation successful!")
            print(f"   PDF file size: {len(pdf_response.content)} bytes")
        else:
            print(f"   ❌ PDF generation failed - unexpected content type")
            print(f"   Response: {pdf_response.text[:500]}")
    else:
        print(f"   ❌ PDF generation failed: {pdf_response.text[:500]}")
    
    # Test Excel with date range filters - should show debugging output
    print(f"\n4. Testing Excel with date range filters (check Render logs for debugging)...")
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
        print(f"   ✅ Excel with date range filter successful!")
        print(f"   File size: {len(excel_date_range_response.content)} bytes")
    else:
        print(f"   ❌ Excel with date range filter failed: {excel_date_range_response.text[:200]}")
        print(f"   Check Render logs for DEBUG output showing the date filtering process")
    
    # Test Excel with year/month filters (should work)
    print(f"\n5. Testing Excel with year/month filters...")
    excel_year_month_response = requests.post(
        f"{BASE_URL}/reports/generate-instant",
        json={
            "reportType": "sales_summary",
            "format": "excel",
            "year": 2024,
            "month": 11,
            "includeCharts": False,
            "includeRawData": True
        },
        headers={
            "Authorization": f"Bearer {admin_token}",
            "Content-Type": "application/json"
        },
        timeout=60
    )
    
    print(f"   Excel (year=2024, month=11) status: {excel_year_month_response.status_code}")
    if excel_year_month_response.status_code == 200:
        print(f"   ✅ Excel with year/month filter successful!")
        print(f"   File size: {len(excel_year_month_response.content)} bytes")
    else:
        print(f"   ❌ Excel with year/month filter failed: {excel_year_month_response.text[:200]}")
        
except Exception as e:
    print(f"   [ERROR] Test failed: {e}")

print(f"\n" + "=" * 80)
print("STORAGE DIRECTORY FIX TEST COMPLETE")
print("=" * 80)

# Final summary
print(f"\n🎯 RESULTS:")
if 'PDF generation successful!' in str(locals()):
    print(f"✅ PDF Generation: FIXED!")
else:
    print(f"❌ PDF Generation: Still failing")

if 'Excel with date range filter successful!' in str(locals()):
    print(f"✅ Excel Date Range Filtering: FIXED!")
else:
    print(f"❌ Excel Date Range Filtering: Still failing - check Render logs for DEBUG output")

if 'Excel with year/month filter successful!' in str(locals()):
    print(f"✅ Excel Year/Month Filtering: WORKING!")
else:
    print(f"❌ Excel Year/Month Filtering: Not working")

print(f"\n📋 NEXT STEPS:")
print(f"1. Check Render logs for DEBUG output showing date filtering process")
print(f"2. Look for 'DEBUG: Processing date filters' messages")
print(f"3. Verify the match_stage values are correct")
print(f"4. If date filtering still fails, the issue is in the MongoDB aggregation pipeline")
