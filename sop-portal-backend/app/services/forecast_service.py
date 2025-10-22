"""
Forecast Service Layer
Handles forecast CRUD operations, submissions, versioning, and price calculations
"""
from typing import Optional, List, Dict, Any
from datetime import datetime
from bson import ObjectId
from motor.motor_asyncio import AsyncIOMotorDatabase
from fastapi import HTTPException, status

from app.models.forecast import (
    ForecastCreate,
    ForecastUpdate,
    ForecastInDB,
    ForecastStatus,
    MonthlyForecast
)
from app.models.sop_cycle import CycleStatus


class ForecastService:
    """Service class for forecast operations"""

    def __init__(self, db: AsyncIOMotorDatabase):
        self.db = db
        self.collection = db.forecasts
        self.cycles_collection = db.sop_cycles
        self.matrix_collection = db.pricing_matrix
        self.customers_collection = db.customers
        self.products_collection = db.products
        self.users_collection = db.users

    async def get_customer_price(self, customer_id: str, product_id: str) -> Optional[float]:
        """
        Fetch customer-specific price from pricing matrix
        """
        matrix_entry = await self.matrix_collection.find_one({
            "customerId": customer_id,
            "itemCode": product_id,
            "isActive": True
        })

        if matrix_entry and "unitPrice" in matrix_entry:
            return float(matrix_entry["unitPrice"])

        return None

    def calculate_totals(self, monthly_forecasts: List[MonthlyForecast]) -> Dict[str, float]:
        """
        Calculate total quantity and revenue from monthly forecasts
        """
        total_quantity = 0.0
        total_revenue = 0.0

        for month_data in monthly_forecasts:
            total_quantity += month_data.quantity
            if month_data.revenue:
                total_revenue += month_data.revenue
            elif month_data.unitPrice:
                total_revenue += month_data.quantity * month_data.unitPrice

        return {
            "totalQuantity": total_quantity,
            "totalRevenue": round(total_revenue, 2)
        }

    async def apply_pricing_to_months(
        self,
        monthly_forecasts: List[MonthlyForecast],
        use_customer_price: bool,
        customer_id: str,
        product_id: str,
        override_price: Optional[float] = None
    ) -> List[MonthlyForecast]:
        """
        Apply pricing to monthly forecasts
        - If useCustomerPrice=True, fetch from matrix
        - If useCustomerPrice=False and overridePrice provided, use override
        - Calculate revenue for each month
        """
        # Determine which price to use
        unit_price = None

        if use_customer_price:
            unit_price = await self.get_customer_price(customer_id, product_id)
            if unit_price is None:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail=f"No customer-specific price found for customer {customer_id} and product {product_id}. Please provide an override price."
                )
        elif override_price is not None:
            unit_price = override_price
        else:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Either enable customer pricing or provide an override price."
            )

        # Apply pricing to each month
        updated_months = []
        for month_data in monthly_forecasts:
            month_dict = month_data.model_dump()
            month_dict["unitPrice"] = unit_price
            month_dict["revenue"] = round(month_data.quantity * unit_price, 2)
            updated_months.append(MonthlyForecast(**month_dict))

        return updated_months

    async def create_forecast(
        self,
        forecast_data: ForecastCreate,
        sales_rep_id: str
    ) -> ForecastInDB:
        """
        Create a new forecast
        - Validates cycle is open
        - Applies pricing
        - Calculates totals
        """
        # Validate cycle exists and is open
        try:
            cycle = await self.cycles_collection.find_one({"_id": ObjectId(forecast_data.cycleId)})
        except:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Invalid cycle ID format"
            )

        if not cycle:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="S&OP cycle not found"
            )

        if cycle.get("status") != CycleStatus.OPEN:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Cannot create forecast for cycle in {cycle.get('status')} status. Cycle must be OPEN."
            )

        # Check if forecast already exists for this combination
        existing = await self.collection.find_one({
            "cycleId": forecast_data.cycleId,
            "customerId": forecast_data.customerId,
            "productId": forecast_data.productId,
            "salesRepId": sales_rep_id,
            "status": {"$ne": ForecastStatus.REJECTED}  # Allow recreation if rejected
        })

        if existing:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Forecast already exists for this cycle/customer/product combination. Use update endpoint instead."
            )

        # Apply pricing to monthly forecasts
        monthly_forecasts_with_pricing = await self.apply_pricing_to_months(
            forecast_data.monthlyForecasts,
            forecast_data.useCustomerPrice,
            forecast_data.customerId,
            forecast_data.productId,
            forecast_data.overridePrice
        )

        # Calculate totals
        totals = self.calculate_totals(monthly_forecasts_with_pricing)

        # Create forecast document
        forecast_doc = {
            "cycleId": forecast_data.cycleId,
            "customerId": forecast_data.customerId,
            "productId": forecast_data.productId,
            "salesRepId": sales_rep_id,
            "status": ForecastStatus.DRAFT,
            "monthlyForecasts": [m.model_dump() for m in monthly_forecasts_with_pricing],
            "useCustomerPrice": forecast_data.useCustomerPrice,
            "overridePrice": forecast_data.overridePrice,
            "totalQuantity": totals["totalQuantity"],
            "totalRevenue": totals["totalRevenue"],
            "version": 1,
            "previousVersionId": None,
            "notes": forecast_data.notes,
            "createdAt": datetime.utcnow(),
            "updatedAt": datetime.utcnow(),
            "submittedAt": None
        }

        result = await self.collection.insert_one(forecast_doc)
        forecast_doc["_id"] = str(result.inserted_id)

        return ForecastInDB(**forecast_doc)

    async def get_forecast_by_id(self, forecast_id: str) -> Optional[ForecastInDB]:
        """Get forecast by ID"""
        try:
            forecast_doc = await self.collection.find_one({"_id": ObjectId(forecast_id)})
            if forecast_doc:
                forecast_doc["_id"] = str(forecast_doc["_id"])
                return ForecastInDB(**forecast_doc)
            return None
        except:
            return None

    async def update_forecast(
        self,
        forecast_id: str,
        forecast_update: ForecastUpdate,
        sales_rep_id: str
    ) -> ForecastInDB:
        """
        Update an existing forecast
        - Validates forecast is in DRAFT status
        - Prevents editing after submission
        - Recalculates pricing and totals
        """
        forecast = await self.get_forecast_by_id(forecast_id)
        if not forecast:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Forecast not found"
            )

        # Verify ownership
        if forecast.salesRepId != sales_rep_id:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="You can only update your own forecasts"
            )

        # Prevent editing after submission
        if forecast.status != ForecastStatus.DRAFT:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Cannot edit forecast in {forecast.status} status. Only DRAFT forecasts can be edited."
            )

        # Build update document
        update_data = {}

        if forecast_update.monthlyForecasts is not None:
            # Reapply pricing
            use_customer_price = forecast_update.useCustomerPrice if forecast_update.useCustomerPrice is not None else forecast.useCustomerPrice
            override_price = forecast_update.overridePrice if forecast_update.overridePrice is not None else forecast.overridePrice

            monthly_forecasts_with_pricing = await self.apply_pricing_to_months(
                forecast_update.monthlyForecasts,
                use_customer_price,
                forecast.customerId,
                forecast.productId,
                override_price
            )

            # Calculate totals
            totals = self.calculate_totals(monthly_forecasts_with_pricing)

            update_data["monthlyForecasts"] = [m.model_dump() for m in monthly_forecasts_with_pricing]
            update_data["totalQuantity"] = totals["totalQuantity"]
            update_data["totalRevenue"] = totals["totalRevenue"]

        if forecast_update.useCustomerPrice is not None:
            update_data["useCustomerPrice"] = forecast_update.useCustomerPrice

        if forecast_update.overridePrice is not None:
            update_data["overridePrice"] = forecast_update.overridePrice

        if forecast_update.notes is not None:
            update_data["notes"] = forecast_update.notes

        if update_data:
            update_data["updatedAt"] = datetime.utcnow()
            await self.collection.update_one(
                {"_id": ObjectId(forecast_id)},
                {"$set": update_data}
            )

        return await self.get_forecast_by_id(forecast_id)

    async def submit_forecast(self, forecast_id: str, sales_rep_id: str) -> ForecastInDB:
        """
        Submit a forecast for review/approval
        - Validates forecast is in DRAFT status
        - Validates at least 12 months of forecast data (mandatory check)
        - Changes status to SUBMITTED
        """
        forecast = await self.get_forecast_by_id(forecast_id)
        if not forecast:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Forecast not found"
            )

        # Verify ownership
        if forecast.salesRepId != sales_rep_id:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="You can only submit your own forecasts"
            )

        # Validate status
        if forecast.status != ForecastStatus.DRAFT:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Cannot submit forecast in {forecast.status} status. Only DRAFT forecasts can be submitted."
            )

        # MANDATORY CHECK: At least 12 months of forecast data with quantity > 0
        future_months_with_data = [
            m for m in forecast.monthlyForecasts
            if m.isFuture and m.quantity > 0
        ]

        if len(future_months_with_data) < 12:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Forecast submission requires at least 12 months of forecast data. Currently have {len(future_months_with_data)} months with quantities."
            )

        # Update status to SUBMITTED
        update_data = {
            "status": ForecastStatus.SUBMITTED,
            "submittedAt": datetime.utcnow(),
            "updatedAt": datetime.utcnow()
        }

        await self.collection.update_one(
            {"_id": ObjectId(forecast_id)},
            {"$set": update_data}
        )

        # Update cycle statistics
        await self._update_cycle_stats(forecast.cycleId)

        return await self.get_forecast_by_id(forecast_id)

    async def _update_cycle_stats(self, cycle_id: str):
        """Update cycle submission statistics after forecast submission"""
        # This will trigger the cycle service to recalculate stats
        # For now, we'll just mark it as a TODO for the cycle to auto-refresh
        pass

    async def list_forecasts(
        self,
        skip: int = 0,
        limit: int = 100,
        cycle_id: Optional[str] = None,
        sales_rep_id: Optional[str] = None,
        customer_id: Optional[str] = None,
        product_id: Optional[str] = None,
        status: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        List forecasts with filtering and pagination
        """
        query = {}

        if cycle_id:
            query["cycleId"] = cycle_id

        if sales_rep_id:
            query["salesRepId"] = sales_rep_id

        if customer_id:
            query["customerId"] = customer_id

        if product_id:
            query["productId"] = product_id

        if status:
            query["status"] = status

        # Get total count
        total = await self.collection.count_documents(query)

        # Get paginated forecasts
        cursor = self.collection.find(query).skip(skip).limit(limit).sort("createdAt", -1)
        forecasts = []
        async for forecast_doc in cursor:
            forecast_doc["_id"] = str(forecast_doc["_id"])
            forecasts.append(ForecastInDB(**forecast_doc))

        # Calculate pagination info
        total_pages = (total + limit - 1) // limit if limit > 0 else 1
        current_page = (skip // limit) + 1 if limit > 0 else 1

        return {
            "forecasts": forecasts,
            "total": total,
            "page": current_page,
            "pageSize": limit,
            "totalPages": total_pages,
            "hasNext": skip + limit < total,
            "hasPrev": skip > 0
        }

    async def delete_forecast(self, forecast_id: str, sales_rep_id: str) -> bool:
        """
        Delete a forecast (only if in DRAFT status)
        """
        forecast = await self.get_forecast_by_id(forecast_id)
        if not forecast:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Forecast not found"
            )

        # Verify ownership
        if forecast.salesRepId != sales_rep_id:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="You can only delete your own forecasts"
            )

        # Only allow deletion of draft forecasts
        if forecast.status != ForecastStatus.DRAFT:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Cannot delete forecast in {forecast.status} status. Only DRAFT forecasts can be deleted."
            )

        result = await self.collection.delete_one({"_id": ObjectId(forecast_id)})
        return result.deleted_count > 0

    async def get_forecast_statistics(self, cycle_id: str) -> Dict[str, Any]:
        """
        Get forecast statistics for a specific cycle
        - Total forecasts
        - Submitted vs draft
        - Total quantity and revenue
        """
        pipeline = [
            {"$match": {"cycleId": cycle_id}},
            {
                "$group": {
                    "_id": "$status",
                    "count": {"$sum": 1},
                    "totalQuantity": {"$sum": "$totalQuantity"},
                    "totalRevenue": {"$sum": "$totalRevenue"}
                }
            }
        ]

        results = await self.collection.aggregate(pipeline).to_list(length=100)

        stats = {
            "totalForecasts": 0,
            "draftForecasts": 0,
            "submittedForecasts": 0,
            "approvedForecasts": 0,
            "rejectedForecasts": 0,
            "totalQuantity": 0,
            "totalRevenue": 0
        }

        for item in results:
            status_value = item["_id"]
            count = item["count"]

            stats["totalForecasts"] += count

            if status_value == ForecastStatus.DRAFT:
                stats["draftForecasts"] = count
            elif status_value == ForecastStatus.SUBMITTED:
                stats["submittedForecasts"] = count
                stats["totalQuantity"] += item["totalQuantity"]
                stats["totalRevenue"] += item["totalRevenue"]
            elif status_value == ForecastStatus.APPROVED:
                stats["approvedForecasts"] = count
                stats["totalQuantity"] += item["totalQuantity"]
                stats["totalRevenue"] += item["totalRevenue"]
            elif status_value == ForecastStatus.REJECTED:
                stats["rejectedForecasts"] = count

        stats["totalRevenue"] = round(stats["totalRevenue"], 2)

        return stats
