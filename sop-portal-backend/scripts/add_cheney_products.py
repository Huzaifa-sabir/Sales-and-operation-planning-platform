"""
Add Cheney Brothers and its active products to matrix
"""
import asyncio
import os
from motor.motor_asyncio import AsyncIOMotorClient
from dotenv import load_dotenv
from datetime import datetime, timezone

load_dotenv()

# Cheney Brothers active products
CHENEY_PRODUCTS = [
    {'itemCode': '110010', 'description': 'Peeled Garlic 4x5 LB Garland #2'},
    {'itemCode': '110023', 'description': 'Peeled Garlic 4x5lb Cheney'},
    {'itemCode': '130037', 'description': 'Roasted Garlic Cheney 4x5lbs'},
    {'itemCode': '150006', 'description': 'Fresh Garlic 30 LB Arg 6 White'},
    {'itemCode': '190001', 'description': 'Black Garlic 10x15 CT'},
    {'itemCode': '210011', 'description': 'Fresh Shallots 4x5lb'},
    {'itemCode': '220004', 'description': 'Peeled Shallots 4x5lb Cheney'},
    {'itemCode': '330030', 'description': 'Minced Garlic 6x32 Oz - CHENEY'},
    {'itemCode': '810009', 'description': 'Fresh Turmeric 10lb'},
    {'itemCode': '810010', 'description': 'Fresh Ginger 20lb'},
]

async def add_cheney_products():
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
    print("ADDING CHENEY BROTHERS ACTIVE PRODUCTS")
    print("="*60)
    
    # Find Cheney Brothers customer
    cheney_customer = await db.customers.find_one({
        "customerName": {"$regex": "Cheney", "$options": "i"}
    })
    
    if not cheney_customer:
        print("\n✗ Cheney Brothers customer NOT found!")
        print("Please import customers first.")
        client.close()
        return
    
    customer_id = cheney_customer.get('customerId')
    customer_name = cheney_customer.get('customerName')
    
    print(f"\n✓ Found customer: {customer_name} (ID: {customer_id})")
    
    # Get product descriptions from products collection
    product_codes = [p['itemCode'] for p in CHENEY_PRODUCTS]
    products = await db.products.find({
        "itemCode": {"$in": product_codes}
    }).to_list(length=100)
    
    product_map = {p['itemCode']: p.get('itemDescription', '') for p in products}
    
    print(f"\n✓ Found {len(products)} products in database")
    
    # Create/update matrix entries
    now = datetime.now(timezone.utc)
    created_count = 0
    updated_count = 0
    
    for product_info in CHENEY_PRODUCTS:
        item_code = product_info['itemCode']
        description = product_info['description']
        
        # Use description from products collection if available, otherwise use provided one
        final_description = product_map.get(item_code, description)
        
        # Check if matrix entry exists
        existing = await db.product_customer_matrix.find_one({
            'customerId': customer_id,
            'productId': item_code
        })
        
        if existing:
            # Update existing entry
            await db.product_customer_matrix.update_one(
                {
                    'customerId': customer_id,
                    'productId': item_code
                },
                {
                    '$set': {
                        'customerName': customer_name,
                        'productCode': item_code,
                        'productDescription': final_description,
                        'isActive': True,
                        'updatedAt': now
                    }
                }
            )
            updated_count += 1
            print(f"  Updated: {item_code} - {final_description[:50]}")
        else:
            # Create new entry
            await db.product_customer_matrix.insert_one({
                'customerId': customer_id,
                'customerName': customer_name,
                'productId': item_code,
                'productCode': item_code,
                'productDescription': final_description,
                'isActive': True,
                'customerSpecificPrice': None,
                'lastOrderDate': None,
                'totalOrdersQty': None,
                'notes': None,
                'createdAt': now,
                'updatedAt': now
            })
            created_count += 1
            print(f"  Created: {item_code} - {final_description[:50]}")
    
    print("\n" + "="*60)
    print(f"COMPLETE: {created_count} created, {updated_count} updated")
    print("="*60)
    
    # Verify
    matrix_count = await db.product_customer_matrix.count_documents({
        'customerId': customer_id,
        'isActive': True,
        'productId': {'$in': product_codes}
    })
    print(f"\n✓ Verified: {matrix_count} active products for Cheney Brothers")
    
    client.close()

if __name__ == '__main__':
    asyncio.run(add_cheney_products())

