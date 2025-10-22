#!/usr/bin/env python3
"""
Simple test for customers list
"""
import asyncio
from app.config.database import db
from app.services.customer_service import CustomerService

async def test_list_customers():
    try:
        print("Testing list customers...")
        
        # Connect to database
        await db.connect_db()
        database = db.get_database()
        
        # Test customer service
        customer_service = CustomerService(database)
        
        # Test listing customers
        print("Listing customers...")
        result = await customer_service.list_customers(skip=0, limit=5)
        print(f"✅ Found {len(result['customers'])} customers")
        print(f"Total: {result['total']}")
        
        # Print first customer details
        if result['customers']:
            first_customer = result['customers'][0]
            print(f"First customer: {first_customer.customerId} - {first_customer.customerName}")
        
        await db.close_db()
        
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    asyncio.run(test_list_customers())
