"""
Seed script to populate sales history data in MongoDB
"""
import asyncio
from datetime import datetime, timedelta
from motor.motor_asyncio import AsyncIOMotorClient
from bson import ObjectId
import random


async def seed_sales_history():
    """Add sample sales history data to the database"""
    client = AsyncIOMotorClient('mongodb://localhost:27017')
    db = client.sop_portal

    print("Starting sales history data seeding...")

    # Get existing customers and products
    customers = await db.customers.find().to_list(length=100)
    products = await db.products.find().to_list(length=100)

    if not customers:
        print("ERROR: No customers found in database. Please seed customers first.")
        return

    if not products:
        print("ERROR: No products found in database. Please seed products first.")
        return

    print(f"Found {len(customers)} customers and {len(products)} products")

    # Clear existing sales history
    result = await db.sales_history.delete_many({})
    print(f"Cleared {result.deleted_count} existing sales history records")

    # Generate sales history for last 24 months
    sales_records = []
    base_date = datetime.now() - timedelta(days=730)  # 24 months ago

    record_count = 0
    for month_offset in range(24):
        month_date = base_date + timedelta(days=30 * month_offset)
        year = month_date.year
        month = month_date.month

        # Create sales records for random customer-product combinations
        # Each month, create 5-10 sales records
        num_records = random.randint(5, 10)

        for _ in range(num_records):
            customer = random.choice(customers)
            product = random.choice(products)

            # Get sales rep from customer if available
            sales_rep_id = customer.get('salesRepId', 'SR001')
            sales_rep_name = customer.get('salesRepName', 'Unknown Rep')

            # Generate realistic quantities based on product type
            base_quantity = random.randint(100, 1000)
            quantity = base_quantity + random.randint(-50, 50)

            # Get product pricing
            pricing = product.get('pricing', {})
            avg_price = pricing.get('avgPrice', 50.0)
            cost_price = pricing.get('costPrice', avg_price * 0.7)

            # Add some variation to unit price
            unit_price = avg_price + random.uniform(-5, 5)

            # Calculate totals
            total_sales = quantity * unit_price
            cogs = quantity * cost_price
            gross_profit = total_sales - cogs
            gross_profit_percent = (gross_profit / total_sales * 100) if total_sales > 0 else 0

            # Get product description
            item_description = product.get('itemDescription') or product.get('description', 'Unknown Product')

            sales_record = {
                "_id": str(ObjectId()),
                "customerId": str(customer['_id']),
                "productId": product.get('itemCode', 'UNKNOWN'),
                "salesRepId": sales_rep_id,
                "customerName": customer.get('customerName', 'Unknown Customer'),
                "productCode": product.get('itemCode', 'UNKNOWN'),
                "productDescription": item_description,
                "salesRepName": sales_rep_name,
                "yearMonth": month_date.strftime('%Y-%m'),  # String in YYYY-MM format
                "year": year,
                "month": month,  # Integer 1-12
                "quantity": quantity,
                "unitPrice": round(unit_price, 2),
                "totalSales": round(total_sales, 2),
                "costPrice": round(cost_price, 2),
                "cogs": round(cogs, 2),
                "grossProfit": round(gross_profit, 2),
                "grossProfitPercent": round(gross_profit_percent, 2),
                "createdAt": month_date,
            }

            sales_records.append(sales_record)
            record_count += 1

    # Insert all records
    if sales_records:
        result = await db.sales_history.insert_many(sales_records)
        print(f"OK - Inserted {len(result.inserted_ids)} sales history records")

        # Show some statistics
        total_sales = sum(r['totalSales'] for r in sales_records)
        total_quantity = sum(r['quantity'] for r in sales_records)
        avg_price = total_sales / total_quantity if total_quantity > 0 else 0

        print(f"\nStatistics:")
        print(f"  Total Sales: ${total_sales:,.2f}")
        print(f"  Total Quantity: {total_quantity:,} units")
        print(f"  Average Unit Price: ${avg_price:.2f}")
        print(f"  Time Period: {sales_records[0]['yearMonth']} to {sales_records[-1]['yearMonth']}")
    else:
        print("No sales records to insert")

    # Create indexes for better query performance
    await db.sales_history.create_index([("customerId", 1)])
    await db.sales_history.create_index([("productId", 1)])
    await db.sales_history.create_index([("salesRepId", 1)])
    await db.sales_history.create_index([("year", 1), ("month", 1)])
    await db.sales_history.create_index([("yearMonth", -1)])
    print("\nCreated indexes for sales_history collection")

    client.close()
    print("\nSales history seeding completed successfully!")


if __name__ == "__main__":
    asyncio.run(seed_sales_history())
