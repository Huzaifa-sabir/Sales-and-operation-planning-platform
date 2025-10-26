"""
Add November 2025 sales data to RENDER MongoDB database
This script connects to your deployed Render MongoDB and adds test data
"""
from pymongo import MongoClient
from datetime import datetime

# IMPORTANT: Replace this with your actual Render MongoDB URI
# You can find it in Render dashboard > your service > Environment Variables > MONGODB_URI
RENDER_MONGODB_URI = input("Enter your Render MongoDB URI: ").strip()

if not RENDER_MONGODB_URI or RENDER_MONGODB_URI == "":
    print("[ERROR] You must provide a MongoDB URI")
    print("\nHow to find it:")
    print("1. Go to render.com")
    print("2. Open your backend service")
    print("3. Go to 'Environment' tab")
    print("4. Copy the MONGODB_URI value")
    exit(1)

print("=" * 70)
print("Adding November 2025 Sales Data to RENDER MongoDB")
print("=" * 70)
print(f"Connecting to: {RENDER_MONGODB_URI[:30]}...")

try:
    # Connect to Render MongoDB
    client = MongoClient(RENDER_MONGODB_URI, serverSelectionTimeoutMS=5000)
    db = client['sop_portal']

    # Test connection
    client.server_info()
    print("[OK] Connected to Render MongoDB successfully!")

except Exception as e:
    print(f"[ERROR] Failed to connect to MongoDB: {str(e)}")
    print("\nPlease check:")
    print("1. MongoDB URI is correct")
    print("2. Your IP is whitelisted in MongoDB Atlas (if using Atlas)")
    print("3. Network connection is stable")
    exit(1)

# Check current data
print("\n[INFO] Checking current database state...")
total_sales = db.salesHistory.count_documents({})
nov_sales = db.salesHistory.count_documents({"year": 2025, "monthNum": 11})
customers_count = db.customers.count_documents({})
products_count = db.products.count_documents({})

print(f"  Total sales records: {total_sales}")
print(f"  November 2025 records: {nov_sales}")
print(f"  Customers: {customers_count}")
print(f"  Products: {products_count}")

if nov_sales > 0:
    response = input(f"\n[WARNING] Found {nov_sales} existing November 2025 records. Delete and recreate? (yes/no): ")
    if response.lower() == 'yes':
        result = db.salesHistory.delete_many({"year": 2025, "monthNum": 11})
        print(f"[OK] Deleted {result.deleted_count} existing November records")
    else:
        print("[INFO] Keeping existing records and adding more...")

# Get existing customers and products from RENDER database
customers = list(db.customers.find().limit(5))
products = list(db.products.find().limit(5))

if len(customers) == 0:
    print("[ERROR] No customers found in database!")
    print("You need to import customers first before adding sales data")
    exit(1)

if len(products) == 0:
    print("[ERROR] No products found in database!")
    print("You need to import products first before adding sales data")
    exit(1)

print(f"\n[OK] Found {len(customers)} customers")
print(f"[OK] Found {len(products)} products")

# Get a sales rep
sales_rep = db.users.find_one({"role": "sales_rep"})
if not sales_rep:
    sales_rep = db.users.find_one({"role": "admin"})

sales_rep_id = str(sales_rep["_id"]) if sales_rep else "default-rep"
sales_rep_name = sales_rep.get("fullName", "Default Sales Rep") if sales_rep else "Default Sales Rep"

print(f"[OK] Using sales rep: {sales_rep_name}")

# Create November 2025 sales data
november_sales = []

print("\n[INFO] Generating November 2025 sales records...")

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

print(f"[OK] Generated {len(november_sales)} November 2025 sales records")

# Insert into Render database
if november_sales:
    try:
        result = db.salesHistory.insert_many(november_sales)
        print(f"[OK] Inserted {len(result.inserted_ids)} records into Render MongoDB")

        # Verify insertion
        nov_count = db.salesHistory.count_documents({"year": 2025, "monthNum": 11})
        print(f"[OK] Total November 2025 records now in Render database: {nov_count}")

        # Calculate totals
        total_revenue = sum(s["totalSales"] for s in november_sales)
        total_quantity = sum(s["quantity"] for s in november_sales)

        print("\n" + "=" * 70)
        print("November 2025 Sales Summary (Added to Render)")
        print("=" * 70)
        print(f"Total Records: {len(november_sales)}")
        print(f"Total Revenue: ${total_revenue:,.2f}")
        print(f"Total Quantity: {total_quantity:,.2f}")
        print(f"Average Revenue per Transaction: ${total_revenue/len(november_sales):,.2f}")
        print("=" * 70)

        print("\n[OK] Sample records added:")
        for i, sale in enumerate(november_sales[:3]):
            print(f"  {i+1}. {sale['customerName']} - {sale['productDescription']}")
            print(f"     Qty: {sale['quantity']}, Price: ${sale['unitPrice']}, Total: ${sale['totalSales']}")

        print("\n[SUCCESS] November 2025 data successfully added to Render MongoDB!")
        print("\nNext Steps:")
        print("1. Go to your deployed frontend")
        print("2. Navigate to Reports page")
        print("3. Select 'Sales Summary Report'")
        print("4. Set filter: Year=2025, Month=November (11)")
        print("5. Click 'Generate Excel'")
        print(f"6. Report should show Total Revenue: ${total_revenue:,.2f}")
        print(f"7. Report should show Total Quantity: {total_quantity:,.2f}")
        print(f"8. Report should show Transactions: {len(november_sales)}")

    except Exception as e:
        print(f"[ERROR] Failed to insert data: {str(e)}")
        exit(1)
else:
    print("[ERROR] No sales records generated")
    exit(1)

client.close()
