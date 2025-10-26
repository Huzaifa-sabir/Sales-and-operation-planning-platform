"""
Test PDF generation and date filtering step by step
"""
import requests
import time
import os

BASE_URL = "https://sales-and-operation-planning-platform-1.onrender.com/api/v1"

print("=" * 80)
print("STEP-BY-STEP TESTING OF PDF AND DATE FILTERING")
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
    
    # Test PDF generation (no date filters)
    print(f"\n2. Testing PDF generation (no date filters)...")
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
            filename = "test_report.pdf"
            with open(filename, 'wb') as f:
                f.write(pdf_response.content)
            print(f"   [OK] Saved PDF as: {filename}")
            print(f"   PDF file size: {len(pdf_response.content)} bytes")
        else:
            print(f"   ❌ PDF generation failed - unexpected content type")
            print(f"   Response: {pdf_response.text[:500]}")
    else:
        print(f"   ❌ PDF generation failed: {pdf_response.text[:500]}")
    
    # Test Excel with year/month filters (simpler than date range)
    print(f"\n3. Testing Excel with year/month filters...")
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
        filename = "november_2024_year_month_filter.xlsx"
        with open(filename, 'wb') as f:
            f.write(excel_year_month_response.content)
        print(f"   [OK] Saved as: {filename}")
        print(f"   File size: {len(excel_year_month_response.content)} bytes")
    else:
        print(f"   ❌ Excel with year/month filter failed: {excel_year_month_response.text[:200]}")
    
    # Test Excel with date range filters
    print(f"\n4. Testing Excel with date range filters...")
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
        filename = "november_2024_date_range_filter.xlsx"
        with open(filename, 'wb') as f:
            f.write(excel_date_range_response.content)
        print(f"   [OK] Saved as: {filename}")
        print(f"   File size: {len(excel_date_range_response.content)} bytes")
    else:
        print(f"   ❌ Excel with date range filter failed: {excel_date_range_response.text[:200]}")
    
    # Compare file sizes
    print(f"\n5. Comparing file sizes...")
    try:
        # Get the simple report size (no filters)
        simple_report_size = 8993  # From previous test
        
        if os.path.exists("november_2024_year_month_filter.xlsx"):
            year_month_size = os.path.getsize("november_2024_year_month_filter.xlsx")
            print(f"   Simple report (no filter): {simple_report_size} bytes")
            print(f"   Year/Month filter report: {year_month_size} bytes")
            
            if year_month_size < simple_report_size:
                print(f"   ✅ Year/Month filtering IS working - file is smaller!")
            else:
                print(f"   ❌ Year/Month filtering NOT working - file is same/larger size")
        
        if os.path.exists("november_2024_date_range_filter.xlsx"):
            date_range_size = os.path.getsize("november_2024_date_range_filter.xlsx")
            print(f"   Date range filter report: {date_range_size} bytes")
            
            if date_range_size < simple_report_size:
                print(f"   ✅ Date range filtering IS working - file is smaller!")
            else:
                print(f"   ❌ Date range filtering NOT working - file is same/larger size")
                
    except Exception as e:
        print(f"   [ERROR] Could not compare file sizes: {e}")
        
except Exception as e:
    print(f"   [ERROR] Test failed: {e}")

print(f"\n" + "=" * 80)
print("STEP-BY-STEP TEST COMPLETE")
print("=" * 80)

# Final summary
print(f"\n🎯 FINAL RESULTS:")
if 'PDF generation successful!' in str(locals()):
    print(f"✅ PDF Generation: WORKING!")
else:
    print(f"❌ PDF Generation: Still failing")

if 'Year/Month filtering IS working' in str(locals()):
    print(f"✅ Year/Month Filtering: WORKING!")
else:
    print(f"❌ Year/Month Filtering: Not working")

if 'Date range filtering IS working' in str(locals()):
    print(f"✅ Date Range Filtering: WORKING!")
else:
    print(f"❌ Date Range Filtering: Not working")
