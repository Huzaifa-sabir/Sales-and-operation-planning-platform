"""
Database Indexes for Performance Optimization
Creates indexes on frequently queried fields
"""
from motor.motor_asyncio import AsyncIOMotorDatabase


async def create_performance_indexes(db: AsyncIOMotorDatabase):
    """Create all database indexes for optimal query performance"""

    # Users indexes
    await db.users.create_index("email", unique=True)
    await db.users.create_index("employeeId", unique=True, sparse=True)
    await db.users.create_index([("role", 1), ("isActive", 1)])
    await db.users.create_index("isActive")

    # Customers indexes
    await db.customers.create_index("customerId", unique=True)
    await db.customers.create_index("customerName")
    await db.customers.create_index([("region", 1), ("territory", 1)])
    await db.customers.create_index("isActive")

    # Products indexes
    await db.products.create_index("itemCode", unique=True)
    await db.products.create_index("itemDescription")
    await db.products.create_index("category")
    await db.products.create_index("isActive")

    # Pricing matrix indexes
    await db.pricing_matrix.create_index([("customerId", 1), ("productId", 1)], unique=True)
    await db.pricing_matrix.create_index("customerId")
    await db.pricing_matrix.create_index("productId")
    await db.pricing_matrix.create_index("effectiveDate")

    # Sales history indexes
    await db.sales_history.create_index([("customerId", 1), ("productId", 1), ("year", 1), ("month", 1)])
    await db.sales_history.create_index([("year", 1), ("month", 1)])
    await db.sales_history.create_index("saleDate")
    await db.sales_history.create_index("customerId")
    await db.sales_history.create_index("productId")

    # S&OP Cycles indexes
    await db.sop_cycles.create_index("cycleName")
    await db.sop_cycles.create_index("status")
    await db.sop_cycles.create_index([("startDate", 1), ("endDate", 1)])
    await db.sop_cycles.create_index("endDate")
    await db.sop_cycles.create_index([("status", 1), ("endDate", 1)])

    # Forecasts indexes
    await db.forecasts.create_index([("cycleId", 1), ("salesRepId", 1)])
    await db.forecasts.create_index([("cycleId", 1), ("customerId", 1), ("productId", 1)])
    await db.forecasts.create_index("status")
    await db.forecasts.create_index("salesRepId")
    await db.forecasts.create_index([("cycleId", 1), ("status", 1)])
    await db.forecasts.create_index("submittedAt")

    # Reports indexes
    await db.reports.create_index([("userId", 1), ("reportType", 1)])
    await db.reports.create_index("status")
    await db.reports.create_index("cacheKey")
    await db.reports.create_index([("createdAt", 1), ("expiresAt", 1)])
    await db.reports.create_index("generatedAt")

    # Settings indexes
    await db.settings.create_index("key", unique=True)
    await db.settings.create_index("category")
    await db.settings.create_index("isPublic")

    # Audit logs indexes
    await db.audit_logs.create_index("timestamp")
    await db.audit_logs.create_index("userId")
    await db.audit_logs.create_index("action")
    await db.audit_logs.create_index([("entityType", 1), ("entityId", 1)])
    await db.audit_logs.create_index("severity")
    await db.audit_logs.create_index([("timestamp", -1), ("severity", 1)])  # For recent critical events

    # TTL index for automatic audit log cleanup (optional - comment out if not needed)
    # This will automatically delete audit logs older than 90 days
    # await db.audit_logs.create_index("timestamp", expireAfterSeconds=7776000)  # 90 days

    print("All database indexes created successfully")
