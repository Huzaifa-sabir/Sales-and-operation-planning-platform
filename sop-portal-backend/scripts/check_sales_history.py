"""
Check Sales History Data and Test Endpoints
"""
import asyncio
import os
from motor.motor_asyncio import AsyncIOMotorClient
from dotenv import load_dotenv

load_dotenv()

async def check_sales_history():
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
    print("SALES HISTORY VERIFICATION")
    print("="*60)
    
    # Count sales history
    count = await db.sales_history.count_documents({})
    print(f"\nSales History Records: {count}")
    
    if count > 0:
        sample = await db.sales_history.find_one({})
        print(f"\nSample record fields:")
        for key, value in sample.items():
            if key != '_id':
                print(f"  {key}: {type(value).__name__} = {str(value)[:50]}")
        
        # Check unique customers
        customers = await db.sales_history.distinct("customerId")
        print(f"\nUnique customers in sales history: {len(customers)}")
        
        # Check unique products
        products = await db.sales_history.distinct("productId")
        print(f"Unique products in sales history: {len(products)}")
        
        # Check year/month range
        years = await db.sales_history.distinct("year")
        months = await db.sales_history.distinct("month")
        print(f"Year range: {min(years) if years else 'N/A'} - {max(years) if years else 'N/A'}")
        print(f"Months: {sorted(set(months)) if months else 'N/A'}")
    else:
        print("\n⚠️  WARNING: No sales history records found!")
        print("   Sales history data needs to be imported from Excel files")
    
    print("\n" + "="*60)
    
    client.close()

if __name__ == '__main__':
    asyncio.run(check_sales_history())

