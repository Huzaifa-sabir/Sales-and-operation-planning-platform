"""
Database seeding script to populate initial data
"""
import asyncio
from datetime import datetime, timedelta
from motor.motor_asyncio import AsyncIOMotorDatabase
import logging

from app.config.database import db
from app.config.settings import settings
from app.utils.security import hash_password

logger = logging.getLogger(__name__)


async def seed_users(database: AsyncIOMotorDatabase):
    """Seed initial users"""
    users_collection = database.users

    # Check if admin user already exists
    existing_admin = await users_collection.find_one({"username": settings.ADMIN_USERNAME})
    if existing_admin:
        logger.info(f"Admin user '{settings.ADMIN_USERNAME}' already exists")
        return

    # Create admin user
    admin_user = {
        "username": settings.ADMIN_USERNAME,
        "email": settings.ADMIN_EMAIL,
        "fullName": settings.ADMIN_FULL_NAME,
        "role": "admin",
        "hashedPassword": hash_password(settings.ADMIN_PASSWORD),
        "isActive": True,
        "loginAttempts": 0,
        "metadata": {},
        "createdAt": datetime.utcnow(),
        "updatedAt": datetime.utcnow()
    }

    result = await users_collection.insert_one(admin_user)
    logger.info(f"Created admin user: {settings.ADMIN_USERNAME} (ID: {result.inserted_id})")

    # Create sales rep user
    sales_user = {
        "username": "sales",
        "email": "sales@heavygarlic.com",
        "fullName": "David Brace",
        "role": "sales_rep",
        "hashedPassword": hash_password("sales123"),
        "isActive": True,
        "loginAttempts": 0,
        "metadata": {
            "territory": "Central America",
            "phone": "+1-305-555-0101"
        },
        "createdAt": datetime.utcnow(),
        "updatedAt": datetime.utcnow()
    }

    result = await users_collection.insert_one(sales_user)
    logger.info(f"Created sales rep user: sales (ID: {result.inserted_id})")

    # Get sales rep ID for customers
    sales_rep = await users_collection.find_one({"username": "sales"})
    return str(sales_rep["_id"])


async def seed_customers(database: AsyncIOMotorDatabase, sales_rep_id: str):
    """Seed initial customers from Excel data"""
    customers_collection = database.customers

    # Check if customers already exist
    count = await customers_collection.count_documents({})
    if count > 0:
        logger.info(f"Customers collection already has {count} documents")
        return

    # Sample customers from Excel files
    customers = [
        {
            "customerId": "PATITO-000001",
            "customerName": "Industria Los Patitos, S.A.",
            "sopCustomerName": "Los Patitos",
            "salesRepId": sales_rep_id,
            "salesRepName": "David Brace",
            "location": {
                "city": "La Casona Del Cerdo",
                "state": "HR",
                "country": "Honduras"
            },
            "contactPerson": "Maria Rodriguez",
            "contactEmail": "maria@lospatitos.hn",
            "contactPhone": "+504-2234-5678",
            "isActive": True,
            "metadata": {"totalSalesYTD": 125000.50},
            "createdAt": datetime.utcnow(),
            "updatedAt": datetime.utcnow()
        },
        {
            "customerId": "CANADA-000002",
            "customerName": "Canadawide Fruit Wholesalers Inc.",
            "sopCustomerName": "Canadawide",
            "salesRepId": sales_rep_id,
            "salesRepName": "David Brace",
            "location": {
                "city": "Toronto",
                "state": "ON",
                "country": "Canada"
            },
            "contactPerson": "John Smith",
            "contactEmail": "john@canadawide.ca",
            "contactPhone": "+1-416-555-0100",
            "isActive": True,
            "metadata": {"totalSalesYTD": 250000.00},
            "createdAt": datetime.utcnow(),
            "updatedAt": datetime.utcnow()
        },
        {
            "customerId": "AAORG-000003",
            "customerName": "A&A Organic Farms Corp.",
            "sopCustomerName": "A&A Organic",
            "salesRepId": sales_rep_id,
            "salesRepName": "David Brace",
            "location": {
                "city": "Miami",
                "state": "FL",
                "country": "USA"
            },
            "contactPerson": "Alice Johnson",
            "contactEmail": "alice@aaorganic.com",
            "contactPhone": "+1-305-555-0200",
            "isActive": True,
            "metadata": {"totalSalesYTD": 180000.75},
            "createdAt": datetime.utcnow(),
            "updatedAt": datetime.utcnow()
        },
        {
            "customerId": "MIAMI-000004",
            "customerName": "Miami Wholesale Market",
            "sopCustomerName": "Miami Wholesale",
            "salesRepId": sales_rep_id,
            "salesRepName": "David Brace",
            "location": {
                "city": "Miami",
                "state": "FL",
                "country": "USA"
            },
            "contactPerson": "Carlos Garcia",
            "contactEmail": "carlos@miamiwholesale.com",
            "contactPhone": "+1-305-555-0300",
            "isActive": True,
            "metadata": {"totalSalesYTD": 320000.00},
            "createdAt": datetime.utcnow(),
            "updatedAt": datetime.utcnow()
        },
        {
            "customerId": "FRESH-000005",
            "customerName": "Fresh Produce Distributors",
            "sopCustomerName": "Fresh Produce",
            "salesRepId": sales_rep_id,
            "salesRepName": "David Brace",
            "location": {
                "city": "Los Angeles",
                "state": "CA",
                "country": "USA"
            },
            "contactPerson": "Sarah Lee",
            "contactEmail": "sarah@freshproduce.com",
            "contactPhone": "+1-213-555-0400",
            "isActive": True,
            "metadata": {"totalSalesYTD": 210000.25},
            "createdAt": datetime.utcnow(),
            "updatedAt": datetime.utcnow()
        },
        {
            "customerId": "GARDEN-000006",
            "customerName": "Garden Valley Foods",
            "sopCustomerName": "Garden Valley",
            "salesRepId": sales_rep_id,
            "salesRepName": "David Brace",
            "location": {
                "city": "Phoenix",
                "state": "AZ",
                "country": "USA"
            },
            "contactPerson": "Mike Davis",
            "contactEmail": "mike@gardenvalley.com",
            "contactPhone": "+1-602-555-0500",
            "isActive": True,
            "metadata": {"totalSalesYTD": 145000.00},
            "createdAt": datetime.utcnow(),
            "updatedAt": datetime.utcnow()
        }
    ]

    result = await customers_collection.insert_many(customers)
    logger.info(f"Seeded {len(result.inserted_ids)} customers")


async def seed_products(database: AsyncIOMotorDatabase):
    """Seed initial products from Excel data"""
    products_collection = database.products

    # Check if products already exist
    count = await products_collection.count_documents({})
    if count > 0:
        logger.info(f"Products collection already has {count} documents")
        return

    # Sample products from Excel files
    products = [
        {
            "itemCode": "110001",
            "description": "Peeled Garlic 12x1 LB Garland",
            "group": {
                "code": "G1",
                "subgroup": "G1S7",
                "desc": "Group 1-2"
            },
            "manufacturing": {
                "location": "Miami",
                "line": "Peeled Garlic Repack"
            },
            "weight": 12.0,
            "uom": "CS",
            "pricing": {
                "avgPrice": 52.00,
                "costPrice": 40.00,
                "currency": "USD"
            },
            "isActive": True,
            "metadata": {"salesYTD": 25000},
            "createdAt": datetime.utcnow(),
            "updatedAt": datetime.utcnow()
        },
        {
            "itemCode": "110002",
            "description": "Peeled Garlic 12x3 LB Garland",
            "group": {
                "code": "G1",
                "subgroup": "G1S7",
                "desc": "Group 1-2"
            },
            "manufacturing": {
                "location": "Miami",
                "line": "Peeled Garlic Repack"
            },
            "weight": 36.0,
            "uom": "CS",
            "pricing": {
                "avgPrice": 95.00,
                "costPrice": 75.00,
                "currency": "USD"
            },
            "isActive": True,
            "metadata": {"salesYTD": 18000},
            "createdAt": datetime.utcnow(),
            "updatedAt": datetime.utcnow()
        },
        {
            "itemCode": "130030",
            "description": "Garlic Puree 40 LB Bag",
            "group": {
                "code": "G1",
                "subgroup": "G1S8",
                "desc": "Group 1-2"
            },
            "manufacturing": {
                "location": "Miami",
                "line": "Garlic Puree"
            },
            "weight": 40.0,
            "uom": "BAG",
            "pricing": {
                "avgPrice": 70.00,
                "costPrice": 55.00,
                "currency": "USD"
            },
            "isActive": True,
            "metadata": {"salesYTD": 12000},
            "createdAt": datetime.utcnow(),
            "updatedAt": datetime.utcnow()
        },
        {
            "itemCode": "110005",
            "description": "Chopped Garlic 12x16 OZ",
            "group": {
                "code": "G1",
                "subgroup": "G1S7",
                "desc": "Group 1-2"
            },
            "manufacturing": {
                "location": "Miami",
                "line": "Chopped Garlic"
            },
            "weight": 12.0,
            "uom": "CS",
            "pricing": {
                "avgPrice": 48.00,
                "costPrice": 38.00,
                "currency": "USD"
            },
            "isActive": True,
            "metadata": {"salesYTD": 15000},
            "createdAt": datetime.utcnow(),
            "updatedAt": datetime.utcnow()
        },
        {
            "itemCode": "120015",
            "description": "Ginger Paste 30 LB Bucket",
            "group": {
                "code": "G2",
                "subgroup": "G2S1",
                "desc": "Group 2-1"
            },
            "manufacturing": {
                "location": "Miami",
                "line": "Ginger Processing"
            },
            "weight": 30.0,
            "uom": "BUCKET",
            "pricing": {
                "avgPrice": 85.00,
                "costPrice": 68.00,
                "currency": "USD"
            },
            "isActive": True,
            "metadata": {"salesYTD": 8000},
            "createdAt": datetime.utcnow(),
            "updatedAt": datetime.utcnow()
        },
        {
            "itemCode": "140020",
            "description": "Mixed Herbs 24x8 OZ",
            "group": {
                "code": "G3",
                "subgroup": "G3S2",
                "desc": "Group 3-1"
            },
            "manufacturing": {
                "location": "Miami",
                "line": "Herbs Processing"
            },
            "weight": 12.0,
            "uom": "CS",
            "pricing": {
                "avgPrice": 62.00,
                "costPrice": 48.00,
                "currency": "USD"
            },
            "isActive": True,
            "metadata": {"salesYTD": 10000},
            "createdAt": datetime.utcnow(),
            "updatedAt": datetime.utcnow()
        },
        {
            "itemCode": "110010",
            "description": "Minced Garlic 6x32 OZ",
            "group": {
                "code": "G1",
                "subgroup": "G1S7",
                "desc": "Group 1-2"
            },
            "manufacturing": {
                "location": "Miami",
                "line": "Minced Garlic"
            },
            "weight": 12.0,
            "uom": "CS",
            "pricing": {
                "avgPrice": 55.00,
                "costPrice": 42.00,
                "currency": "USD"
            },
            "isActive": True,
            "metadata": {"salesYTD": 14000},
            "createdAt": datetime.utcnow(),
            "updatedAt": datetime.utcnow()
        },
        {
            "itemCode": "110015",
            "description": "Roasted Garlic 12x12 OZ",
            "group": {
                "code": "G1",
                "subgroup": "G1S7",
                "desc": "Group 1-2"
            },
            "manufacturing": {
                "location": "Miami",
                "line": "Roasted Garlic"
            },
            "weight": 9.0,
            "uom": "CS",
            "pricing": {
                "avgPrice": 58.00,
                "costPrice": 45.00,
                "currency": "USD"
            },
            "isActive": True,
            "metadata": {"salesYTD": 9000},
            "createdAt": datetime.utcnow(),
            "updatedAt": datetime.utcnow()
        },
        {
            "itemCode": "150025",
            "description": "Cilantro Paste 20 LB Bag",
            "group": {
                "code": "G3",
                "subgroup": "G3S3",
                "desc": "Group 3-2"
            },
            "manufacturing": {
                "location": "Miami",
                "line": "Herbs Processing"
            },
            "weight": 20.0,
            "uom": "BAG",
            "pricing": {
                "avgPrice": 42.00,
                "costPrice": 32.00,
                "currency": "USD"
            },
            "isActive": True,
            "metadata": {"salesYTD": 7000},
            "createdAt": datetime.utcnow(),
            "updatedAt": datetime.utcnow()
        }
    ]

    result = await products_collection.insert_many(products)
    logger.info(f"Seeded {len(result.inserted_ids)} products")


async def seed_sales_history(database: AsyncIOMotorDatabase):
    """Seed sample sales history data"""
    sales_collection = database.salesHistory
    customers_collection = database.customers
    products_collection = database.products

    # Check if sales history already exists
    count = await sales_collection.count_documents({})
    if count > 0:
        logger.info(f"Sales history collection already has {count} documents")
        return

    # Get sample customers and products
    customers = await customers_collection.find().limit(3).to_list(length=3)
    products = await products_collection.find().limit(3).to_list(length=3)

    if not customers or not products:
        logger.warning("Cannot seed sales history: no customers or products found")
        return

    sales_records = []
    # Generate 24 months of sales data
    for month_offset in range(24):
        date = datetime.utcnow() - timedelta(days=30 * month_offset)
        month_str = date.strftime("%Y-%m")
        year = date.year
        month_num = date.month

        for customer in customers:
            for product in products:
                # Generate random-ish quantity based on month
                base_qty = 50 + (month_offset % 10) * 10
                quantity = base_qty + (hash(f"{customer['customerId']}{product['itemCode']}{month_str}") % 50)

                unit_price = product["pricing"]["avgPrice"]
                total_sales = quantity * unit_price
                cost_price = product["pricing"].get("costPrice", unit_price * 0.8)
                gross_profit = (unit_price - cost_price) * quantity

                sales_records.append({
                    "customerId": customer["customerId"],
                    "customerName": customer["sopCustomerName"] or customer["customerName"],
                    "productId": str(product["_id"]),
                    "productCode": product["itemCode"],
                    "productDescription": product["description"],
                    "month": month_str,
                    "year": year,
                    "monthNum": month_num,
                    "quantity": float(quantity),
                    "unitPrice": unit_price,
                    "totalSales": total_sales,
                    "costPrice": cost_price,
                    "grossProfit": gross_profit,
                    "salesRepId": customer["salesRepId"],
                    "salesRepName": customer["salesRepName"],
                    "createdAt": datetime.utcnow()
                })

    if sales_records:
        result = await sales_collection.insert_many(sales_records)
        logger.info(f"Seeded {len(result.inserted_ids)} sales history records")


async def run_seed():
    """Main seed function"""
    try:
        logger.info("Starting database seeding...")

        # Connect to database
        await db.connect_db()
        database = db.get_database()

        # Seed in order (users first, then customers, products, sales history)
        sales_rep_id = await seed_users(database)
        await seed_customers(database, sales_rep_id)
        await seed_products(database)
        await seed_sales_history(database)

        logger.info("Database seeding completed successfully!")

    except Exception as e:
        logger.error(f"Error seeding database: {e}")
        raise
    finally:
        await db.close_db()


if __name__ == "__main__":
    # Run the seed script
    asyncio.run(run_seed())
