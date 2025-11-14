"""
Check the generated report content
"""
import pandas as pd

try:
    df = pd.read_excel("test_output.xlsx", sheet_name='Summary')
    print("\nReport Summary:")
    print(df.to_string())
    
    # Check Monthly Trends
    try:
        df_trends = pd.read_excel("test_output.xlsx", sheet_name='Monthly Trends')
        print("\n\nMonthly Trends:")
        print(df_trends.to_string())
    except:
        print("\nNo Monthly Trends sheet")
        
except Exception as e:
    print(f"Error: {e}")
    print("\nTrying to find the latest Excel file...")
    
    import os
    import glob
    excel_files = glob.glob("*FINAL*.xlsx")
    print(f"Found Excel files: {excel_files}")
    
    if excel_files:
        latest = max(excel_files, key=os.path.getctime)
        print(f"Analyzing latest file: {latest}")
        try:
            df = pd.read_excel(latest, sheet_name='Summary')
            print(df.to_string())
        except Exception as e2:
            print(f"Error analyzing file: {e2}")

