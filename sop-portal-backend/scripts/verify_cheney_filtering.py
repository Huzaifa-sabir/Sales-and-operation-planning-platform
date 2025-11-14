"""
Verify Cheney Brothers product filtering
"""
import asyncio
import os
from motor.motor_asyncio import AsyncIOMotorClient
from dotenv import load_dotenv

load_dotenv()

async def verify():
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
    print("VERIFYING CHENEY BROTHERS FILTERING")
    print("="*60)
    
    # Check matrix entries
    matrix_entries = await db.product_customer_matrix.find({
        'customerId': 'CHENEY-BROTHERS',
        'isActive': True
    }).to_list(length=100)
    
    print(f"\n✓ Matrix entries for CHENEY-BROTHERS (isActive=True): {len(matrix_entries)}")
    product_ids_from_matrix = [m.get('productId') for m in matrix_entries]
    print(f"  Product IDs in matrix: {sorted(product_ids_from_matrix)}")
    
    # Check if products exist with these IDs
    print(f"\n✓ Checking if products exist with these itemCodes:")
    products = await db.products.find({
        'itemCode': {'$in': product_ids_from_matrix}
    }).to_list(length=100)
    
    print(f"  Found {len(products)} matching products:")
    for p in products:
        print(f"    {p.get('itemCode')}: {p.get('itemDescription', 'N/A')[:60]}")
    
    # Check products that don't exist
    found_ids = [p.get('itemCode') for p in products]
    missing_ids = [pid for pid in product_ids_from_matrix if pid not in found_ids]
    if missing_ids:
        print(f"\n  ⚠️  Product IDs in matrix but NOT in products collection: {missing_ids}")
    
    # Test the filtering logic (simulate backend)
    print(f"\n✓ Testing filtering logic:")
    matrix_docs = await db.product_customer_matrix.find(
        {"customerId": "CHENEY-BROTHERS", "isActive": True}
    ).to_list(length=None)
    
    product_ids = [doc["productId"] for doc in matrix_docs]
    print(f"  Product IDs from matrix query: {sorted(product_ids)}")
    
    if product_ids:
        filtered_products = await db.products.find({
            "itemCode": {"$in": product_ids},
            "isActive": True
        }).to_list(length=100)
        
        print(f"  Products found with filter: {len(filtered_products)}")
        for p in filtered_products:
            print(f"    {p.get('itemCode')}: {p.get('itemDescription', 'N/A')[:60]}")
    
    print("\n" + "="*60)
    client.close()

if __name__ == '__main__':
    asyncio.run(verify())

