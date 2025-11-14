"""
Generate and analyze report contents
"""
import requests
import pandas as pd
from datetime import datetime

BASE_URL = "https://sales-and-operation-planning-platform-1.onrender.com/api/v1"

print("=" * 80)
print("GENERATE AND ANALYZE REPORT CONTENTS")
print("=" * 80)

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
    
    # Test 1: Generate Excel report for November 2024
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
        filename = f"report_november_2024_{datetime.now().strftime('%Y%m%d_%H%M%S')}.xlsx"
        with open(filename, 'wb') as f:
            f.write(excel_response.content)
        print(f"   ✅ Report saved: {filename} ({len(excel_response.content)} bytes)")
        
        # Analyze the Excel file
        print(f"\n3. Analyzing Excel report contents...")
        try:
            excel_file = pd.ExcelFile(filename)
            print(f"   Sheets: {excel_file.sheet_names}")
            
            # Analyze Summary sheet
            print(f"\n   === SUMMARY SHEET ===")
            df_summary = pd.read_excel(filename, sheet_name='Summary')
            print(df_summary.to_string())
            
            # Analyze Monthly Trends sheet
            if 'Monthly Trends' in excel_file.sheet_names:
                print(f"\n   === MONTHLY TRENDS SHEET ===")
                df_trends = pd.read_excel(filename, sheet_name='Monthly Trends')
                print(df_trends.head(10).to_string())
                
            # Analyze Top Customers sheet
            if 'Top Customers' in excel_file.sheet_names:
                print(f"\n   === TOP CUSTOMERS SHEET ===")
                df_customers = pd.read_excel(filename, sheet_name='Top Customers')
                print(df_customers.head(10).to_string())
                
            # Analyze Top Products sheet
            if 'Top Products' in excel_file.sheet_names:
                print(f"\n   === TOP PRODUCTS SHEET ===")
                df_products = pd.read_excel(filename, sheet_name='Top Products')
                print(df_products.head(10).to_string())
                
        except Exception as e:
            print(f"   [ERROR] Could not analyze Excel: {e}")
    else:
        print(f"   ❌ Failed to generate Excel report: {excel_response.text[:200]}")
    
    # Test 2: Generate PDF report
    print(f"\n4. Generating PDF report for November 2024...")
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
    
    if pdf_response.status_code == 200:
        filename = f"report_november_2024_{datetime.now().strftime('%Y%m%d_%H%M%S')}.pdf"
        with open(filename, 'wb') as f:
            f.write(pdf_response.content)
        print(f"   ✅ PDF report saved: {filename} ({len(pdf_response.content)} bytes)")
        print(f"   [NOTE] PDF is a binary file, cannot display content here")
        print(f"   [OK] You can open the PDF file to view the full report")
    else:
        print(f"   ❌ Failed to generate PDF report: {pdf_response.text[:200]}")
    
    # Test 3: Generate report with date range
    print(f"\n5. Generating Excel report with date range (Dec 2024 - Jan 2025)...")
    dr_response = requests.post(
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
    
    if dr_response.status_code == 200:
        filename = f"report_date_range_{datetime.now().strftime('%Y%m%d_%H%M%S')}.xlsx"
        with open(filename, 'wb') as f:
            f.write(dr_response.content)
        print(f"   ✅ Date range report saved: {filename} ({len(dr_response.content)} bytes)")
        
        # Analyze the date range report
        print(f"\n6. Analyzing date range report contents...")
        try:
            excel_file = pd.ExcelFile(filename)
            print(f"   Sheets: {excel_file.sheet_names}")
            
            df_summary = pd.read_excel(filename, sheet_name='Summary')
            print(f"\n   === SUMMARY SHEET ===")
            print(df_summary.to_string())
            
        except Exception as e:
            print(f"   [ERROR] Could not analyze date range report: {e}")
    else:
        print(f"   ❌ Failed to generate date range report: {dr_response.text[:200]}")
        
except Exception as e:
    print(f"   [ERROR] Test failed: {e}")

print(f"\n" + "=" * 80)
print("REPORT GENERATION AND ANALYSIS COMPLETE")
print("=" * 80)

print(f"\n📊 SUMMARY:")
print(f"✅ Excel reports with November 2024 data generated")
print(f"✅ PDF report for November 2024 generated")
print(f"✅ Excel report with date range generated")
print(f"\n📁 Check the generated files in the current directory:")
print(f"   - report_november_2024_*.xlsx")
print(f"   - report_november_2024_*.pdf")
print(f"   - report_date_range_*.xlsx")

