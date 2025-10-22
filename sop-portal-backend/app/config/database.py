from motor.motor_asyncio import AsyncIOMotorClient, AsyncIOMotorDatabase
from typing import Optional
from app.config.settings import settings
import logging

logger = logging.getLogger(__name__)


class Database:
    """MongoDB database connection manager"""

    client: Optional[AsyncIOMotorClient] = None
    database: Optional[AsyncIOMotorDatabase] = None

    @classmethod
    async def connect_db(cls):
        """Connect to MongoDB database"""
        try:
            logger.info(f"Connecting to MongoDB at {settings.MONGODB_URL}")
            cls.client = AsyncIOMotorClient(settings.MONGODB_URL)
            cls.database = cls.client[settings.MONGODB_DB_NAME]

            # Test connection
            await cls.client.admin.command('ping')
            logger.info(f"Successfully connected to MongoDB database: {settings.MONGODB_DB_NAME}")

            # Create indexes
            await cls.create_indexes()

        except Exception as e:
            logger.error(f"Failed to connect to MongoDB: {e}")
            raise

    @classmethod
    async def close_db(cls):
        """Close MongoDB database connection"""
        if cls.client:
            cls.client.close()
            logger.info("MongoDB connection closed")

    @classmethod
    def get_database(cls) -> AsyncIOMotorDatabase:
        """Get database instance"""
        if cls.database is None:
            raise RuntimeError("Database not connected. Call connect_db() first.")
        return cls.database

    @classmethod
    async def create_indexes(cls):
        """Create database indexes for optimization"""
        if cls.database is None:
            return

        try:
            # Users collection indexes
            await cls.database.users.create_index("username", unique=True)
            await cls.database.users.create_index("email", unique=True)
            await cls.database.users.create_index([("role", 1), ("isActive", 1)])

            # Customers collection indexes
            await cls.database.customers.create_index("customerId", unique=True)
            await cls.database.customers.create_index("salesRepId")
            await cls.database.customers.create_index([("isActive", 1)])

            # Products collection indexes
            await cls.database.products.create_index("itemCode", unique=True)
            await cls.database.products.create_index("group.code")
            await cls.database.products.create_index("manufacturing.location")
            await cls.database.products.create_index([("isActive", 1)])

            # Sales History indexes
            await cls.database.salesHistory.create_index([("customerId", 1), ("month", -1)])
            await cls.database.salesHistory.create_index([("productId", 1), ("month", -1)])
            await cls.database.salesHistory.create_index("month")

            # S&OP Cycles indexes
            await cls.database.sopCycles.create_index([("year", 1), ("month", 1)], unique=True)
            await cls.database.sopCycles.create_index("status")
            await cls.database.sopCycles.create_index("dates.closeDate")

            # S&OP Forecasts indexes
            await cls.database.sopForecasts.create_index([("cycleId", 1), ("customerId", 1), ("productId", 1)])
            await cls.database.sopForecasts.create_index("salesRepId")
            await cls.database.sopForecasts.create_index("status")

            # Product Customer Matrix indexes
            await cls.database.productCustomerMatrix.create_index([("customerId", 1), ("productId", 1)], unique=True)
            await cls.database.productCustomerMatrix.create_index("customerId")
            await cls.database.productCustomerMatrix.create_index("productId")

            logger.info("Database indexes created successfully")

        except Exception as e:
            logger.warning(f"Error creating indexes: {e}")


# Global database instance
db = Database()


# Dependency for FastAPI routes
async def get_db() -> AsyncIOMotorDatabase:
    """Dependency to get database in route handlers"""
    return db.get_database()
