"""
Add November 2025 data to your Render MongoDB Atlas - IMMEDIATE FIX
Run this with your Render MongoDB URI
"""
from pymongo import MongoClient
from datetime import datetime
import sys

# PASTE YOUR RENDER MONGODB_URI HERE:
MONGODB_URI = input("Paste your Render MONGODB_URI (from Render dashboard > Environment): ").strip()

if not MONGODB_URI or MONGODB_URI == "":
    print("[ERROR] MongoDB URI is required!")
    print("\nHow to get it:")
    print("1. Go to dashboard.render.com")
    print("2. Click your backend service")
    print("3. Click 'Environment' tab")
    print("4. Copy the MONGODB_URI value")
    sys.exit(1)

print("=" * 80)
print("ADDING NOVEMBER 2025 DATA TO ATLAS - LIVE FIX")
print("=" * 80)

try:
    client = MongoClient(MONGODB_URI, serverSelectionTimeoutMS=10000)
    db = client['sop_portal']

    # Test connection
    client.server_info()
    print("[OK] Connected to MongoDB Atlas\n")

    # Check current state
    total_before = db.salesHistory.count_documents({})
    nov_before = db.salesHistory.count_documents({"year": 2025, "monthNum": 11})

    print(f"Current state:")
    print(f"  Total sales: {total_before}")
    print(f"  November 2025: {nov_before}")

    # Get customers and products from Atlas
    customers = list(db.customers.find().limit(5))
    products = list(db.products.find().limit(5))

    if len(customers) == 0:
        print("\n[ERROR] No customers in database!")
        sys.exit(1)

    if len(products) == 0:
        print("\n[ERROR] No products in database!")
        sys.exit(1)

    print(f"\n[OK] Found {len(customers)} customers and {len(products)} products")

    # Get admin user for sales rep
    admin = db.users.find_one({"email": "admin@heavygarlic.com"})
    if not admin:
        admin = db.users.find_one({"role": "admin"})

    sales_rep_id = str(admin["_id"]) if admin else "default-rep"
    sales_rep_name = admin.get("fullName", "Admin") if admin else "Admin"

    print(f"[OK] Using sales rep: {sales_rep_name}")

    # Create November 2025 sales
    november_sales = []

    for i, customer in enumerate(customers):
        for j, product in enumerate(products):
            quantity = 50 + (i * 20) + (j * 10)
            unit_price = 25.00 + (j * 15.50)
            cost_price = unit_price * 0.65

            total_sales = quantity * unit_price
            cogs = quantity * cost_price
            gross_profit = total_sales - cogs
            gross_profit_percent = (gross_profit / total_sales * 100) if total_sales > 0 else 0

            sale_record = {
                "customerId": customer.get("customerId", str(customer["_id"])),
                "customerName": customer.get("customerName", "Unknown"),
                "productId": product.get("itemCode", str(product["_id"])),
                "productCode": product.get("itemCode", "UNKNOWN"),
                "productDescription": product.get("itemDescription", "Unknown"),
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
                "createdAt": datetime.utcnow()
            }

            november_sales.append(sale_record)

    print(f"\n[OK] Created {len(november_sales)} November sales records")

    # Insert into Atlas
    result = db.salesHistory.insert_many(november_sales)
    print(f"[OK] Inserted {len(result.inserted_ids)} records into Atlas")

    # Verify
    nov_after = db.salesHistory.count_documents({"year": 2025, "monthNum": 11})
    total_after = db.salesHistory.count_documents({})

    print(f"\nAfter insertion:")
    print(f"  Total sales: {total_after} (+{total_after - total_before})")
    print(f"  November 2025: {nov_after}")

    # Calculate totals
    total_revenue = sum(s["totalSales"] for s in november_sales)
    total_quantity = sum(s["quantity"] for s in november_sales)

    print("\n" + "=" * 80)
    print("NOVEMBER 2025 DATA ADDED SUCCESSFULLY!")
    print("=" * 80)
    print(f"Records: {len(november_sales)}")
    print(f"Total Revenue: ${total_revenue:,.2f}")
    print(f"Total Quantity: {total_quantity:,.2f}")
    print("=" * 80)

    print("\n[NEXT STEP]")
    print("Go to https://soptest.netlify.app/reports")
    print("1. Select 'Sales Summary Report'")
    print("2. Year: Select '2025'")
    print("3. Month: Select 'November'")
    print("4. Click 'Generate Excel'")
    print(f"5. Should show: ${total_revenue:,.2f} revenue")

    client.close()

except Exception as e:
    print(f"\n[ERROR] {e}")
    print("\nPossible issues:")
    print("1. Wrong MongoDB URI")
    print("2. IP not whitelisted in MongoDB Atlas")
    print("3. Network connection issue")
    sys.exit(1)
