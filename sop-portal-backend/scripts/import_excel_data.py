"""
Comprehensive Excel Data Import Script
Extracts customers, products, product-customer matrix, and sales history from Excel files
"""
import pandas as pd
import asyncio
from typing import Dict, List, Set, Optional
from datetime import datetime
from motor.motor_asyncio import AsyncIOMotorClient
from bson import ObjectId
import os
import sys
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from app.config.database import Database
from app.models.customer import CustomerCreate, CustomerLocation
from app.models.product import ProductCreate, ProductGroup, ProductManufacturing, ProductPricing
from app.models.product_customer_matrix import ProductCustomerMatrixCreate
from app.models.sales_history import SalesHistoryCreate


class ExcelDataImporter:
    """Imports all data from Excel consolidated files"""
    
    def __init__(self, db):
        self.db = db
        self.customers_collection = db.customers
        self.products_collection = db.products
        self.matrix_collection = db.productCustomerMatrix
        self.sales_history_collection = db.sales_history
        self.users_collection = db.users
        
        # Tracking
        self.stats = {
            'customers_created': 0,
            'customers_updated': 0,
            'products_created': 0,
            'products_updated': 0,
            'matrix_entries_created': 0,
            'sales_history_created': 0,
            'errors': []
        }
    
    def extract_customers_from_excel(self, excel_file: str, sales_rep_mapping: Dict[str, str]) -> List[Dict]:
        """Extract customers from Excel sheet names"""
        xl = pd.ExcelFile(excel_file)
        
        # System sheets to skip
        system_sheets = ['Budget', 'Sheet1', 'Summary', 'Full Harvest']
        customer_sheets = [s for s in xl.sheet_names if s not in system_sheets]
        
        customers = []
        for sheet_name in customer_sheets:
            # Extract customer name from sheet name
            customer_name = sheet_name.strip()
            
            # Try to find sales rep from filename or mapping
            sales_rep_name = "Unknown"
            sales_rep_id = None
            
            # Check if filename contains sales rep name (e.g., "Consolidated Master File SOP_Nov25 - JR.xlsx")
            if "JR" in excel_file or "Jr" in excel_file:
                sales_rep_name = "JR"
            elif "ANTHONY" in excel_file:
                sales_rep_name = "Anthony"
            elif "RANDELL" in excel_file:
                sales_rep_name = "Randell"
            elif "Mario" in excel_file:
                sales_rep_name = "Mario"
            elif "DB" in excel_file:
                sales_rep_name = "DB"
            elif "PG" in excel_file:
                sales_rep_name = "PG"
            elif "Keith" in excel_file:
                sales_rep_name = "Keith"
            
            # Check mapping
            if customer_name in sales_rep_mapping:
                sales_rep_name = sales_rep_mapping[customer_name]
            
            # Generate customer ID from name
            customer_id = customer_name.upper().replace(' ', '-').replace("'", '').replace('.', '')[:20]
            
            customers.append({
                'customerId': customer_id,
                'customerName': customer_name,
                'sopCustomerName': customer_name,
                'salesRepName': sales_rep_name,
                'salesRepId': sales_rep_id,  # Will be resolved later
                'location': CustomerLocation(),
                'isActive': True
            })
        
        return customers
    
    def extract_products_from_excel(self, excel_file: str) -> List[Dict]:
        """Extract unique products from all customer sheets"""
        xl = pd.ExcelFile(excel_file)
        system_sheets = ['Budget', 'Sheet1', 'Summary', 'Full Harvest']
        customer_sheets = [s for s in xl.sheet_names if s not in system_sheets]
        
        products_seen = {}  # itemCode -> product data
        
        for sheet_name in customer_sheets:
            try:
                # Read sheet starting from row 6 (0-indexed = 6)
                df = pd.read_excel(excel_file, sheet_name=sheet_name, header=None, skiprows=6)
                
                # Expected columns: [0: '#', 1: 'Group', 2: 'ITEM CODE', 3: 'DESCRIPTION', ...]
                for idx, row in df.iterrows():
                    if pd.isna(row.iloc[2]) or pd.isna(row.iloc[3]):  # Skip if no item code or description
                        continue
                    
                    item_code = str(int(row.iloc[2])) if pd.notna(row.iloc[2]) else None
                    description = str(row.iloc[3]).strip() if pd.notna(row.iloc[3]) else None
                    group_category = str(row.iloc[1]).strip() if pd.notna(row.iloc[1]) else None
                    
                    if not item_code or not description:
                        continue
                    
                    # Parse group category (e.g., "G01 - Garlic Production")
                    group_code = None
                    group_name = None
                    if group_category:
                        parts = group_category.split(' - ')
                        if len(parts) >= 1:
                            group_code = parts[0].strip()
                        if len(parts) >= 2:
                            group_name = parts[1].strip()
                    
                    # Store product if not seen before
                    if item_code not in products_seen:
                        products_seen[item_code] = {
                            'itemCode': item_code,
                            'itemDescription': description,
                            'group': ProductGroup(
                                code=group_code or 'UNKNOWN',
                                desc=group_name or 'Unknown'
                            ) if group_code else None,
                            'manufacturing': ProductManufacturing(
                                location='Miami',  # Default
                                line=None
                            ),
                            'isActive': True
                        }
            except Exception as e:
                self.stats['errors'].append(f"Error processing sheet {sheet_name}: {str(e)}")
        
        return list(products_seen.values())
    
    def extract_matrix_from_excel(self, excel_file: str, customer_map: Dict[str, str]) -> List[Dict]:
        """Extract product-customer matrix from Excel"""
        xl = pd.ExcelFile(excel_file)
        system_sheets = ['Budget', 'Sheet1', 'Summary', 'Full Harvest']
        customer_sheets = [s for s in xl.sheet_names if s not in system_sheets]
        
        matrix_entries = []
        
        for sheet_name in customer_sheets:
            customer_id = customer_map.get(sheet_name)
            if not customer_id:
                continue
            
            try:
                df = pd.read_excel(excel_file, sheet_name=sheet_name, header=None, skiprows=6)
                
                for idx, row in df.iterrows():
                    if pd.isna(row.iloc[2]) or pd.isna(row.iloc[3]):
                        continue
                    
                    item_code = str(int(row.iloc[2])) if pd.notna(row.iloc[2]) else None
                    description = str(row.iloc[3]).strip() if pd.notna(row.iloc[3]) else None
                    
                    if not item_code or not description:
                        continue
                    
                    # Check if product has any forecast data (columns 5+)
                    has_data = False
                    for col_idx in range(5, min(len(row), 50)):  # Check first 45 columns
                        if pd.notna(row.iloc[col_idx]) and row.iloc[col_idx] != 0:
                            has_data = True
                            break
                    
                    # If product appears in customer sheet, it's active
                    matrix_entries.append({
                        'customerId': customer_id,
                        'customerName': sheet_name,
                        'productId': item_code,
                        'productCode': item_code,
                        'productDescription': description,
                        'isActive': True
                    })
            except Exception as e:
                self.stats['errors'].append(f"Error processing matrix for {sheet_name}: {str(e)}")
        
        return matrix_entries
    
    async def resolve_sales_rep_ids(self, customers: List[Dict]):
        """Resolve sales rep IDs from names"""
        # Get all unique sales rep names
        rep_names = set(c['salesRepName'] for c in customers)
        
        # Try to find existing users
        for rep_name in rep_names:
            user = await self.users_collection.find_one({
                '$or': [
                    {'fullName': {'$regex': rep_name, '$options': 'i'}},
                    {'username': {'$regex': rep_name, '$options': 'i'}},
                    {'email': {'$regex': rep_name, '$options': 'i'}}
                ]
            })
            
            if user:
                # Update all customers with this rep name
                for customer in customers:
                    if customer['salesRepName'] == rep_name:
                        customer['salesRepId'] = str(user['_id'])
            else:
                # Create a placeholder user or use default admin
                admin_user = await self.users_collection.find_one({'role': 'admin'})
                if admin_user:
                    for customer in customers:
                        if customer['salesRepName'] == rep_name:
                            customer['salesRepId'] = str(admin_user['_id'])
    
    async def import_customers(self, customers: List[Dict]):
        """Import customers into database"""
        await self.resolve_sales_rep_ids(customers)
        
        for customer_data in customers:
            try:
                # Check if customer exists
                existing = await self.customers_collection.find_one({
                    'customerId': customer_data['customerId']
                })
                
                if existing:
                    # Update existing
                    await self.customers_collection.update_one(
                        {'customerId': customer_data['customerId']},
                        {'$set': {
                            **customer_data,
                            'updatedAt': datetime.utcnow()
                        }}
                    )
                    self.stats['customers_updated'] += 1
                else:
                    # Create new
                    customer_data['createdAt'] = datetime.utcnow()
                    customer_data['updatedAt'] = datetime.utcnow()
                    await self.customers_collection.insert_one(customer_data)
                    self.stats['customers_created'] += 1
            except Exception as e:
                self.stats['errors'].append(f"Error importing customer {customer_data.get('customerId')}: {str(e)}")
    
    async def import_products(self, products: List[Dict]):
        """Import products into database"""
        for product_data in products:
            try:
                # Check if product exists
                existing = await self.products_collection.find_one({
                    'itemCode': product_data['itemCode']
                })
                
                if existing:
                    # Update existing
                    update_data = {
                        'itemDescription': product_data['itemDescription'],
                        'updatedAt': datetime.utcnow()
                    }
                    if product_data.get('group'):
                        update_data['group'] = product_data['group'].model_dump() if hasattr(product_data['group'], 'model_dump') else product_data['group']
                    if product_data.get('manufacturing'):
                        update_data['manufacturing'] = product_data['manufacturing'].model_dump() if hasattr(product_data['manufacturing'], 'model_dump') else product_data['manufacturing']
                    
                    await self.products_collection.update_one(
                        {'itemCode': product_data['itemCode']},
                        {'$set': update_data}
                    )
                    self.stats['products_updated'] += 1
                else:
                    # Create new
                    product_data['createdAt'] = datetime.utcnow()
                    product_data['updatedAt'] = datetime.utcnow()
                    # Convert Pydantic models to dict
                    if 'group' in product_data and hasattr(product_data['group'], 'model_dump'):
                        product_data['group'] = product_data['group'].model_dump()
                    if 'manufacturing' in product_data and hasattr(product_data['manufacturing'], 'model_dump'):
                        product_data['manufacturing'] = product_data['manufacturing'].model_dump()
                    await self.products_collection.insert_one(product_data)
                    self.stats['products_created'] += 1
            except Exception as e:
                self.stats['errors'].append(f"Error importing product {product_data.get('itemCode')}: {str(e)}")
    
    async def import_matrix(self, matrix_entries: List[Dict]):
        """Import product-customer matrix"""
        for entry in matrix_entries:
            try:
                # Check if entry exists
                existing = await self.matrix_collection.find_one({
                    'customerId': entry['customerId'],
                    'productId': entry['productId']
                })
                
                if existing:
                    # Update existing
                    await self.matrix_collection.update_one(
                        {'customerId': entry['customerId'], 'productId': entry['productId']},
                        {'$set': {
                            **entry,
                            'updatedAt': datetime.utcnow()
                        }}
                    )
                else:
                    # Create new
                    entry['createdAt'] = datetime.utcnow()
                    entry['updatedAt'] = datetime.utcnow()
                    await self.matrix_collection.insert_one(entry)
                    self.stats['matrix_entries_created'] += 1
            except Exception as e:
                self.stats['errors'].append(f"Error importing matrix entry {entry.get('customerId')}/{entry.get('productId')}: {str(e)}")
    
    async def import_all_from_file(self, excel_file: str, sales_rep_mapping: Optional[Dict[str, str]] = None):
        """Import all data from Excel file"""
        if sales_rep_mapping is None:
            sales_rep_mapping = {}
        
        print(f"\n=== Importing from {excel_file} ===")
        
        # Extract data
        print("Extracting customers...")
        customers = self.extract_customers_from_excel(excel_file, sales_rep_mapping)
        print(f"Found {len(customers)} customers")
        
        print("Extracting products...")
        products = self.extract_products_from_excel(excel_file)
        print(f"Found {len(products)} unique products")
        
        # Import customers first (needed for matrix)
        print("Importing customers...")
        await self.import_customers(customers)
        
        # Create customer map for matrix
        customer_map = {c['customerName']: c['customerId'] for c in customers}
        
        print("Extracting product-customer matrix...")
        matrix_entries = self.extract_matrix_from_excel(excel_file, customer_map)
        print(f"Found {len(matrix_entries)} matrix entries")
        
        print("Importing products...")
        await self.import_products(products)
        
        print("Importing product-customer matrix...")
        await self.import_matrix(matrix_entries)
        
        print("\n=== Import Summary ===")
        print(f"Customers created: {self.stats['customers_created']}")
        print(f"Customers updated: {self.stats['customers_updated']}")
        print(f"Products created: {self.stats['products_created']}")
        print(f"Products updated: {self.stats['products_updated']}")
        print(f"Matrix entries created: {self.stats['matrix_entries_created']}")
        print(f"Errors: {len(self.stats['errors'])}")
        if self.stats['errors']:
            print("\nErrors:")
            for error in self.stats['errors'][:10]:  # Show first 10
                print(f"  - {error}")


async def main():
    """Main import function"""
    import os
    from dotenv import load_dotenv
    
    load_dotenv()
    
    # Get MongoDB URL
    mongodb_url = os.getenv('MONGODB_URL')
    if not mongodb_url:
        print("Error: MONGODB_URL not found in environment")
        return
    
    # Connect to database
    client = AsyncIOMotorClient(mongodb_url)
    db_name = mongodb_url.split('/')[-1].split('?')[0]
    db = client[db_name]
    
    # Initialize importer
    importer = ExcelDataImporter(db)
    
    # Find all Excel files
    excel_files = [
        'Consolidated Master File SOP_Nov25 - JR.xlsx',
        'Consolidated Master File SOP_Nov25 - ANTHONY.xlsx',
        'Consolidated Master File SOP_Nov25 - RANDELL.xlsx',
        'Consolidated Master File SOP_Nov25 - Mario Jr.xlsx',
        'Consolidated Master File SOP_Nov25 - Mario Sr.xlsx',
        'Consolidated Master File SOP_Nov25 - DB.xlsx',
        'Consolidated Master File SOP_Nov25 - PG.xlsx',
        'Consolidated Master File SOP_Nov25 Keith JC.xlsx',
    ]
    
    # Filter to existing files
    existing_files = [f for f in excel_files if os.path.exists(f)]
    
    if not existing_files:
        print("No Excel files found!")
        return
    
    print(f"Found {len(existing_files)} Excel files to import")
    
    # Import each file
    for excel_file in existing_files:
        await importer.import_all_from_file(excel_file)
    
    print("\n=== Final Summary ===")
    print(f"Total customers created: {importer.stats['customers_created']}")
    print(f"Total customers updated: {importer.stats['customers_updated']}")
    print(f"Total products created: {importer.stats['products_created']}")
    print(f"Total products updated: {importer.stats['products_updated']}")
    print(f"Total matrix entries created: {importer.stats['matrix_entries_created']}")
    print(f"Total errors: {len(importer.stats['errors'])}")
    
    client.close()


if __name__ == '__main__':
    asyncio.run(main())

