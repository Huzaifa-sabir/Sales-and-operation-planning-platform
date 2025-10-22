import pandas as pd
import json

print("\n" + "="*100)
print("DETAILED DATA STRUCTURE ANALYSIS")
print("="*100)

# Analyze the main consolidated file to understand the complete structure
file_path = r"D:\Heavy\01. 2023 _ Jan-Sept _ S_OP Oct-Dec.xlsx"

try:
    # Product-Item list
    print("\n\n--- PRODUCT TABLE STRUCTURE ---")
    df_product = pd.read_excel(file_path, sheet_name='Product-Item list', header=0)
    print(f"Total Products: {len(df_product)}")
    print("\nSample Product Data:")
    print(df_product.head(10).to_string())

    # Customer list
    print("\n\n--- CUSTOMER TABLE STRUCTURE ---")
    df_customer = pd.read_excel(file_path, sheet_name='Customer list', header=0)
    print(f"Total Customers: {len(df_customer)}")
    print("\nSample Customer Data:")
    print(df_customer.head(10).to_string())

    # User list
    print("\n\n--- USER TABLE STRUCTURE ---")
    df_user = pd.read_excel(file_path, sheet_name='User list', header=0)
    print(f"Total Users: {len(df_user)}")
    print("\nUser List:")
    print(df_user.to_string())

    # Sales data
    print("\n\n--- SALES DATA STRUCTURE ---")
    df_sales = pd.read_excel(file_path, sheet_name='Sales', header=3)
    print(f"Total Sales Records: {len(df_sales)}")
    print("\nSales Columns:")
    for col in df_sales.columns:
        print(f"  - {col}")
    print("\nSample Sales Data:")
    print(df_sales.head(5).to_string())

    # Item x Customer matrix
    print("\n\n--- ITEM x CUSTOMER ACTIVATION MATRIX ---")
    df_matrix = pd.read_excel(file_path, sheet_name='Item x Customer', header=0, nrows=20)
    print(f"Matrix Shape: {df_matrix.shape}")
    print("\nSample Matrix (showing structure):")
    print(df_matrix.head(10).to_string())

except Exception as e:
    print(f"Error: {str(e)}")

# Analyze S&OP template from sales rep file
print("\n\n" + "="*100)
print("S&OP TEMPLATE STRUCTURE (Sales Rep File)")
print("="*100)

file_path2 = r"D:\Heavy\Consolidated Master File SOP_Nov25 - JR.xlsx"
try:
    xl_file = pd.ExcelFile(file_path2)
    print(f"\nSheets in Sales Rep Template: {xl_file.sheet_names}")

    # Analyze the first sheet
    df_sop = pd.read_excel(file_path2, sheet_name=0, header=None, nrows=30)
    print(f"\nS&OP Template Structure:")
    print(df_sop.to_string())

except Exception as e:
    print(f"Error: {str(e)}")

print("\n\n" + "="*100)
print("ANALYSIS COMPLETE - Ready for Database Design")
print("="*100)
