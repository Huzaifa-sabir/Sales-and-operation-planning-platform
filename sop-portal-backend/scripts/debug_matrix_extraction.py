"""
Debug matrix extraction to see what's being extracted
"""
import pandas as pd
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

def debug_matrix_extraction():
    excel_file = 'Consolidated Master File SOP_Nov25 - JR.xlsx'
    
    # Find "Cheney Brothers" sheet
    xl = pd.ExcelFile(excel_file)
    cheney_sheets = [s for s in xl.sheet_names if 'cheney' in s.lower()]
    
    if not cheney_sheets:
        print("Cheney Brothers sheet not found. Trying 'Better Butter' sheet...")
        sheet_name = 'Better Butter'
    else:
        sheet_name = cheney_sheets[0]
        print(f"Found Cheney sheet: {sheet_name}")
    
    print(f"\nAnalyzing sheet: {sheet_name}")
    
    # Try different skip_rows values
    for skip_rows in [6, 7, 5]:
        print(f"\n--- Using skiprows={skip_rows} ---")
        try:
            df = pd.read_excel(excel_file, sheet_name=sheet_name, header=None, skiprows=skip_rows, nrows=10)
            print(f"Shape: {df.shape}")
            print(f"First row (index 0):")
            for i in range(min(10, len(df.columns))):
                val = df.iloc[0, i] if i < len(df.columns) else None
                print(f"  Column {i}: {val} (type: {type(val).__name__})")
            
            # Check if this looks like data or header
            if df.shape[0] > 0:
                col2_val = df.iloc[0, 2] if df.shape[1] > 2 else None
                print(f"  Column 2 value: {col2_val}")
                if col2_val and str(col2_val).strip() and not str(col2_val).startswith("ITEM"):
                    print(f"  ✓ This looks like data!")
                    # Show first 5 rows
                    print(f"\n  First 5 data rows (columns 1-3):")
                    for idx in range(min(5, len(df))):
                        row_num = df.iloc[idx, 1] if df.shape[1] > 1 else None
                        item_code = df.iloc[idx, 2] if df.shape[1] > 2 else None
                        desc = df.iloc[idx, 3] if df.shape[1] > 3 else None
                        print(f"    Row {idx}: #{row_num}, Code={item_code}, Desc={desc}")
        except Exception as e:
            print(f"  Error: {e}")

if __name__ == '__main__':
    debug_matrix_extraction()

