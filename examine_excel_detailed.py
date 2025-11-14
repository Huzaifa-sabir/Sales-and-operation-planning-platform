import pandas as pd
import sys

file = 'Consolidated Master File SOP_Nov25 - JR.xlsx'

try:
    xl = pd.ExcelFile(file)
    
    # Get customer sheets
    system_sheets = ['Budget', 'Sheet1', 'Summary', 'Full Harvest']
    customer_sheets = [s for s in xl.sheet_names if s not in system_sheets]
    
    print(f"=== Analyzing Excel Structure ===\n")
    print(f"Total sheets: {len(xl.sheet_names)}")
    print(f"Customer sheets: {len(customer_sheets)}")
    
    # Examine a customer sheet more carefully
    sample = customer_sheets[0] if customer_sheets else None
    if sample:
        print(f"\n=== Detailed Analysis: {sample} ===")
        df = pd.read_excel(file, sheet_name=sample, header=None, nrows=30)
        
        # Find where actual data starts
        print("\nFirst 20 rows (looking for headers):")
        for i in range(min(20, len(df))):
            row = df.iloc[i]
            non_null = row.dropna()
            if len(non_null) > 0:
                print(f"Row {i}: {non_null.head(5).tolist()}")
        
        # Try to find product codes (usually numeric codes like 110010)
        print("\n=== Searching for product codes ===")
        df_all = pd.read_excel(file, sheet_name=sample)
        for col_idx in range(min(5, len(df_all.columns))):
            col = df_all.iloc[:, col_idx]
            # Look for numeric codes
            numeric_values = pd.to_numeric(col, errors='coerce').dropna()
            if len(numeric_values) > 0:
                # Check if values look like product codes (6-digit numbers)
                codes = numeric_values[numeric_values >= 100000]
                if len(codes) > 0:
                    print(f"Column {col_idx} might contain product codes: {codes.head(5).tolist()}")
                    
except Exception as e:
    print(f"Error: {e}")
    import traceback
    traceback.print_exc()

