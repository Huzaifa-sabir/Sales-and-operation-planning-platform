import asyncio
from motor.motor_asyncio import AsyncIOMotorClient

async def check_sales():
    client = AsyncIOMotorClient('mongodb://localhost:27017')
    db = client.sop_portal

    # Count total records
    total = await db.sales_history.count_documents({})
    print(f'Total sales history records: {total}')

    # Get a sample record
    sample = await db.sales_history.find_one()
    if sample:
        print(f'\nSample record:')
        print(f'  Customer: {sample.get("customerName")}')
        print(f'  Product: {sample.get("productCode")} - {sample.get("productDescription")}')
        print(f'  Year-Month: {sample.get("yearMonth")}')
        print(f'  Quantity: {sample.get("quantity")}')
        print(f'  Total Sales: ${sample.get("totalSales"):,.2f}')
        print(f'  Gross Profit: ${sample.get("grossProfit"):,.2f}')

    # Get summary by year
    pipeline = [
        {
            '$group': {
                '_id': '$year',
                'totalSales': {'$sum': '$totalSales'},
                'count': {'$sum': 1}
            }
        },
        {'$sort': {'_id': 1}}
    ]

    print(f'\nSales by Year:')
    async for year_data in db.sales_history.aggregate(pipeline):
        print(f'  {year_data["_id"]}: ${year_data["totalSales"]:,.2f} ({year_data["count"]} records)')

    client.close()

asyncio.run(check_sales())
