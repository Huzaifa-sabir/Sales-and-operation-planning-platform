"""
Verify Database Import - Quick Check Script
"""
import asyncio
import os
from motor.motor_asyncio import AsyncIOMotorClient
from dotenv import load_dotenv

load_dotenv()

async def verify_import():
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
    print("DATABASE VERIFICATION")
    print("="*60)
    
    # Count customers
    customers_count = await db.customers.count_documents({})
    print(f"\nCustomers: {customers_count}")
    sample_customer = await db.customers.find_one({})
    if sample_customer:
        print(f"  Sample: {sample_customer.get('customerName', 'N/A')} (ID: {sample_customer.get('customerId', 'N/A')})")
    
    # Count products
    products_count = await db.products.count_documents({})
    print(f"\nProducts: {products_count}")
    sample_product = await db.products.find_one({})
    if sample_product:
        print(f"  Sample: {sample_product.get('itemDescription', 'N/A')} (Code: {sample_product.get('itemCode', 'N/A')})")
    
    # Count matrix entries
    matrix_count = await db.product_customer_matrix.count_documents({})
    print(f"\nProduct-Customer Matrix Entries: {matrix_count}")
    sample_matrix = await db.product_customer_matrix.find_one({})
    if sample_matrix:
        print(f"  Sample: Customer {sample_matrix.get('customerId', 'N/A')} - Product {sample_matrix.get('productId', 'N/A')}")
    
    # Count active matrix entries
    active_matrix = await db.product_customer_matrix.count_documents({'isActive': True})
    print(f"  Active entries: {active_matrix}")
    
    # Count users
    users_count = await db.users.count_documents({})
    print(f"\nUsers: {users_count}")
    admin_user = await db.users.find_one({'role': 'admin'})
    if admin_user:
        print(f"  Admin user: {admin_user.get('email', 'N/A')} ({admin_user.get('username', 'N/A')})")
    
    print("\n" + "="*60)
    print("VERIFICATION COMPLETE")
    print("="*60)
    
    client.close()

if __name__ == '__main__':
    asyncio.run(verify_import())

