"""
Test matrix extraction to verify column mapping
"""
import pandas as pd
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

def test_extraction():
    excel_file = 'Consolidated Master File SOP_Nov25 - JR.xlsx'
    
    # Find "Cheney Brothers" or use first customer sheet
    xl = pd.ExcelFile(excel_file)
    cheney_sheets = [s for s in xl.sheet_names if 'cheney' in s.lower()]
    
    if not cheney_sheets:
        sheet_name = xl.sheet_names[0]  # Use first sheet
        print(f"Using sheet: {sheet_name}")
    else:
        sheet_name = cheney_sheets[0]
        print(f"Found Cheney sheet: {sheet_name}")
    
    print(f"\nTesting extraction from: {sheet_name}")
    
    # Try skiprows=7 (correct data row)
    df = pd.read_excel(excel_file, sheet_name=sheet_name, header=None, skiprows=7, nrows=10)
    
    print(f"\nShape: {df.shape}")
    print(f"\nFirst 3 rows (columns 0-4):")
    for idx in range(min(3, len(df))):
        row_num = df.iloc[idx, 1] if df.shape[1] > 1 else None
        group = df.iloc[idx, 2] if df.shape[1] > 2 else None
        item_code_raw = df.iloc[idx, 3] if df.shape[1] > 3 else None
        desc_raw = df.iloc[idx, 4] if df.shape[1] > 4 else None
        
        print(f"  Row {idx}:")
        print(f"    Column 1 (row #): {row_num}")
        print(f"    Column 2 (group): {group}")
        print(f"    Column 3 (item code?): {item_code_raw} (type: {type(item_code_raw).__name__})")
        print(f"    Column 4 (description?): {desc_raw}")
        
        # Normalize item code
        if pd.notna(item_code_raw):
            try:
                code_str = str(item_code_raw).strip()
                if code_str.isdigit():
                    normalized = code_str
                else:
                    numeric_part = ''.join(c for c in code_str if c.isdigit())
                    normalized = numeric_part if numeric_part else None
                print(f"    → Normalized item code: {normalized}")
            except:
                print(f"    → Normalization failed")

if __name__ == '__main__':
    test_extraction()

