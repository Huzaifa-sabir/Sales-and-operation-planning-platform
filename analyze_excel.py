import pandas as pd
import os
from pathlib import Path

# Get all Excel files
excel_files = [
    "Consolidated S_OP9.xlsx",
    "02. Sales Comparison 20250930 ER.xlsx",
    "01. 2023 _ Jan-Sept _ S_OP Oct-Dec.xlsx",
    "Consolidated Master File SOP_Nov25 - RANDELL.xlsx",
    "Consolidated Master File SOP_Nov25 - ANTHONY.xlsx",
    "Consolidated Master File SOP_Nov25 - JR.xlsx",
]

print("=" * 100)
print("ANALYZING S&OP EXCEL FILES")
print("=" * 100)

for file in excel_files:
    file_path = f"D:\\Heavy\\{file}"
    if not os.path.exists(file_path):
        continue

    print(f"\n{'='*100}")
    print(f"FILE: {file}")
    print(f"{'='*100}")

    try:
        # Get all sheet names
        xl_file = pd.ExcelFile(file_path)
        print(f"\nSheet Names ({len(xl_file.sheet_names)} sheets):")
        for idx, sheet in enumerate(xl_file.sheet_names, 1):
            print(f"  {idx}. {sheet}")

        # Analyze first 3 sheets in detail
        for sheet_name in xl_file.sheet_names[:3]:
            print(f"\n--- Sheet: '{sheet_name}' ---")
            try:
                df = pd.read_excel(file_path, sheet_name=sheet_name, nrows=10)
                print(f"Shape: {df.shape[0]} rows × {df.shape[1]} columns (showing first 10 rows)")
                print(f"\nColumns ({len(df.columns)}):")
                for col in df.columns:
                    print(f"  - {col}")

                print(f"\nFirst 5 rows preview:")
                print(df.head().to_string())

            except Exception as e:
                print(f"Error reading sheet '{sheet_name}': {str(e)}")

        if len(xl_file.sheet_names) > 3:
            print(f"\n... and {len(xl_file.sheet_names) - 3} more sheets")

    except Exception as e:
        print(f"Error analyzing file: {str(e)}")

print("\n" + "=" * 100)
print("ANALYSIS COMPLETE")
print("=" * 100)
