"""
Download and analyze a completed report to see why it shows 0.00 values
"""
import requests
import pandas as pd

BASE_URL = "https://sales-and-operation-planning-platform-1.onrender.com/api/v1"

print("=" * 80)
print("DOWNLOADING AND ANALYZING COMPLETED REPORT")
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

# Download a completed report
report_id = "68fe3ec531691689c797bd86"  # From the previous test
print(f"\n2. Downloading report {report_id}...")

try:
    download_response = requests.get(
        f"{BASE_URL}/reports/{report_id}/download",
        headers={"Authorization": f"Bearer {admin_token}"}
    )
    
    print(f"   Download status: {download_response.status_code}")
    print(f"   Content-Type: {download_response.headers.get('content-type', 'N/A')}")
    
    if download_response.status_code == 200:
        # Save the file
        filename = f"downloaded_report_{report_id}.xlsx"
        with open(filename, 'wb') as f:
            f.write(download_response.content)
        print(f"   [OK] Saved as: {filename}")
        
        # Analyze the Excel file
        print(f"\n3. Analyzing Excel file...")
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
                    
                    # Look for numeric columns
                    numeric_cols = df.select_dtypes(include=['number']).columns
                    if len(numeric_cols) > 0:
                        print(f"     Numeric columns: {list(numeric_cols)}")
                        for col in numeric_cols:
                            non_zero_count = (df[col] != 0).sum()
                            print(f"       {col}: {non_zero_count} non-zero values out of {len(df)}")
                else:
                    print(f"     [WARNING] Sheet is empty!")
                    
        except Exception as e:
            print(f"   [ERROR] Could not analyze Excel file: {e}")
    else:
        print(f"   [ERROR] Download failed: {download_response.text[:200]}")
        
except Exception as e:
    print(f"   [ERROR] Download test failed: {e}")

# Also test the instant report we just generated
print(f"\n4. Analyzing the instant report we just generated...")
try:
    df = pd.read_excel("november_2024_report.xlsx")
    print(f"   Rows: {len(df)}")
    print(f"   Columns: {list(df.columns)}")
    
    if len(df) > 0:
        print(f"   Full content:")
        print(df.to_string())
        
        # Look for any non-empty cells
        non_empty_cells = 0
        for col in df.columns:
            non_empty_count = df[col].notna().sum()
            non_empty_cells += non_empty_count
            if non_empty_count > 0:
                print(f"   Column '{col}' has {non_empty_count} non-empty values")
        
        print(f"   Total non-empty cells: {non_empty_cells}")
    else:
        print(f"   [WARNING] Report is completely empty!")
        
except Exception as e:
    print(f"   [ERROR] Could not analyze instant report: {e}")

print(f"\n" + "=" * 80)
print("REPORT ANALYSIS COMPLETE")
print("=" * 80)
