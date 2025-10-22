#!/usr/bin/env python3
"""
Test ExcelService directly
"""
import asyncio
from app.config.database import db
from app.services.customer_service import CustomerService
from app.services.excel_service import ExcelService

async def test_excel_direct():
    try:
        print("Testing ExcelService directly...")
        
        # Connect to database
        await db.connect_db()
        database = db.get_database()
        
        # Test customer service
        customer_service = CustomerService(database)
        
        # Get customers
        print("1. Getting customers...")
        result = await customer_service.list_customers(skip=0, limit=5)
        print(f"✅ Got {len(result['customers'])} customers")
        
        # Convert to dict format
        print("2. Converting to dict format...")
        customers_data = []
        for c in result["customers"]:
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
        
        print(f"✅ Converted {len(customers_data)} customers")
        
        # Test Excel generation
        print("3. Testing Excel generation...")
        try:
            excel_file = ExcelService.export_customers(customers_data)
            print(f"✅ Excel generation successful - Size: {len(excel_file.getvalue())} bytes")
            
            # Test if we can read the file
            excel_file.seek(0)
            content = excel_file.read()
            print(f"✅ File content read successfully - {len(content)} bytes")
            
        except Exception as e:
            print(f"❌ Excel generation failed: {e}")
            import traceback
            traceback.print_exc()
        
        await db.close_db()
        
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    asyncio.run(test_excel_direct())
