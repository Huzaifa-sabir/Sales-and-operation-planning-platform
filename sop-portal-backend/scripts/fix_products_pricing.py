"""
Fix existing products in database - add missing avgPrice field
"""
import asyncio
import os
from motor.motor_asyncio import AsyncIOMotorClient
from dotenv import load_dotenv

load_dotenv()

async def fix_products():
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
    products_collection = db.products
    
    print("\n=== Fixing Products ===")
    
    # Find all products with pricing that doesn't have avgPrice
    products_to_fix = []
    async for product in products_collection.find({}):
        pricing = product.get('pricing')
        if pricing:
            if 'avgPrice' not in pricing or pricing.get('avgPrice') is None:
                products_to_fix.append(product)
    
    print(f"Found {len(products_to_fix)} products to fix")
    
    fixed_count = 0
    for product in products_to_fix:
        try:
            update_data = {}
            
            # Fix pricing structure
            pricing = product.get('pricing', {})
            if isinstance(pricing, dict):
                # If basePrice exists but avgPrice doesn't, use basePrice as avgPrice
                if 'basePrice' in pricing and pricing.get('basePrice') is not None:
                    update_data['pricing.avgPrice'] = float(pricing.get('basePrice'))
                elif 'avgPrice' not in pricing or pricing.get('avgPrice') is None:
                    update_data['pricing.avgPrice'] = 0.0
                
                # Ensure currency exists
                if 'currency' not in pricing:
                    update_data['pricing.currency'] = 'USD'
                
                # Rename basePrice to costPrice if it exists and we're using it as avgPrice
                if 'basePrice' in pricing and pricing.get('basePrice') is not None:
                    # Don't rename, just ensure avgPrice exists
                    pass
            else:
                # If pricing is None or not a dict, create new structure
                update_data['pricing'] = {
                    'avgPrice': 0.0,
                    'costPrice': None,
                    'currency': 'USD'
                }
            
            if update_data:
                await products_collection.update_one(
                    {'_id': product['_id']},
                    {'$set': update_data}
                )
                fixed_count += 1
        except Exception as e:
            print(f"Error fixing product {product.get('itemCode', 'unknown')}: {str(e)}")
    
    print(f"Fixed {fixed_count} products")
    
    # Verify fix
    still_broken = []
    async for product in products_collection.find({}):
        pricing = product.get('pricing')
        if pricing and isinstance(pricing, dict):
            if 'avgPrice' not in pricing or pricing.get('avgPrice') is None:
                still_broken.append(product.get('itemCode', 'unknown'))
    
    if still_broken:
        print(f"Warning: {len(still_broken)} products still have issues")
        print(f"First 10: {still_broken[:10]}")
    else:
        print("All products fixed successfully!")
    
    client.close()

if __name__ == '__main__':
    asyncio.run(fix_products())

