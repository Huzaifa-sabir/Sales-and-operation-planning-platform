"""
Test Cheney Brothers API filtering - simulate the API call
"""
import asyncio
import os
from motor.motor_asyncio import AsyncIOMotorClient
from dotenv import load_dotenv

load_dotenv()

async def test_api():
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
    print("TESTING CHENEY BROTHERS API FILTERING")
    print("="*60)
    
    # Test customer ID variations
    customer_id_variations = ['CHENEY-BROTHERS', 'Cheney Brothers', 'CHENEY_BROTHERS']
    
    for customer_id in customer_id_variations:
        print(f"\n--- Testing customer_id: '{customer_id}' ---")
        
        # Step 1: Get matrix entries
        matrix_docs = await db.product_customer_matrix.find(
            {"customerId": customer_id, "isActive": True}
        ).to_list(length=None)
        
        print(f"  Matrix entries found: {len(matrix_docs)}")
        if matrix_docs:
            product_ids = [doc["productId"] for doc in matrix_docs]
            print(f"  Product IDs from matrix: {sorted(product_ids)[:10]}")
            
            # Step 2: Filter products
            products = await db.products.find({
                "itemCode": {"$in": product_ids},
                "isActive": True
            }).to_list(length=100)
            
            print(f"  Products found: {len(products)}")
            for p in products[:10]:
                print(f"    {p.get('itemCode')}: {p.get('itemDescription', 'N/A')[:50]}")
        else:
            print(f"  ⚠️  No matrix entries found for customer_id='{customer_id}'")
    
    # Check what customer IDs actually exist in matrix
    print("\n--- Checking actual customer IDs in matrix ---")
    distinct_customer_ids = await db.product_customer_matrix.distinct("customerId")
    cheney_ids = [cid for cid in distinct_customer_ids if 'cheney' in str(cid).lower()]
    print(f"  Customer IDs with 'cheney' in matrix: {cheney_ids}")
    
    # Check customer collection
    print("\n--- Checking customer collection ---")
    customers = await db.customers.find({
        "customerName": {"$regex": "Cheney", "$options": "i"}
    }).to_list(length=10)
    for c in customers:
        print(f"  Customer ID: '{c.get('customerId')}', Name: '{c.get('customerName')}'")
    
    print("\n" + "="*60)
    client.close()

if __name__ == '__main__':
    try:
        asyncio.run(test_api())
    except Exception as e:
        print(f"Error: {e}")
        import traceback
        traceback.print_exc()

