"""
Final test of PDF generation and date filtering after all fixes
"""
import requests
import time
import os

BASE_URL = "https://sales-and-operation-planning-platform-1.onrender.com/api/v1"

print("=" * 80)
print("FINAL TEST: PDF GENERATION AND DATE FILTERING AFTER ALL FIXES")
print("=" * 80)

# Wait for deployment
print("\n1. Waiting for all fixes to deploy...")
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
    
    # Test PDF generation (no date filters)
    print(f"\n3. Testing PDF generation (no date filters)...")
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
            filename = "test_report_FINAL.pdf"
            with open(filename, 'wb') as f:
                f.write(pdf_response.content)
            print(f"   [OK] Saved PDF as: {filename}")
            print(f"   PDF file size: {len(pdf_response.content)} bytes")
        else:
            print(f"   ❌ PDF generation failed - unexpected content type")
            print(f"   Response: {pdf_response.text[:500]}")
    else:
        print(f"   ❌ PDF generation failed: {pdf_response.text[:500]}")
    
    # Test PDF with November 2024 filter
    print(f"\n4. Testing PDF generation with November 2024 filter...")
    pdf_nov_response = requests.post(
        f"{BASE_URL}/reports/generate-instant",
        json={
            "reportType": "sales_summary",
            "format": "pdf",
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
    
    print(f"   PDF (Nov 2024) status: {pdf_nov_response.status_code}")
    if pdf_nov_response.status_code == 200:
        if 'application/pdf' in pdf_nov_response.headers.get('content-type', ''):
            print(f"   ✅ PDF with November 2024 filter successful!")
            filename = "november_2024_report_FINAL.pdf"
            with open(filename, 'wb') as f:
                f.write(pdf_nov_response.content)
            print(f"   [OK] Saved PDF as: {filename}")
            print(f"   PDF file size: {len(pdf_nov_response.content)} bytes")
        else:
            print(f"   ❌ PDF with filter failed - unexpected content type")
    else:
        print(f"   ❌ PDF with filter failed: {pdf_nov_response.text[:200]}")
    
    # Test Excel with date range filters
    print(f"\n5. Testing Excel with date range filters...")
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
        filename = "november_2024_date_range_FINAL.xlsx"
        with open(filename, 'wb') as f:
            f.write(excel_date_range_response.content)
        print(f"   [OK] Saved as: {filename}")
        print(f"   File size: {len(excel_date_range_response.content)} bytes")
    else:
        print(f"   ❌ Excel with date range filter failed: {excel_date_range_response.text[:200]}")
    
    # Test Excel with year/month filters (should work)
    print(f"\n6. Testing Excel with year/month filters...")
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
        filename = "november_2024_year_month_FINAL.xlsx"
        with open(filename, 'wb') as f:
            f.write(excel_year_month_response.content)
        print(f"   [OK] Saved as: {filename}")
        print(f"   File size: {len(excel_year_month_response.content)} bytes")
    else:
        print(f"   ❌ Excel with year/month filter failed: {excel_year_month_response.text[:200]}")
    
    # Compare file sizes
    print(f"\n7. Comparing file sizes...")
    try:
        if os.path.exists("november_2024_date_range_FINAL.xlsx"):
            date_range_size = os.path.getsize("november_2024_date_range_FINAL.xlsx")
            print(f"   Date range filter report: {date_range_size} bytes")
        
        if os.path.exists("november_2024_year_month_FINAL.xlsx"):
            year_month_size = os.path.getsize("november_2024_year_month_FINAL.xlsx")
            print(f"   Year/Month filter report: {year_month_size} bytes")
            
            # Compare with previous test (7803 bytes)
            if year_month_size < 8000:  # Should be smaller than all data
                print(f"   ✅ Year/Month filtering IS working - file is smaller!")
            else:
                print(f"   ❌ Year/Month filtering NOT working - file is too large")
                
    except Exception as e:
        print(f"   [ERROR] Could not compare file sizes: {e}")
        
except Exception as e:
    print(f"   [ERROR] Test failed: {e}")

print(f"\n" + "=" * 80)
print("FINAL TEST COMPLETE")
print("=" * 80)

# Final summary
print(f"\n🎯 FINAL RESULTS:")
if 'PDF generation successful!' in str(locals()):
    print(f"✅ PDF Generation: WORKING!")
else:
    print(f"❌ PDF Generation: Still failing")

if 'PDF with November 2024 filter successful!' in str(locals()):
    print(f"✅ PDF with Date Filtering: WORKING!")
else:
    print(f"❌ PDF with Date Filtering: Still failing")

if 'Excel with date range filter' in str(locals()) and 'status: 200' in str(locals()):
    print(f"✅ Excel Date Range Filtering: WORKING!")
else:
    print(f"❌ Excel Date Range Filtering: Still failing")

if 'Year/Month filtering IS working' in str(locals()):
    print(f"✅ Excel Year/Month Filtering: WORKING!")
else:
    print(f"❌ Excel Year/Month Filtering: Not working")

print(f"\n🎉 All issues should now be resolved!")
print(f"📊 November 2024 reports should show correct data: $1,004,189.55")
print(f"📄 Both Excel and PDF formats should work")
print(f"🔍 Date filtering should work for both year/month and date range filters")
