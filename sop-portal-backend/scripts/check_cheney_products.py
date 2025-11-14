"""
Check Cheney Brothers customer and their products
"""
import asyncio
import os
from motor.motor_asyncio import AsyncIOMotorClient
from dotenv import load_dotenv

load_dotenv()

async def check_cheney():
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
    print("CHECKING CHENEY BROTHERS")
    print("="*60)
    
    # Find Cheney Brothers customer
    cheney_customer = await db.customers.find_one({
        "customerName": {"$regex": "Cheney", "$options": "i"}
    })
    
    if cheney_customer:
        print(f"\n✓ Customer found:")
        print(f"  ID: {cheney_customer.get('customerId')}")
        print(f"  Name: {cheney_customer.get('customerName')}")
        print(f"  Active: {cheney_customer.get('isActive', True)}")
    else:
        print("\n✗ Cheney Brothers customer NOT found!")
        # List some customers to see what's there
        print("\nSample customers:")
        customers = await db.customers.find({}).limit(10).to_list(length=10)
        for c in customers:
            print(f"  - {c.get('customerName')} ({c.get('customerId')})")
    
    # Check matrix entries for Cheney
    if cheney_customer:
        customer_id = cheney_customer.get('customerId')
        matrix_entries = await db.product_customer_matrix.find({
            "customerId": customer_id,
            "isActive": True
        }).to_list(length=100)
        
        print(f"\n✓ Matrix entries for Cheney Brothers: {len(matrix_entries)}")
        print("\nProduct IDs in matrix:")
        product_ids = [e.get('productId') for e in matrix_entries]
        unique_ids = list(set(product_ids))
        print(f"  Unique product IDs: {len(unique_ids)}")
        
        # Show sample
        print("\nSample entries:")
        for entry in matrix_entries[:10]:
            print(f"  Product ID: {entry.get('productId')} | Code: {entry.get('productCode')} | Desc: {entry.get('productDescription', '')[:50]}")
        
        # Check if these product IDs match actual products
        print("\nChecking if product IDs match actual products...")
        matching_products = await db.products.find({
            "itemCode": {"$in": product_ids[:20]}
        }).to_list(length=20)
        
        print(f"  Found {len(matching_products)} matching products:")
        for p in matching_products[:5]:
            print(f"    {p.get('itemCode')}: {p.get('itemDescription', 'N/A')[:50]}")
        
        # Expected products for Cheney
        expected = ['110010', '110023', '130037', '150006', '190001', '210011', '220004', '330030', '810009', '810010']
        print(f"\nExpected product codes for Cheney: {expected}")
        found_expected = [pid for pid in expected if pid in product_ids]
        print(f"  Found {len(found_expected)}/{len(expected)} expected products")
        if found_expected:
            print(f"  Found: {found_expected}")
        missing = [pid for pid in expected if pid not in product_ids]
        if missing:
            print(f"  Missing: {missing}")
    
    print("\n" + "="*60)
    client.close()

if __name__ == '__main__':
    asyncio.run(check_cheney())

