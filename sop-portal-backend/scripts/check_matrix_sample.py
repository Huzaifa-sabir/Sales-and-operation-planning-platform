"""
Check actual matrix entries in database to see product IDs
"""
import asyncio
import os
from motor.motor_asyncio import AsyncIOMotorClient
from dotenv import load_dotenv

load_dotenv()

async def check_sample():
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
    
    # Check Cheney Brothers entries
    cheney_entries = await db.product_customer_matrix.find({
        "customerName": {"$regex": "Cheney", "$options": "i"}
    }).limit(10).to_list(length=10)
    
    print(f"\nFound {len(cheney_entries)} Cheney Brothers entries (sample of 10):")
    for entry in cheney_entries:
        print(f"  Product ID: {entry.get('productId')} | Code: {entry.get('productCode')} | Desc: {entry.get('productDescription')[:50] if entry.get('productDescription') else 'N/A'}")
    
    # Check if product IDs match actual product item codes
    print(f"\nChecking if product IDs match actual products...")
    product_ids = [e['productId'] for e in cheney_entries]
    products = await db.products.find({
        "itemCode": {"$in": product_ids}
    }).to_list(length=20)
    
    print(f"  Found {len(products)} matching products:")
    for p in products[:5]:
        print(f"    {p.get('itemCode')}: {p.get('itemDescription', 'N/A')[:50]}")
    
    # Check products that DON'T match
    all_product_codes = await db.products.distinct("itemCode")
    mismatched = [pid for pid in product_ids if pid not in all_product_codes]
    if mismatched:
        print(f"\n  ⚠️  Product IDs in matrix that DON'T match products: {mismatched[:10]}")
    
    client.close()

if __name__ == '__main__':
    asyncio.run(check_sample())

