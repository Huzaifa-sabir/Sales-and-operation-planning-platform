#!/usr/bin/env python3
"""
Debug conversion issue
"""
import asyncio
from app.config.database import db
from app.services.customer_service import CustomerService
from app.models.customer import CustomerInDB

async def test_conversion_debug():
    try:
        print("Testing conversion debug...")
        
        # Connect to database
        await db.connect_db()
        database = db.get_database()
        
        # Test customer service
        customer_service = CustomerService(database)
        
        # Get customers
        print("1. Getting customers...")
        result = await customer_service.list_customers(skip=0, limit=5)
        print(f"✅ Got {len(result['customers'])} customers")
        
        # Test conversion to dict format (like export does)
        print("2. Testing conversion to dict format...")
        customers_data = []
        for c in result["customers"]:
            try:
                customer_dict = {
                    "customerId": c.customerId,
                    "customerName": c.customerName,
                    "contactPerson": c.contactPerson,
                    "contactEmail": c.contactEmail,
                    "contactPhone": c.contactPhone,
                    "location": c.location.model_dump() if c.location else None,
                    "paymentTerms": getattr(c, 'paymentTerms', None),
                    "creditLimit": getattr(c, 'creditLimit', None),
                    "isActive": c.isActive,
                    "createdAt": c.createdAt
                }
                customers_data.append(customer_dict)
                print(f"✅ Converted customer: {c.customerId}")
            except Exception as e:
                print(f"❌ Failed to convert customer {c.customerId}: {e}")
                import traceback
                traceback.print_exc()
        
        print(f"✅ Successfully converted {len(customers_data)} customers")
        
        await db.close_db()
        
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    asyncio.run(test_conversion_debug())

