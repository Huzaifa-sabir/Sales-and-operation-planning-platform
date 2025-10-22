"""
Sales History Service Layer
Handles sales history data retrieval, filtering, and aggregation
"""
from typing import Optional, List, Dict, Any
from datetime import datetime, timedelta
from dateutil.relativedelta import relativedelta
from bson import ObjectId
from motor.motor_asyncio import AsyncIOMotorDatabase

from app.models.sales_history import SalesHistoryInDB


class SalesHistoryService:
    """Service class for sales history operations"""

    def __init__(self, db: AsyncIOMotorDatabase):
        self.db = db
        self.collection = db.sales_history

    async def get_sales_history(
        self,
        skip: int = 0,
        limit: int = 100,
        customer_id: Optional[str] = None,
        product_id: Optional[str] = None,
        start_date: Optional[datetime] = None,
        end_date: Optional[datetime] = None,
        year: Optional[int] = None,
        month: Optional[int] = None
    ) -> Dict[str, Any]:
        """
        Get sales history with filtering
        Returns paginated sales records with filtering options
        """
        # Build filter query
        query = {}

        if customer_id:
            query["customerId"] = customer_id

        if product_id:
            query["productId"] = product_id

        # Date range filtering
        if year and month:
            # Specific month
            query["year"] = year
            query["month"] = month
        elif year:
            # Specific year
            query["year"] = year
        elif start_date or end_date:
            # Custom date range
            date_query = {}
            if start_date:
                date_query["$gte"] = start_date
            if end_date:
                date_query["$lte"] = end_date

            if date_query:
                # We need to match on year/month combination
                # This is simplified - in production you'd want more sophisticated date handling
                query["$and"] = []
                if start_date:
                    query["$and"].append({
                        "$or": [
                            {"year": {"$gt": start_date.year}},
                            {"year": start_date.year, "month": {"$gte": start_date.month}}
                        ]
                    })
                if end_date:
                    query["$and"].append({
                        "$or": [
                            {"year": {"$lt": end_date.year}},
                            {"year": end_date.year, "month": {"$lte": end_date.month}}
                        ]
                    })

        # Get total count
        total = await self.collection.count_documents(query)

        # Get paginated sales records
        cursor = self.collection.find(query).skip(skip).limit(limit).sort([("year", -1), ("month", -1)])
        sales_records = []
        async for record in cursor:
            record["_id"] = str(record["_id"])
            sales_records.append(SalesHistoryInDB(**record))

        # Calculate pagination info
        total_pages = (total + limit - 1) // limit if limit > 0 else 1
        current_page = (skip // limit) + 1 if limit > 0 else 1

        return {
            "records": sales_records,
            "total": total,
            "page": current_page,
            "pageSize": limit,
            "totalPages": total_pages,
            "hasNext": skip + limit < total,
            "hasPrev": skip > 0
        }

    async def get_sales_statistics(
        self,
        customer_id: Optional[str] = None,
        product_id: Optional[str] = None,
        start_date: Optional[datetime] = None,
        end_date: Optional[datetime] = None
    ) -> Dict[str, Any]:
        """
        Get aggregated sales statistics
        Returns total quantity, revenue, and other metrics
        """
        # Build match stage for aggregation
        match_stage = {}

        if customer_id:
            match_stage["customerId"] = customer_id

        if product_id:
            match_stage["productId"] = product_id

        if start_date or end_date:
            date_filter = {}
            if start_date:
                date_filter["$gte"] = start_date
            if end_date:
                date_filter["$lte"] = end_date

        # Aggregation pipeline
        pipeline = []

        if match_stage:
            pipeline.append({"$match": match_stage})

        pipeline.extend([
            {
                "$group": {
                    "_id": None,
                    "totalQuantity": {"$sum": "$quantity"},
                    "totalRevenue": {"$sum": {"$multiply": ["$quantity", "$unitPrice"]}},
                    "avgQuantity": {"$avg": "$quantity"},
                    "avgUnitPrice": {"$avg": "$unitPrice"},
                    "recordCount": {"$sum": 1},
                    "minQuantity": {"$min": "$quantity"},
                    "maxQuantity": {"$max": "$quantity"}
                }
            }
        ])

        result = await self.collection.aggregate(pipeline).to_list(length=1)

        if result:
            stats = result[0]
            return {
                "totalQuantity": stats.get("totalQuantity", 0),
                "totalRevenue": round(stats.get("totalRevenue", 0), 2),
                "avgQuantity": round(stats.get("avgQuantity", 0), 2),
                "avgUnitPrice": round(stats.get("avgUnitPrice", 0), 2),
                "recordCount": stats.get("recordCount", 0),
                "minQuantity": stats.get("minQuantity", 0),
                "maxQuantity": stats.get("maxQuantity", 0)
            }
        else:
            return {
                "totalQuantity": 0,
                "totalRevenue": 0,
                "avgQuantity": 0,
                "avgUnitPrice": 0,
                "recordCount": 0,
                "minQuantity": 0,
                "maxQuantity": 0
            }

    async def get_sales_by_month(
        self,
        customer_id: Optional[str] = None,
        product_id: Optional[str] = None,
        months: int = 12
    ) -> List[Dict[str, Any]]:
        """
        Get sales aggregated by month for charts
        Returns last N months of sales data
        """
        # Build match stage
        match_stage = {}

        if customer_id:
            match_stage["customerId"] = customer_id

        if product_id:
            match_stage["productId"] = product_id

        # Calculate date range for last N months
        end_date = datetime.now()
        start_date = end_date - relativedelta(months=months)

        # Aggregation pipeline
        pipeline = []

        if match_stage:
            pipeline.append({"$match": match_stage})

        pipeline.extend([
            {
                "$group": {
                    "_id": {
                        "year": "$year",
                        "month": "$month"
                    },
                    "totalQuantity": {"$sum": "$quantity"},
                    "totalRevenue": {"$sum": {"$multiply": ["$quantity", "$unitPrice"]}},
                    "recordCount": {"$sum": 1}
                }
            },
            {
                "$sort": {
                    "_id.year": 1,
                    "_id.month": 1
                }
            },
            {
                "$limit": months
            }
        ])

        results = await self.collection.aggregate(pipeline).to_list(length=months)

        formatted_results = []
        for item in results:
            formatted_results.append({
                "year": item["_id"]["year"],
                "month": item["_id"]["month"],
                "monthLabel": f"{item['_id']['year']}-{str(item['_id']['month']).zfill(2)}",
                "totalQuantity": item["totalQuantity"],
                "totalRevenue": round(item["totalRevenue"], 2),
                "recordCount": item["recordCount"]
            })

        return formatted_results

    async def get_top_products(
        self,
        customer_id: Optional[str] = None,
        limit: int = 10,
        months: int = 12
    ) -> List[Dict[str, Any]]:
        """
        Get top selling products by quantity
        """
        match_stage = {}

        if customer_id:
            match_stage["customerId"] = customer_id

        # Calculate date range
        end_date = datetime.now()
        start_date = end_date - relativedelta(months=months)

        pipeline = []

        if match_stage:
            pipeline.append({"$match": match_stage})

        pipeline.extend([
            {
                "$group": {
                    "_id": "$productId",
                    "totalQuantity": {"$sum": "$quantity"},
                    "totalRevenue": {"$sum": {"$multiply": ["$quantity", "$unitPrice"]}},
                    "avgUnitPrice": {"$avg": "$unitPrice"}
                }
            },
            {
                "$sort": {"totalQuantity": -1}
            },
            {
                "$limit": limit
            }
        ])

        results = await self.collection.aggregate(pipeline).to_list(length=limit)

        formatted_results = []
        for item in results:
            formatted_results.append({
                "productId": item["_id"],
                "totalQuantity": item["totalQuantity"],
                "totalRevenue": round(item["totalRevenue"], 2),
                "avgUnitPrice": round(item["avgUnitPrice"], 2)
            })

        return formatted_results

    async def get_top_customers(
        self,
        product_id: Optional[str] = None,
        limit: int = 10,
        months: int = 12
    ) -> List[Dict[str, Any]]:
        """
        Get top customers by revenue
        """
        match_stage = {}

        if product_id:
            match_stage["productId"] = product_id

        pipeline = []

        if match_stage:
            pipeline.append({"$match": match_stage})

        pipeline.extend([
            {
                "$group": {
                    "_id": "$customerId",
                    "totalQuantity": {"$sum": "$quantity"},
                    "totalRevenue": {"$sum": {"$multiply": ["$quantity", "$unitPrice"]}},
                    "avgUnitPrice": {"$avg": "$unitPrice"}
                }
            },
            {
                "$sort": {"totalRevenue": -1}
            },
            {
                "$limit": limit
            }
        ])

        results = await self.collection.aggregate(pipeline).to_list(length=limit)

        formatted_results = []
        for item in results:
            formatted_results.append({
                "customerId": item["_id"],
                "totalQuantity": item["totalQuantity"],
                "totalRevenue": round(item["totalRevenue"], 2),
                "avgUnitPrice": round(item["avgUnitPrice"], 2)
            })

        return formatted_results
