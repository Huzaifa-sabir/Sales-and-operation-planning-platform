"""
Test Sales History Endpoints and Verify Filtering
"""
import asyncio
import os
import sys
from motor.motor_asyncio import AsyncIOMotorClient
from bson import ObjectId
from dotenv import load_dotenv

load_dotenv()

async def test_sales_history():
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
    print("SALES HISTORY ENDPOINT TESTING")
    print("="*60)
    
    # Get a sample customer ID from customers collection
    customer = await db.customers.find_one({})
    if customer:
        customer_id = customer.get('customerId')
        print(f"\nTesting with customer: {customer.get('customerName')} (ID: {customer_id})")
        
        # Test filtering by customer ID
        count = await db.sales_history.count_documents({"customerId": customer_id})
        print(f"Sales records for customer '{customer_id}': {count}")
        
        # Also check if there are any records with customerName matching
        count_by_name = await db.sales_history.count_documents({"customerName": customer.get('customerName')})
        print(f"Sales records for customer name '{customer.get('customerName')}': {count_by_name}")
    
    # Get a sample product
    product = await db.products.find_one({})
    if product:
        product_code = product.get('itemCode')
        print(f"\nTesting with product: {product.get('itemDescription')} (Code: {product_code})")
        
        # Test filtering by product code
        count = await db.sales_history.count_documents({"productId": product_code})
        print(f"Sales records for product '{product_code}': {count}")
        
        # Also check by productCode field
        count_by_code = await db.sales_history.count_documents({"productCode": product_code})
        print(f"Sales records for productCode '{product_code}': {count_by_code}")
    
    # Check what fields are used in sales_history
    sample = await db.sales_history.find_one({})
    if sample:
        print(f"\nSales History Record Structure:")
        print(f"  customerId: {sample.get('customerId')} (type: {type(sample.get('customerId')).__name__})")
        print(f"  customerName: {sample.get('customerName')}")
        print(f"  productId: {sample.get('productId')} (type: {type(sample.get('productId')).__name__})")
        print(f"  productCode: {sample.get('productCode')}")
    
    # Check if we need to link sales_history to customers/products by name
    all_customers = await db.customers.find({}).to_list(length=10)
    all_sales = await db.sales_history.find({}).to_list(length=10)
    
    print(f"\nSample customer IDs in customers collection:")
    for c in all_customers[:5]:
        print(f"  {c.get('customerId')} - {c.get('customerName')}")
    
    print(f"\nSample customer IDs in sales_history collection:")
    for s in all_sales[:5]:
        print(f"  {s.get('customerId')} - {s.get('customerName')}")
    
    print("\n" + "="*60)
    
    client.close()

if __name__ == '__main__':
    asyncio.run(test_sales_history())

