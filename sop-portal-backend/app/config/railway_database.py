"""
Railway-specific database configuration for MongoDB Atlas
"""
import os
import ssl
from motor.motor_asyncio import AsyncIOMotorClient, AsyncIOMotorDatabase
from typing import Optional
import logging

logger = logging.getLogger(__name__)

class RailwayDatabase:
    """Railway-optimized MongoDB database connection manager"""

    client: Optional[AsyncIOMotorClient] = None
    database: Optional[AsyncIOMotorDatabase] = None

    @classmethod
    async def connect_db(cls):
        """Connect to MongoDB database with Railway-specific configuration"""
        try:
            # Get connection string from environment or use default
            mongodb_url = os.getenv(
                "MONGODB_URL", 
                "mongodb+srv://huzaifasabir289_db_user:4SLjzoPzm00pQNNv@cluster0.4owv6bf.mongodb.net/sop_portal?retryWrites=true&w=majority"
            )
            
            logger.info(f"Connecting to MongoDB at {mongodb_url}")
            
            # Railway-specific SSL configuration
            cls.client = AsyncIOMotorClient(
                mongodb_url,
                tls=True,
                tlsAllowInvalidCertificates=True,
                tlsAllowInvalidHostnames=True,
                serverSelectionTimeoutMS=60000,
                connectTimeoutMS=60000,
                socketTimeoutMS=60000,
                retryWrites=True,
                retryReads=True,
                maxPoolSize=10,
                minPoolSize=1,
                heartbeatFrequencyMS=10000,
                maxIdleTimeMS=30000
            )
            
            db_name = os.getenv("MONGODB_DB_NAME", "sop_portal")
            cls.database = cls.client[db_name]

            # Test connection with extended retry logic
            max_retries = 5
            for attempt in range(max_retries):
                try:
                    await cls.client.admin.command('ping')
                    logger.info(f"Successfully connected to MongoDB database: {db_name}")
                    break
                except Exception as e:
                    if attempt == max_retries - 1:
                        logger.error(f"Final connection attempt failed: {e}")
                        raise e
                    logger.warning(f"Connection attempt {attempt + 1} failed, retrying in 5 seconds...")
                    import asyncio
                    await asyncio.sleep(5)

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
railway_db = RailwayDatabase()
