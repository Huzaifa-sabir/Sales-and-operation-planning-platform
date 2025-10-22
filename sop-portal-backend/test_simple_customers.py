#!/usr/bin/env python3
"""
Simple test for customers API
"""
import asyncio
from app.config.database import db
from app.services.customer_service import CustomerService
from app.models.customer import CustomerCreate, CustomerLocation

async def test_customer_service():
    try:
        print("Testing customer service directly...")
        
        # Connect to database
        await db.connect_db()
        database = db.get_database()
        
        # Test customer service
        customer_service = CustomerService(database)
        
        # Test creating a customer
        customer_data = CustomerCreate(
            customerId="TEST-001",
            customerName="Test Customer",
            salesRepId="default-rep",
            salesRepName="Default Sales Rep",
            location=CustomerLocation(
                city="Test City",
                state="TS",
                address="123 Test St",
                zipCode="12345",
                country="USA"
            ),
            contactPerson="Test Person"
        )
        
        print("Creating customer...")
        result = await customer_service.create_customer(customer_data)
        print(f"✅ Customer created successfully: {result.customerId}")
        
        # Test listing customers
        print("Listing customers...")
        customers = await customer_service.list_customers(skip=0, limit=10)
        print(f"✅ Found {len(customers['customers'])} customers")
        
        await db.close_db()
        
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    asyncio.run(test_customer_service())
