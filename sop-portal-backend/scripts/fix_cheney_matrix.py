"""
Fix Cheney Brothers matrix - deactivate all wrong entries, keep only the 10 correct ones
"""
import asyncio
import os
from motor.motor_asyncio import AsyncIOMotorClient
from dotenv import load_dotenv
from datetime import datetime, timezone

load_dotenv()

# Cheney Brothers correct active products
CHENEY_CORRECT_PRODUCTS = [
    '110010',  # Peeled Garlic 4x5 LB Garland #2
    '110023',  # Peeled Garlic 4x5lb Cheney
    '130037',  # Roasted Garlic Cheney 4x5lbs
    '150006',  # Fresh Garlic 30 LB Arg 6 White
    '190001',  # Black Garlic 10x15 CT
    '210011',  # Fresh Shallots 4x5lb
    '220004',  # Peeled Shallots 4x5lb Cheney
    '330030',  # Minced Garlic 6x32 Oz - CHENEY
    '810009',  # Fresh Turmeric 10lb
    '810010',  # Fresh Ginger 20lb
]

async def fix_cheney_matrix():
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
    print("FIXING CHENEY BROTHERS MATRIX")
    print("="*60)
    
    # Find Cheney Brothers customer
    cheney_customer = await db.customers.find_one({
        "customerName": {"$regex": "Cheney", "$options": "i"}
    })
    
    if not cheney_customer:
        print("\n✗ Cheney Brothers customer NOT found!")
        client.close()
        return
    
    customer_id = cheney_customer.get('customerId')
    customer_name = cheney_customer.get('customerName')
    
    print(f"\n✓ Found customer: {customer_name} (ID: {customer_id})")
    
    # Get all matrix entries for Cheney Brothers
    all_entries = await db.product_customer_matrix.find({
        'customerId': customer_id
    }).to_list(length=1000)
    
    print(f"\n✓ Found {len(all_entries)} total matrix entries for Cheney Brothers")
    
    now = datetime.now(timezone.utc)
    deactivated_count = 0
    activated_count = 0
    
    # Process all entries
    for entry in all_entries:
        product_id = entry.get('productId')
        is_correct = product_id in CHENEY_CORRECT_PRODUCTS
        
        if is_correct:
            # Activate correct products
            if not entry.get('isActive', True):
                await db.product_customer_matrix.update_one(
                    {'_id': entry['_id']},
                    {'$set': {'isActive': True, 'updatedAt': now}}
                )
                activated_count += 1
                print(f"  ✓ Activated: {product_id}")
        else:
            # Deactivate wrong products
            if entry.get('isActive', True):
                await db.product_customer_matrix.update_one(
                    {'_id': entry['_id']},
                    {'$set': {'isActive': False, 'updatedAt': now}}
                )
                deactivated_count += 1
                print(f"  ✗ Deactivated: {product_id} - {entry.get('productDescription', 'N/A')[:50]}")
    
    print("\n" + "="*60)
    print(f"COMPLETE:")
    print(f"  Activated: {activated_count} correct products")
    print(f"  Deactivated: {deactivated_count} wrong products")
    print("="*60)
    
    # Verify final state
    active_entries = await db.product_customer_matrix.find({
        'customerId': customer_id,
        'isActive': True
    }).to_list(length=100)
    
    print(f"\n✓ Final active products for Cheney Brothers: {len(active_entries)}")
    active_product_ids = [e.get('productId') for e in active_entries]
    print(f"  Active product IDs: {sorted(active_product_ids)}")
    
    # Check if all correct products are active
    missing = [pid for pid in CHENEY_CORRECT_PRODUCTS if pid not in active_product_ids]
    if missing:
        print(f"\n  ⚠️  Missing products: {missing}")
    else:
        print(f"\n  ✓ All 10 correct products are active!")
    
    # Check for any wrong active products
    wrong_active = [pid for pid in active_product_ids if pid not in CHENEY_CORRECT_PRODUCTS]
    if wrong_active:
        print(f"\n  ⚠️  Wrong active products (should be deactivated): {wrong_active[:10]}")
    else:
        print(f"\n  ✓ No wrong products are active!")
    
    client.close()

if __name__ == '__main__':
    asyncio.run(fix_cheney_matrix())

