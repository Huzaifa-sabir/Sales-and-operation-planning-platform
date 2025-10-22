import pandas as pd

print("="*80)
print("QUICK DATA STRUCTURE ANALYSIS")
print("="*80)

file_path = r"D:\Heavy\01. 2023 _ Jan-Sept _ S_OP Oct-Dec.xlsx"

# Product list
print("\n--- PRODUCT TABLE ---")
df_product = pd.read_excel(file_path, sheet_name='Product-Item list', header=0, nrows=5)
print("Columns:", list(df_product.columns))
print("\nSample:")
print(df_product.head())

# Customer list
print("\n--- CUSTOMER TABLE ---")
df_customer = pd.read_excel(file_path, sheet_name='Customer list', header=0, nrows=5)
print("Columns:", list(df_customer.columns))
print("\nSample:")
print(df_customer.head())

# User list
print("\n--- USER TABLE ---")
df_user = pd.read_excel(file_path, sheet_name='User list', header=0)
print("Columns:", list(df_user.columns))
print(f"\nTotal Users: {len(df_user)}")
print(df_user)

print("\n" + "="*80)
