"""
Test the fixed report generation for November 2024
"""
import requests
import pandas as pd

BASE_URL = "https://sales-and-operation-planning-platform-1.onrender.com/api/v1"

print("=" * 80)
print("TESTING FIXED REPORT GENERATION FOR NOVEMBER 2024")
print("=" * 80)

# Login as admin
print("\n1. Logging in as admin...")
admin_response = requests.post(
    f"{BASE_URL}/auth/login",
    json={"email": "admin@heavygarlic.com", "password": "admin123"},
    headers={"Content-Type": "application/json"}
)

admin_data = admin_response.json()
admin_token = admin_data.get("access_token")
print(f"   [OK] Admin logged in successfully")

# Test instant report generation for November 2024
print(f"\n2. Testing instant report generation for November 2024...")
try:
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
    print(f"   Content-Type: {instant_response.headers.get('content-type', 'N/A')}")
    
    if instant_response.status_code == 200:
        if 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet' in instant_response.headers.get('content-type', ''):
            print(f"   [SUCCESS] Received Excel file")
            # Save the file
            filename = "november_2024_report_fixed.xlsx"
            with open(filename, 'wb') as f:
                f.write(instant_response.content)
            print(f"   [OK] Saved as: {filename}")
            
            # Analyze the Excel file
            print(f"\n3. Analyzing the fixed Excel file...")
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
                        
                        # Look for numeric columns with non-zero values
                        numeric_cols = df.select_dtypes(include=['number']).columns
                        if len(numeric_cols) > 0:
                            print(f"     Numeric columns analysis:")
                            for col in numeric_cols:
                                non_zero_count = (df[col] != 0).sum()
                                max_val = df[col].max()
                                min_val = df[col].min()
                                print(f"       {col}: {non_zero_count} non-zero values, max={max_val}, min={min_val}")
                    else:
                        print(f"     [WARNING] Sheet is empty!")
                        
            except Exception as e:
                print(f"   [ERROR] Could not analyze Excel file: {e}")
        else:
            print(f"   [WARNING] Unexpected content type")
            print(f"   Response: {instant_response.text[:500]}")
    else:
        print(f"   [ERROR] Instant report failed: {instant_response.text[:500]}")
        
except Exception as e:
    print(f"   [ERROR] Instant report test failed: {e}")

# Test async report generation
print(f"\n4. Testing async report generation...")
try:
    async_response = requests.post(
        f"{BASE_URL}/reports/generate",
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
    
    print(f"   Async report status: {async_response.status_code}")
    
    if async_response.status_code == 202:
        print(f"   [INFO] Report generation started (async)")
        report_data = async_response.json()
        print(f"   Report ID: {report_data.get('reportId')}")
        print(f"   Status: {report_data.get('status')}")
        
        # Wait a moment and check status
        import time
        time.sleep(5)
        
        status_response = requests.get(
            f"{BASE_URL}/reports/{report_data.get('reportId')}",
            headers={"Authorization": f"Bearer {admin_token}"}
        )
        
        if status_response.status_code == 200:
            status_data = status_response.json()
            print(f"   Report status: {status_data.get('status')}")
            if status_data.get('status') == 'completed':
                print(f"   [SUCCESS] Report completed!")
                print(f"   File: {status_data.get('fileName')}")
                print(f"   Download URL: {status_data.get('downloadUrl')}")
            else:
                print(f"   [INFO] Report still processing...")
    else:
        print(f"   [ERROR] Async report failed: {async_response.text[:500]}")
        
except Exception as e:
    print(f"   [ERROR] Async report test failed: {e}")

print(f"\n" + "=" * 80)
print("REPORT GENERATION TEST COMPLETE")
print("=" * 80)
