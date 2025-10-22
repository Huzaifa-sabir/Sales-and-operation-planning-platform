#!/usr/bin/env python3
"""
Debug export issue
"""
import asyncio
from app.config.database import db
from app.services.customer_service import CustomerService

async def test_export_debug():
    try:
        print("Testing export debug...")
        
        # Connect to database
        await db.connect_db()
        database = db.get_database()
        
        # Test customer service
        customer_service = CustomerService(database)
        
        # Test listing customers with small limit first
        print("1. Testing list_customers with limit 5...")
        result = await customer_service.list_customers(skip=0, limit=5)
        print(f"✅ Small limit works - Found {len(result['customers'])} customers")
        
        # Test with larger limit
        print("2. Testing list_customers with limit 100...")
        result = await customer_service.list_customers(skip=0, limit=100)
        print(f"✅ Medium limit works - Found {len(result['customers'])} customers")
        
        # Test with very large limit (like export does)
        print("3. Testing list_customers with limit 10000...")
        result = await customer_service.list_customers(skip=0, limit=10000)
        print(f"✅ Large limit works - Found {len(result['customers'])} customers")
        
        await db.close_db()
        
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    asyncio.run(test_export_debug())
