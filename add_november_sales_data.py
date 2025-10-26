"""
Add November 2025 sales data to test report generation
"""
from pymongo import MongoClient
import os
from datetime import datetime

# Connect to MongoDB
client = MongoClient(os.getenv('MONGODB_URI', 'mongodb://localhost:27017'))
db = client['sop_portal']

print("=" * 70)
print("Adding November 2025 Sales Data for Testing")
print("=" * 70)

# Get existing customers and products
customers = list(db.customers.find().limit(5))
products = list(db.products.find().limit(5))

print(f"\nFound {len(customers)} customers")
print(f"Found {len(products)} products")

# Get a sales rep
sales_rep = db.users.find_one({"role": "sales_rep"})
if not sales_rep:
    sales_rep = db.users.find_one({"role": "admin"})

sales_rep_id = str(sales_rep["_id"]) if sales_rep else "default-rep"
sales_rep_name = sales_rep.get("fullName", "Default Sales Rep") if sales_rep else "Default Sales Rep"

print(f"[OK] Using sales rep: {sales_rep_name}")

# November 2025 sales data
november_sales = []

# Create sales records for November 2025
for i, customer in enumerate(customers):
    for j, product in enumerate(products):
        # Vary quantities and prices for realistic data
        quantity = 50 + (i * 20) + (j * 10)
        unit_price = 25.00 + (j * 15.50)
        cost_price = unit_price * 0.65  # 35% margin

        total_sales = quantity * unit_price
        cogs = quantity * cost_price
        gross_profit = total_sales - cogs
        gross_profit_percent = (gross_profit / total_sales * 100) if total_sales > 0 else 0

        sale_record = {
            "customerId": customer.get("customerId", str(customer["_id"])),
            "customerName": customer.get("customerName", "Unknown Customer"),
            "productId": product.get("itemCode", str(product["_id"])),
            "productCode": product.get("itemCode", "UNKNOWN"),
            "productDescription": product.get("itemDescription", "Unknown Product"),
            "month": "2025-11",
            "year": 2025,
            "monthNum": 11,
            "quantity": float(quantity),
            "unitPrice": round(unit_price, 2),
            "totalSales": round(total_sales, 2),
            "costPrice": round(cost_price, 2),
            "cogs": round(cogs, 2),
            "grossProfit": round(gross_profit, 2),
            "grossProfitPercent": round(gross_profit_percent, 2),
            "salesRepId": sales_rep_id,
            "salesRepName": sales_rep_name,
            "createdAt": datetime.utcnow().isoformat()
        }

        november_sales.append(sale_record)

print(f"\n[OK] Created {len(november_sales)} November 2025 sales records")

# Insert into database
if november_sales:
    result = db.salesHistory.insert_many(november_sales)
    print(f"[OK] Inserted {len(result.inserted_ids)} records into salesHistory collection")

    # Verify insertion
    nov_count = db.salesHistory.count_documents({"year": 2025, "monthNum": 11})
    print(f"[OK] Total November 2025 records in database: {nov_count}")

    # Calculate totals for verification
    total_revenue = sum(s["totalSales"] for s in november_sales)
    total_quantity = sum(s["quantity"] for s in november_sales)

    print("\n" + "=" * 70)
    print("November 2025 Sales Summary")
    print("=" * 70)
    print(f"Total Records: {len(november_sales)}")
    print(f"Total Revenue: ${total_revenue:,.2f}")
    print(f"Total Quantity: {total_quantity:,.2f}")
    print(f"Average Revenue per Transaction: ${total_revenue/len(november_sales):,.2f}")
    print("=" * 70)

    print("\n[OK] Sample records:")
    for i, sale in enumerate(november_sales[:3]):
        print(f"  {i+1}. {sale['customerName']} - {sale['productDescription']}")
        print(f"     Qty: {sale['quantity']}, Price: ${sale['unitPrice']}, Total: ${sale['totalSales']}")

    print("\n[SUCCESS] SUCCESS! November 2025 data added to database")
    print("You can now test report generation with year=2025, month=11")
else:
    print("[ERROR] No sales records created")
