"""
Test PDF generation and investigate date filtering issues
"""
import requests
import time

BASE_URL = "https://sales-and-operation-planning-platform-1.onrender.com/api/v1"

print("=" * 80)
print("TESTING PDF GENERATION AND DATE FILTERING")
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
    
    # Test PDF generation
    print(f"\n2. Testing PDF report generation...")
    pdf_response = requests.post(
        f"{BASE_URL}/reports/generate-instant",
        json={
            "reportType": "sales_summary",
            "format": "pdf",
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
    
    print(f"   PDF report status: {pdf_response.status_code}")
    print(f"   Content-Type: {pdf_response.headers.get('content-type', 'N/A')}")
    
    if pdf_response.status_code == 200:
        if 'application/pdf' in pdf_response.headers.get('content-type', ''):
            print(f"   ✅ PDF generation successful!")
            # Save the PDF file
            filename = "november_2024_report.pdf"
            with open(filename, 'wb') as f:
                f.write(pdf_response.content)
            print(f"   [OK] Saved PDF as: {filename}")
            print(f"   PDF file size: {len(pdf_response.content)} bytes")
        else:
            print(f"   ❌ PDF generation failed - unexpected content type")
            print(f"   Response: {pdf_response.text[:500]}")
    else:
        print(f"   ❌ PDF generation failed: {pdf_response.text[:500]}")
    
    # Test Excel with different date ranges to understand filtering
    print(f"\n3. Testing Excel with different date ranges...")
    
    # Test 1: All data (no date filter)
    print(f"\n3a. Testing Excel with NO date filter...")
    excel_all_response = requests.post(
        f"{BASE_URL}/reports/generate-instant",
        json={
            "reportType": "sales_summary",
            "format": "excel",
            "includeCharts": False,
            "includeRawData": True
        },
        headers={
            "Authorization": f"Bearer {admin_token}",
            "Content-Type": "application/json"
        },
        timeout=60
    )
    
    print(f"   Excel (all data) status: {excel_all_response.status_code}")
    if excel_all_response.status_code == 200:
        with open("all_data_report.xlsx", 'wb') as f:
            f.write(excel_all_response.content)
        print(f"   [OK] Saved all data report")
    
    # Test 2: November 2024 only
    print(f"\n3b. Testing Excel with November 2024 filter...")
    excel_nov_response = requests.post(
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
    
    print(f"   Excel (Nov 2024) status: {excel_nov_response.status_code}")
    if excel_nov_response.status_code == 200:
        with open("november_2024_only_report.xlsx", 'wb') as f:
            f.write(excel_nov_response.content)
        print(f"   [OK] Saved November 2024 report")
    
    # Test 3: Different year (2023)
    print(f"\n3c. Testing Excel with 2023 filter...")
    excel_2023_response = requests.post(
        f"{BASE_URL}/reports/generate-instant",
        json={
            "reportType": "sales_summary",
            "format": "excel",
            "startDate": "2023-01-01",
            "endDate": "2023-12-31",
            "includeCharts": False,
            "includeRawData": True
        },
        headers={
            "Authorization": f"Bearer {admin_token}",
            "Content-Type": "application/json"
        },
        timeout=60
    )
    
    print(f"   Excel (2023) status: {excel_2023_response.status_code}")
    if excel_2023_response.status_code == 200:
        with open("2023_only_report.xlsx", 'wb') as f:
            f.write(excel_2023_response.content)
        print(f"   [OK] Saved 2023 report")
    
    # Analyze the files to see if filtering is working
    print(f"\n4. Analyzing file sizes to check filtering...")
    try:
        import os
        all_data_size = os.path.getsize("all_data_report.xlsx")
        nov_data_size = os.path.getsize("november_2024_only_report.xlsx")
        year_2023_size = os.path.getsize("2023_only_report.xlsx")
        
        print(f"   All data report size: {all_data_size} bytes")
        print(f"   November 2024 report size: {nov_data_size} bytes")
        print(f"   2023 report size: {year_2023_size} bytes")
        
        if abs(all_data_size - nov_data_size) < 1000:
            print(f"   ❌ Date filtering NOT working - files are same size")
        else:
            print(f"   ✅ Date filtering IS working - files are different sizes")
            
    except Exception as e:
        print(f"   [ERROR] Could not analyze file sizes: {e}")
        
except Exception as e:
    print(f"   [ERROR] Test failed: {e}")

print(f"\n" + "=" * 80)
print("PDF AND DATE FILTERING TEST COMPLETE")
print("=" * 80)
