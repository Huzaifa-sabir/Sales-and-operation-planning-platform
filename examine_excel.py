import pandas as pd
import sys

file = 'Consolidated Master File SOP_Nov25 - JR.xlsx'

try:
    xl = pd.ExcelFile(file)
    print(f"File: {file}")
    print(f"Total sheets: {len(xl.sheet_names)}")
    print(f"\nSheet names: {xl.sheet_names[:10]}...")
    
    # Filter customer sheets (exclude system sheets)
    system_sheets = ['Budget', 'Sheet1', 'Summary', 'Full Harvest']
    customer_sheets = [s for s in xl.sheet_names if s not in system_sheets]
    
    print(f"\nCustomer sheets found: {len(customer_sheets)}")
    print(f"Sample: {customer_sheets[:5]}")
    
    # Examine one customer sheet
    if customer_sheets:
        sample_sheet = customer_sheets[0]
        print(f"\n=== Examining sheet: {sample_sheet} ===")
        df = pd.read_excel(file, sheet_name=sample_sheet, nrows=15)
        print(f"Shape: {df.shape}")
        print(f"Columns ({len(df.columns)}): {list(df.columns)}")
        print(f"\nFirst 5 rows:")
        print(df.head().to_string())
        
        # Look for product codes/descriptions
        print(f"\n=== Looking for product info ===")
        for col in df.columns:
            if 'code' in str(col).lower() or 'item' in str(col).lower() or 'product' in str(col).lower():
                print(f"Found column: {col}")
                if len(df[col].dropna()) > 0:
                    print(f"  Sample values: {df[col].dropna().head(3).tolist()}")
    
    # Examine Summary sheet
    if 'Summary' in xl.sheet_names:
        print(f"\n=== Examining Summary sheet ===")
        df_summary = pd.read_excel(file, sheet_name='Summary', nrows=20)
        print(f"Shape: {df_summary.shape}")
        print(f"Columns: {list(df_summary.columns)}")
        print(f"\nFirst 5 rows:")
        print(df_summary.head().to_string())
        
except Exception as e:
    print(f"Error: {e}")
    import traceback
    traceback.print_exc()

