#!/usr/bin/env python3
"""
Check what's in the customers collection
"""
import asyncio
from app.config.database import db

async def check_customers():
    try:
        print("Checking customers collection...")
        
        # Connect to database
        await db.connect_db()
        database = db.get_database()
        
        # Get raw documents
        cursor = database.customers.find({}).limit(5)
        count = 0
        async for doc in cursor:
            count += 1
            print(f"Document {count}:")
            print(f"  _id: {doc.get('_id')}")
            print(f"  customerId: {doc.get('customerId')}")
            print(f"  customerName: {doc.get('customerName')}")
            print(f"  salesRepId: {doc.get('salesRepId', 'MISSING')}")
            print(f"  salesRepName: {doc.get('salesRepName', 'MISSING')}")
            print(f"  location: {doc.get('location')}")
            print(f"  contactPerson: {doc.get('contactPerson', 'MISSING')}")
            print(f"  paymentTerms: {doc.get('paymentTerms', 'MISSING')}")
            print(f"  creditLimit: {doc.get('creditLimit', 'MISSING')}")
            print("---")
        
        print(f"Total documents checked: {count}")
        
        await db.close_db()
        
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    asyncio.run(check_customers())
