"""
Analyze customer Excel structure to create matching template
"""
import pandas as pd
import openpyxl

def analyze_excel():
    excel_file = 'Consolidated Master File SOP_Nov25 - JR.xlsx'
    xl = pd.ExcelFile(excel_file)
    
    # Get customer sheets (exclude system sheets)
    system_sheets = ['Budget', 'Sheet1', 'Summary', 'Full Harvest', 'Sales History']
    customer_sheets = [s for s in xl.sheet_names if s not in system_sheets]
    
    print(f"Found {len(customer_sheets)} customer sheets")
    print(f"First customer sheet: {customer_sheets[0]}")
    
    # Read first customer sheet to understand structure
    df = pd.read_excel(excel_file, sheet_name=customer_sheets[0], header=None, nrows=20)
    
    print("\n" + "="*80)
    print(f"Structure of '{customer_sheets[0]}' sheet:")
    print("="*80)
    print(df.to_string())
    
    # Check row 6 (0-indexed = row 7) for headers
    print("\n" + "="*80)
    print("Row 6 (header row):")
    print("="*80)
    header_row = pd.read_excel(excel_file, sheet_name=customer_sheets[0], header=None, skiprows=5, nrows=1)
    print(header_row.to_string())
    
    # Check row 7 (first data row)
    print("\n" + "="*80)
    print("Row 7 (first data row):")
    print("="*80)
    data_row = pd.read_excel(excel_file, sheet_name=customer_sheets[0], header=None, skiprows=6, nrows=1)
    print(data_row.to_string())

if __name__ == '__main__':
    analyze_excel()

