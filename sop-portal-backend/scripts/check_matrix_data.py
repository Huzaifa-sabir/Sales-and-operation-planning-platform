"""
Check product-customer matrix data in database
"""
import asyncio
import os
from motor.motor_asyncio import AsyncIOMotorClient
from dotenv import load_dotenv

load_dotenv()

async def check_matrix():
    mongodb_url = os.getenv('MONGODB_URL')
    if not mongodb_url:
        print("ERROR: MONGODB_URL not found")
        return
    
    client = AsyncIOMotorClient(mongodb_url)
    db_name = "sop_portal"
    if "/" in mongodb_url:
        parts = mongodb_url.split("/")
        if len(parts) > 3:
            db_part = parts[-1].split("?")[0]
            if db_part:
                db_name = db_part
    
    db = client[db_name]
    
    print("\n" + "="*60)
    print("PRODUCT-CUSTOMER MATRIX VERIFICATION")
    print("="*60)
    
    # Count matrix entries
    matrix_count = await db.product_customer_matrix.count_documents({})
    active_count = await db.product_customer_matrix.count_documents({'isActive': True})
    inactive_count = await db.product_customer_matrix.count_documents({'isActive': False})
    
    print(f"\nTotal matrix entries: {matrix_count}")
    print(f"Active entries: {active_count}")
    print(f"Inactive entries: {inactive_count}")
    
    # Get sample entries
    sample = await db.product_customer_matrix.find_one({})
    if sample:
        print(f"\nSample entry:")
        print(f"  Customer ID: {sample.get('customerId')}")
        print(f"  Customer Name: {sample.get('customerName')}")
        print(f"  Product ID: {sample.get('productId')}")
        print(f"  Product Code: {sample.get('productCode')}")
        print(f"  Product Description: {sample.get('productDescription')}")
        print(f"  Is Active: {sample.get('isActive')}")
    
    # Check unique customers in matrix
    unique_customers = await db.product_customer_matrix.distinct("customerId")
    print(f"\nUnique customers in matrix: {len(unique_customers)}")
    
    # Check unique products in matrix
    unique_products = await db.product_customer_matrix.distinct("productId")
    print(f"Unique products in matrix: {len(unique_products)}")
    
    # Check a specific customer (e.g., look for "Cheney" or similar)
    cheney_matrix = await db.product_customer_matrix.find({
        "customerName": {"$regex": "Cheney", "$options": "i"}
    }).to_list(length=10)
    
    if cheney_matrix:
        print(f"\nFound {len(cheney_matrix)} entries for 'Cheney' customers:")
        for entry in cheney_matrix[:5]:
            print(f"  {entry.get('customerName')} - {entry.get('productCode')} ({'Active' if entry.get('isActive') else 'Inactive'})")
    
    # Check customer IDs match
    print(f"\nChecking customer ID consistency...")
    customers_in_matrix = set(unique_customers)
    customers_in_db = await db.customers.distinct("customerId")
    customers_in_db_set = set(customers_in_db)
    
    missing_in_matrix = customers_in_db_set - customers_in_matrix
    missing_in_db = customers_in_matrix - customers_in_db_set
    
    if missing_in_matrix:
        print(f"  Customers in DB but not in matrix: {len(missing_in_matrix)}")
        print(f"  Sample: {list(missing_in_matrix)[:5]}")
    
    if missing_in_db:
        print(f"  Customer IDs in matrix but not in customers collection: {len(missing_in_db)}")
        print(f"  Sample: {list(missing_in_db)[:5]}")
    
    if not missing_in_matrix and not missing_in_db:
        print("  ✓ All customer IDs match correctly")
    
    print("\n" + "="*60)
    
    client.close()

if __name__ == '__main__':
    asyncio.run(check_matrix())

