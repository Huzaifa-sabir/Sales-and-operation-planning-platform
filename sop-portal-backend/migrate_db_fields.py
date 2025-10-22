"""
Database Migration Script
Migrates 'description' field to 'itemDescription' in products collection
"""
import asyncio
from motor.motor_asyncio import AsyncIOMotorClient

async def migrate_products():
    """Migrate product fields from 'description' to 'itemDescription'"""
    client = AsyncIOMotorClient("mongodb://localhost:27017")
    db = client.sop_portal

    # Update all products that have 'description' but not 'itemDescription'
    result = await db.products.update_many(
        {
            "description": {"$exists": True},
            "itemDescription": {"$exists": False}
        },
        [
            {
                "$set": {
                    "itemDescription": "$description"
                }
            }
        ]
    )

    print(f"OK - Migrated {result.modified_count} products: description -> itemDescription")

    client.close()

async def migrate_customers():
    """Add missing paymentTerms field to customers"""
    client = AsyncIOMotorClient("mongodb://localhost:27017")
    db = client.sop_portal

    # Update all customers that don't have paymentTerms
    result = await db.customers.update_many(
        {"paymentTerms": {"$exists": False}},
        {"$set": {"paymentTerms": "Net 30"}}  # Default payment terms
    )

    print(f"OK - Added paymentTerms to {result.modified_count} customers")

    client.close()

async def main():
    print("Starting database field migration...")
    await migrate_products()
    await migrate_customers()
    print("Migration completed successfully!")

if __name__ == "__main__":
    asyncio.run(main())
