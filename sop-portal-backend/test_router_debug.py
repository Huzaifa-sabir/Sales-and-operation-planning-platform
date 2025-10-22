#!/usr/bin/env python3
"""
Debug router issue
"""
import asyncio
from app.config.database import db
from app.services.customer_service import CustomerService
from app.services.excel_service import ExcelService
from fastapi.responses import StreamingResponse
from datetime import datetime

async def test_router_debug():
    try:
        print("Testing router debug...")
        
        # Connect to database
        await db.connect_db()
        database = db.get_database()
        
        # Test customer service
        customer_service = CustomerService(database)
        
        # Get all customers (like export does)
        print("1. Getting all customers...")
        result = await customer_service.list_customers(
            skip=0,
            limit=10000,  # Get all
            is_active=None
        )
        print(f"✅ Got {len(result['customers'])} customers")
        
        # Convert to dict format (like export does)
        print("2. Converting to dict format...")
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
            except Exception as e:
                print(f"❌ Failed to convert customer {c.customerId}: {e}")
                import traceback
                traceback.print_exc()
                break
        
        print(f"✅ Converted {len(customers_data)} customers")
        
        # Test Excel generation
        print("3. Testing Excel generation...")
        try:
            excel_file = ExcelService.export_customers(customers_data)
            print(f"✅ Excel generation successful - Size: {len(excel_file.getvalue())} bytes")
        except Exception as e:
            print(f"❌ Excel generation failed: {e}")
            import traceback
            traceback.print_exc()
            return
        
        # Test StreamingResponse
        print("4. Testing StreamingResponse...")
        try:
            response = StreamingResponse(
                excel_file,
                media_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
                headers={
                    "Content-Disposition": f"attachment; filename=customers_export_{datetime.now().strftime('%Y%m%d_%H%M%S')}.xlsx"
                }
            )
            print("✅ StreamingResponse created successfully")
        except Exception as e:
            print(f"❌ StreamingResponse creation failed: {e}")
            import traceback
            traceback.print_exc()
        
        await db.close_db()
        
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    asyncio.run(test_router_debug())