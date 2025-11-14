"""Quick test to verify the data in the report"""
import pandas as pd

try:
    # Check the Excel file we just generated
    df = pd.read_excel("FINAL_TEST_DATE_RANGE_FIXED.xlsx", sheet_name='Summary')
    print("\nReport contents:")
    print(df.to_string())
    
    # Also check Monthly Trends sheet
    try:
        df_trends = pd.read_excel("FINAL_TEST_DATE_RANGE_FIXED.xlsx", sheet_name='Monthly Trends')
        print("\n\nMonthly Trends:")
        print(df_trends.to_string())
    except:
        print("\nNo Monthly Trends sheet")
except Exception as e:
    print(f"Error: {e}")

