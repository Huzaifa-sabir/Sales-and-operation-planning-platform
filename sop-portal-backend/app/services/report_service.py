"""
Report Service - Phase 1
Implements core report generation with MongoDB aggregations
Includes: Sales Summary, Forecast vs Actual, Monthly Dashboard
"""
from typing import Optional, Dict, Any, List
from datetime import datetime, timedelta
from bson import ObjectId
from motor.motor_asyncio import AsyncIOMotorDatabase
from fastapi import HTTPException, status
import hashlib
import json

from app.models.report import ReportType, ReportStatus, ReportInDB, ReportFormat


class ReportService:
    """Service class for report generation and management"""

    def __init__(self, db: AsyncIOMotorDatabase):
        self.db = db
        self.reports_collection = db.reports
        self.sales_collection = db.sales_history  # Using sales_history collection
        self.forecasts_collection = db.forecasts
        self.customers_collection = db.customers
        self.products_collection = db.products
        self.cycles_collection = db.sop_cycles

    def _generate_cache_key(self, report_type: str, filters: Dict[str, Any]) -> str:
        """Generate cache key for report"""
        cache_data = f"{report_type}:{json.dumps(filters, sort_keys=True, default=str)}"
        return hashlib.md5(cache_data.encode()).hexdigest()

    async def get_cached_report(
        self,
        report_type: ReportType,
        filters: Dict[str, Any],
        max_age_hours: int = 24
    ) -> Optional[ReportInDB]:
        """Check if valid cached report exists"""
        cache_key = self._generate_cache_key(report_type.value, filters)
        cutoff_time = datetime.utcnow() - timedelta(hours=max_age_hours)

        cached_report = await self.reports_collection.find_one({
            "reportType": report_type.value,
            "cacheKey": cache_key,
            "status": ReportStatus.COMPLETED,
            "generatedAt": {"$gte": cutoff_time}
        })

        if cached_report:
            cached_report["_id"] = str(cached_report["_id"])
            return ReportInDB(**cached_report)

        return None

    async def create_report_metadata(
        self,
        report_type: ReportType,
        report_format: ReportFormat,
        filters: Dict[str, Any],
        options: Dict[str, Any],
        generated_by: str
    ) -> ReportInDB:
        """Create report metadata document"""
        cache_key = self._generate_cache_key(report_type.value, filters)
        expires_at = datetime.utcnow() + timedelta(days=7)  # Reports expire after 7 days

        report_doc = {
            "reportType": report_type.value,
            "format": report_format.value,
            "status": ReportStatus.PENDING,
            "cacheKey": cache_key,
            "filters": filters,
            "options": options,
            "fileName": None,
            "filePath": None,
            "fileSize": None,
            "downloadUrl": None,
            "generatedBy": generated_by,
            "generatedAt": None,
            "expiresAt": expires_at,
            "recordCount": None,
            "processingTime": None,
            "error": None,
            "createdAt": datetime.utcnow(),
            "updatedAt": datetime.utcnow()
        }

        result = await self.reports_collection.insert_one(report_doc)
        report_doc["_id"] = str(result.inserted_id)

        return ReportInDB(**report_doc)

    async def update_report_status(
        self,
        report_id: str,
        status: ReportStatus,
        **kwargs
    ) -> None:
        """Update report status and metadata"""
        update_data = {
            "status": status,
            "updatedAt": datetime.utcnow()
        }
        update_data.update(kwargs)

        await self.reports_collection.update_one(
            {"_id": ObjectId(report_id)},
            {"$set": update_data}
        )

    # ==========================================
    # REPORT 1: SALES SUMMARY
    # ==========================================
    async def generate_sales_summary_data(self, filters: Dict[str, Any]) -> Dict[str, Any]:
        """
        Generate Sales Summary Report Data
        - Total sales by customer/product/period
        - Sales trends
        - Top customers and products
        - Sales breakdowns
        """
        match_stage = self._build_sales_match_stage(filters)

        # Overall totals
        totals_pipeline = [
            {"$match": match_stage},
            {
                "$group": {
                    "_id": None,
                    "totalQuantity": {"$sum": "$quantity"},
                    "totalRevenue": {"$sum": "$totalSales"},
                    "transactionCount": {"$sum": 1},
                    "avgQuantity": {"$avg": "$quantity"},
                    "avgUnitPrice": {"$avg": "$unitPrice"}
                }
            }
        ]

        totals_result = await self.sales_collection.aggregate(totals_pipeline).to_list(1)
        totals = totals_result[0] if totals_result else {
            "totalQuantity": 0,
            "totalRevenue": 0,
            "transactionCount": 0,
            "avgQuantity": 0,
            "avgUnitPrice": 0
        }

        # Monthly trends
        monthly_trends_pipeline = [
            {"$match": match_stage},
            {
                "$group": {
                    "_id": {
                        "year": "$year",
                        "month": "$month"
                    },
                    "quantity": {"$sum": "$quantity"},
                    "revenue": {"$sum": "$totalSales"},
                    "transactions": {"$sum": 1}
                }
            },
            {
                "$sort": {"_id.year": 1, "_id.month": 1}
            },
            {"$limit": 24}  # Last 24 months
        ]

        monthly_trends = await self.sales_collection.aggregate(monthly_trends_pipeline).to_list(24)

        # Top 10 customers by revenue
        top_customers_pipeline = [
            {"$match": match_stage},
            {
                "$group": {
                    "_id": "$customerId",
                    "totalRevenue": {"$sum": "$totalSales"},
                    "totalQuantity": {"$sum": "$quantity"},
                    "transactions": {"$sum": 1}
                }
            },
            {"$sort": {"totalRevenue": -1}},
            {"$limit": 10}
        ]

        top_customers = await self.sales_collection.aggregate(top_customers_pipeline).to_list(10)

        # Enrich with customer names
        for customer in top_customers:
            customer_doc = await self.customers_collection.find_one({"customerId": customer["_id"]})
            customer["customerName"] = customer_doc["customerName"] if customer_doc else customer["_id"]

        # Top 10 products by volume
        top_products_pipeline = [
            {"$match": match_stage},
            {
                "$group": {
                    "_id": "$productId",
                    "totalQuantity": {"$sum": "$quantity"},
                    "totalRevenue": {"$sum": "$totalSales"},
                    "transactions": {"$sum": 1}
                }
            },
            {"$sort": {"totalQuantity": -1}},
            {"$limit": 10}
        ]

        top_products = await self.sales_collection.aggregate(top_products_pipeline).to_list(10)

        # Enrich with product descriptions
        for product in top_products:
            product_doc = await self.products_collection.find_one({"itemCode": product["_id"]})
            product["productDescription"] = product_doc["itemDescription"] if product_doc else product["_id"]

        return {
            "reportType": "Sales Summary",
            "generatedAt": datetime.utcnow().isoformat(),
            "filters": filters,
            "summary": {
                "totalQuantity": round(totals.get("totalQuantity", 0), 2),
                "totalRevenue": round(totals.get("totalRevenue", 0), 2),
                "transactionCount": totals.get("transactionCount", 0),
                "avgQuantity": round(totals.get("avgQuantity", 0), 2),
                "avgUnitPrice": round(totals.get("avgUnitPrice", 0), 2)
            },
            "monthlyTrends": [
                {
                    "year": item["_id"]["year"],
                    "month": item["_id"]["month"],
                    "monthLabel": f"{item['_id']['year']}-{str(item['_id']['month']).zfill(2)}",
                    "quantity": round(item["quantity"], 2),
                    "revenue": round(item["revenue"], 2),
                    "transactions": item["transactions"]
                }
                for item in monthly_trends
            ],
            "topCustomers": [
                {
                    "customerId": item["_id"],
                    "customerName": item["customerName"],
                    "totalRevenue": round(item["totalRevenue"], 2),
                    "totalQuantity": round(item["totalQuantity"], 2),
                    "transactions": item["transactions"]
                }
                for item in top_customers
            ],
            "topProducts": [
                {
                    "productId": item["_id"],
                    "productDescription": item["productDescription"],
                    "totalQuantity": round(item["totalQuantity"], 2),
                    "totalRevenue": round(item["totalRevenue"], 2),
                    "transactions": item["transactions"]
                }
                for item in top_products
            ]
        }

    # ==========================================
    # REPORT 2: FORECAST VS ACTUAL
    # ==========================================
    async def generate_forecast_vs_actual_data(self, filters: Dict[str, Any]) -> Dict[str, Any]:
        """
        Generate Forecast vs Actual Report Data
        - Variance analysis
        - Accuracy metrics
        - Over/under forecast identification
        """
        cycle_id = filters.get("cycleId")
        if not cycle_id:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="cycleId is required for Forecast vs Actual report"
            )

        # Get submitted forecasts for the cycle
        forecasts = await self.forecasts_collection.find({
            "cycleId": cycle_id,
            "status": {"$in": ["submitted", "approved"]}
        }).to_list(1000)

        variance_data = []
        total_forecast = 0
        total_actual = 0
        accurate_count = 0  # Within 10% variance

        for forecast in forecasts:
            # Get actual sales for same period
            for month_forecast in forecast.get("monthlyForecasts", []):
                if not month_forecast.get("isFuture"):  # Only compare historical/current months
                    continue

                actual_sales = await self.sales_collection.find_one({
                    "customerId": forecast["customerId"],
                    "productId": forecast["productId"],
                    "year": month_forecast["year"],
                    "month": month_forecast["month"]
                })

                forecast_qty = month_forecast.get("quantity", 0)
                actual_qty = actual_sales.get("quantity", 0) if actual_sales else 0

                variance = actual_qty - forecast_qty
                variance_pct = (variance / forecast_qty * 100) if forecast_qty > 0 else 0

                total_forecast += forecast_qty
                total_actual += actual_qty

                if abs(variance_pct) <= 10:
                    accurate_count += 1

                variance_data.append({
                    "customerId": forecast["customerId"],
                    "productId": forecast["productId"],
                    "year": month_forecast["year"],
                    "month": month_forecast["month"],
                    "monthLabel": month_forecast["monthLabel"],
                    "forecastQuantity": round(forecast_qty, 2),
                    "actualQuantity": round(actual_qty, 2),
                    "variance": round(variance, 2),
                    "variancePercent": round(variance_pct, 2),
                    "status": "Over" if variance < 0 else "Under" if variance > 0 else "Accurate"
                })

        overall_variance = total_actual - total_forecast
        overall_variance_pct = (overall_variance / total_forecast * 100) if total_forecast > 0 else 0
        accuracy_rate = (accurate_count / len(variance_data) * 100) if variance_data else 0

        return {
            "reportType": "Forecast vs Actual",
            "generatedAt": datetime.utcnow().isoformat(),
            "filters": filters,
            "summary": {
                "totalForecast": round(total_forecast, 2),
                "totalActual": round(total_actual, 2),
                "overallVariance": round(overall_variance, 2),
                "overallVariancePercent": round(overall_variance_pct, 2),
                "accuracyRate": round(accuracy_rate, 2),
                "recordCount": len(variance_data)
            },
            "varianceDetails": variance_data[:100]  # Limit to 100 records for summary
        }

    # ==========================================
    # REPORT 3: MONTHLY DASHBOARD
    # ==========================================
    async def generate_monthly_dashboard_data(self, filters: Dict[str, Any]) -> Dict[str, Any]:
        """
        Generate Monthly Dashboard Report Data
        - Current month KPIs
        - YTD performance
        - Top performers
        - Submission statistics
        """
        # Determine target month/year
        target_year = filters.get("year", datetime.now().year)
        target_month = filters.get("month", datetime.now().month)

        # Current month sales
        current_month_sales = await self.sales_collection.aggregate([
            {
                "$match": {
                    "year": target_year,
                    "month": target_month  # Fixed: use month instead of monthNum
                }
            },
            {
                "$group": {
                    "_id": None,
                    "totalRevenue": {"$sum": "$totalSales"},
                    "totalQuantity": {"$sum": "$quantity"},
                    "transactions": {"$sum": 1}
                }
            }
        ]).to_list(1)

        current_month = current_month_sales[0] if current_month_sales else {
            "totalRevenue": 0,
            "totalQuantity": 0,
            "transactions": 0
        }

        # YTD sales
        ytd_sales = await self.sales_collection.aggregate([
            {
                "$match": {
                    "year": target_year,
                    "month": {"$lte": target_month}  # Fixed: use month instead of monthNum
                }
            },
            {
                "$group": {
                    "_id": None,
                    "totalRevenue": {"$sum": "$totalSales"},
                    "totalQuantity": {"$sum": "$quantity"}
                }
            }
        ]).to_list(1)

        ytd = ytd_sales[0] if ytd_sales else {"totalRevenue": 0, "totalQuantity": 0}

        # Top 5 customers this month
        top_customers = await self.sales_collection.aggregate([
            {
                "$match": {
                    "year": target_year,
                    "month": target_month  # Fixed: use month instead of monthNum
                }
            },
            {
                "$group": {
                    "_id": "$customerId",
                    "revenue": {"$sum": {"$multiply": ["$quantity", "$unitPrice"]}}
                }
            },
            {"$sort": {"revenue": -1}},
            {"$limit": 5}
        ]).to_list(5)

        # Enrich with names
        for customer in top_customers:
            customer_doc = await self.customers_collection.find_one({"customerId": customer["_id"]})
            customer["customerName"] = customer_doc["customerName"] if customer_doc else customer["_id"]

        # Top 5 products this month
        top_products = await self.products_collection.aggregate([
            {
                "$lookup": {
                    "from": "sales_history",  # Using correct collection name
                    "let": {"itemCode": "$itemCode"},
                    "pipeline": [
                        {
                            "$match": {
                                "$expr": {
                                    "$and": [
                                        {"$eq": ["$productId", "$$itemCode"]},
                                        {"$eq": ["$year", target_year]},
                                        {"$eq": ["$month", target_month]}
                                    ]
                                }
                            }
                        },
                        {
                            "$group": {
                                "_id": None,
                                "quantity": {"$sum": "$quantity"}
                            }
                        }
                    ],
                    "as": "sales"
                }
            },
            {"$unwind": {"path": "$sales", "preserveNullAndEmptyArrays": False}},
            {
                "$project": {
                    "itemCode": 1,
                    "itemDescription": 1,
                    "quantity": "$sales.quantity"
                }
            },
            {"$sort": {"quantity": -1}},
            {"$limit": 5}
        ]).to_list(5)

        # Get active cycle submission stats
        active_cycle = await self.cycles_collection.find_one({"status": "open"})
        submission_stats = {"submissionRate": 0, "totalForecasts": 0, "submittedForecasts": 0}

        if active_cycle:
            submission_stats = {
                "cycleName": active_cycle.get("cycleName", "N/A"),
                "submissionRate": active_cycle.get("stats", {}).get("completionPercentage", 0),
                "totalForecasts": active_cycle.get("stats", {}).get("totalForecasts", 0),
                "submittedForecasts": active_cycle.get("stats", {}).get("submittedForecasts", 0)
            }

        return {
            "reportType": "Monthly Dashboard",
            "generatedAt": datetime.utcnow().isoformat(),
            "targetPeriod": f"{target_year}-{str(target_month).zfill(2)}",
            "currentMonth": {
                "revenue": round(current_month.get("totalRevenue", 0), 2),
                "quantity": round(current_month.get("totalQuantity", 0), 2),
                "transactions": current_month.get("transactions", 0)
            },
            "yearToDate": {
                "revenue": round(ytd.get("totalRevenue", 0), 2),
                "quantity": round(ytd.get("totalQuantity", 0), 2)
            },
            "topCustomers": [
                {
                    "customerId": c["_id"],
                    "customerName": c["customerName"],
                    "revenue": round(c["revenue"], 2)
                }
                for c in top_customers
            ],
            "topProducts": [
                {
                    "productId": p["itemCode"],
                    "productDescription": p["itemDescription"],
                    "quantity": round(p["quantity"], 2)
                }
                for p in top_products
            ],
            "forecastSubmission": submission_stats
        }

    # ==========================================
    # REPORT 4: CUSTOMER PERFORMANCE
    # ==========================================
    async def generate_customer_performance_data(self, filters: Dict[str, Any]) -> Dict[str, Any]:
        """
        Generate Customer Performance Report Data
        - Customer-wise sales analysis
        - Growth trends
        - Purchase frequency
        - Revenue contribution
        """
        match_stage = self._build_sales_match_stage(filters)

        # Customer summary pipeline
        customer_pipeline = [
            {"$match": match_stage},
            {
                "$group": {
                    "_id": "$customerId",
                    "totalRevenue": {"$sum": "$totalSales"},
                    "totalQuantity": {"$sum": "$quantity"},
                    "transactions": {"$sum": 1},
                    "avgOrderValue": {"$avg": {"$multiply": ["$quantity", "$unitPrice"]}},
                    "firstPurchase": {"$min": "$saleDate"},
                    "lastPurchase": {"$max": "$saleDate"},
                    "uniqueProducts": {"$addToSet": "$productId"}
                }
            },
            {"$sort": {"totalRevenue": -1}}
        ]

        customers = await self.sales_collection.aggregate(customer_pipeline).to_list(100)

        # Enrich with customer details
        for customer in customers:
            customer_doc = await self.customers_collection.find_one({"customerId": customer["_id"]})
            if customer_doc:
                customer["customerName"] = customer_doc["customerName"]
                customer["region"] = customer_doc.get("region", "N/A")
                customer["territory"] = customer_doc.get("territory", "N/A")
            else:
                customer["customerName"] = customer["_id"]
                customer["region"] = "N/A"
                customer["territory"] = "N/A"

            customer["productDiversity"] = len(customer.get("uniqueProducts", []))

        # Calculate total for percentage contribution
        total_revenue = sum(c["totalRevenue"] for c in customers)

        for customer in customers:
            customer["revenueContribution"] = (customer["totalRevenue"] / total_revenue * 100) if total_revenue > 0 else 0

        return {
            "reportType": "Customer Performance",
            "generatedAt": datetime.utcnow().isoformat(),
            "filters": filters,
            "summary": {
                "totalCustomers": len(customers),
                "totalRevenue": round(total_revenue, 2),
                "avgRevenuePerCustomer": round(total_revenue / len(customers), 2) if customers else 0
            },
            "customers": [
                {
                    "customerId": c["_id"],
                    "customerName": c["customerName"],
                    "region": c["region"],
                    "territory": c["territory"],
                    "totalRevenue": round(c["totalRevenue"], 2),
                    "totalQuantity": round(c["totalQuantity"], 2),
                    "transactions": c["transactions"],
                    "avgOrderValue": round(c["avgOrderValue"], 2),
                    "productDiversity": c["productDiversity"],
                    "revenueContribution": round(c["revenueContribution"], 2),
                    "firstPurchase": c["firstPurchase"].isoformat() if c.get("firstPurchase") else None,
                    "lastPurchase": c["lastPurchase"].isoformat() if c.get("lastPurchase") else None
                }
                for c in customers[:50]  # Top 50 customers
            ]
        }

    # ==========================================
    # REPORT 5: PRODUCT ANALYSIS
    # ==========================================
    async def generate_product_analysis_data(self, filters: Dict[str, Any]) -> Dict[str, Any]:
        """
        Generate Product Analysis Report Data
        - Product-wise sales performance
        - Best/worst performers
        - Category analysis
        - Velocity metrics
        """
        match_stage = self._build_sales_match_stage(filters)

        # Product summary pipeline
        product_pipeline = [
            {"$match": match_stage},
            {
                "$group": {
                    "_id": "$productId",
                    "totalQuantity": {"$sum": "$quantity"},
                    "totalRevenue": {"$sum": "$totalSales"},
                    "transactions": {"$sum": 1},
                    "avgPrice": {"$avg": "$unitPrice"},
                    "uniqueCustomers": {"$addToSet": "$customerId"}
                }
            },
            {"$sort": {"totalRevenue": -1}}
        ]

        products = await self.sales_collection.aggregate(product_pipeline).to_list(100)

        # Enrich with product details
        for product in products:
            product_doc = await self.products_collection.find_one({"itemCode": product["_id"]})
            if product_doc:
                product["itemDescription"] = product_doc["itemDescription"]
                product["category"] = product_doc.get("category", "N/A")
                product["unitOfMeasure"] = product_doc.get("unitOfMeasure", "N/A")
            else:
                product["itemDescription"] = product["_id"]
                product["category"] = "N/A"
                product["unitOfMeasure"] = "N/A"

            product["customerReach"] = len(product.get("uniqueCustomers", []))

        # Category analysis
        category_summary = {}
        for product in products:
            cat = product["category"]
            if cat not in category_summary:
                category_summary[cat] = {"revenue": 0, "quantity": 0, "products": 0}
            category_summary[cat]["revenue"] += product["totalRevenue"]
            category_summary[cat]["quantity"] += product["totalQuantity"]
            category_summary[cat]["products"] += 1

        total_revenue = sum(p["totalRevenue"] for p in products)

        return {
            "reportType": "Product Analysis",
            "generatedAt": datetime.utcnow().isoformat(),
            "filters": filters,
            "summary": {
                "totalProducts": len(products),
                "totalRevenue": round(total_revenue, 2),
                "totalCategories": len(category_summary)
            },
            "products": [
                {
                    "productId": p["_id"],
                    "itemDescription": p["itemDescription"],
                    "category": p["category"],
                    "unitOfMeasure": p["unitOfMeasure"],
                    "totalQuantity": round(p["totalQuantity"], 2),
                    "totalRevenue": round(p["totalRevenue"], 2),
                    "transactions": p["transactions"],
                    "avgPrice": round(p["avgPrice"], 2),
                    "customerReach": p["customerReach"]
                }
                for p in products[:50]  # Top 50 products
            ],
            "categoryBreakdown": [
                {
                    "category": cat,
                    "revenue": round(data["revenue"], 2),
                    "quantity": round(data["quantity"], 2),
                    "products": data["products"]
                }
                for cat, data in sorted(category_summary.items(), key=lambda x: x[1]["revenue"], reverse=True)
            ]
        }

    # ==========================================
    # REPORT 6: CYCLE SUBMISSION STATUS
    # ==========================================
    async def generate_cycle_submission_status_data(self, filters: Dict[str, Any]) -> Dict[str, Any]:
        """
        Generate Cycle Submission Status Report Data
        - Forecast submission tracking
        - Sales rep compliance
        - Pending forecasts
        - Submission timeline
        """
        cycle_id = filters.get("cycleId")
        if not cycle_id:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="cycleId is required for Cycle Submission Status report"
            )

        # Get cycle details
        cycle = await self.cycles_collection.find_one({"_id": ObjectId(cycle_id)})
        if not cycle:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="S&OP Cycle not found"
            )

        # Get all forecasts for this cycle
        forecasts = await self.forecasts_collection.find({"cycleId": cycle_id}).to_list(1000)

        # Group by sales rep
        sales_rep_summary = {}
        for forecast in forecasts:
            sales_rep_id = forecast.get("salesRepId", "Unknown")
            if sales_rep_id not in sales_rep_summary:
                sales_rep_summary[sales_rep_id] = {
                    "draft": 0,
                    "submitted": 0,
                    "approved": 0,
                    "rejected": 0,
                    "totalForecasts": 0,
                    "lastSubmission": None
                }

            status = forecast.get("status", "draft")
            sales_rep_summary[sales_rep_id][status] = sales_rep_summary[sales_rep_id].get(status, 0) + 1
            sales_rep_summary[sales_rep_id]["totalForecasts"] += 1

            if forecast.get("submittedAt") and (not sales_rep_summary[sales_rep_id]["lastSubmission"] or
                forecast["submittedAt"] > sales_rep_summary[sales_rep_id]["lastSubmission"]):
                sales_rep_summary[sales_rep_id]["lastSubmission"] = forecast["submittedAt"]

        # Calculate submission rate
        for sales_rep_id, data in sales_rep_summary.items():
            submitted_count = data.get("submitted", 0) + data.get("approved", 0)
            data["submissionRate"] = (submitted_count / data["totalForecasts"] * 100) if data["totalForecasts"] > 0 else 0

        # Overall statistics
        total_forecasts = len(forecasts)
        submitted_forecasts = sum(1 for f in forecasts if f.get("status") in ["submitted", "approved"])
        draft_forecasts = sum(1 for f in forecasts if f.get("status") == "draft")

        return {
            "reportType": "Cycle Submission Status",
            "generatedAt": datetime.utcnow().isoformat(),
            "filters": filters,
            "cycle": {
                "cycleId": str(cycle["_id"]),
                "cycleName": cycle.get("cycleName", "N/A"),
                "status": cycle.get("status", "N/A"),
                "startDate": cycle.get("startDate").isoformat() if cycle.get("startDate") else None,
                "endDate": cycle.get("endDate").isoformat() if cycle.get("endDate") else None
            },
            "summary": {
                "totalForecasts": total_forecasts,
                "submittedForecasts": submitted_forecasts,
                "draftForecasts": draft_forecasts,
                "submissionRate": round((submitted_forecasts / total_forecasts * 100) if total_forecasts > 0 else 0, 2)
            },
            "salesRepBreakdown": [
                {
                    "salesRepId": rep_id,
                    "totalForecasts": data["totalForecasts"],
                    "submitted": data.get("submitted", 0) + data.get("approved", 0),
                    "draft": data.get("draft", 0),
                    "submissionRate": round(data["submissionRate"], 2),
                    "lastSubmission": data["lastSubmission"].isoformat() if data["lastSubmission"] else None
                }
                for rep_id, data in sales_rep_summary.items()
            ]
        }

    # ==========================================
    # REPORT 7: GROSS PROFIT ANALYSIS
    # ==========================================
    async def generate_gross_profit_analysis_data(self, filters: Dict[str, Any]) -> Dict[str, Any]:
        """
        Generate Gross Profit Analysis Report Data
        - Margin analysis by product/customer
        - Profitability trends
        - Cost analysis
        """
        match_stage = self._build_sales_match_stage(filters)

        # Profit analysis pipeline (requires cost data from pricing matrix)
        profit_pipeline = [
            {"$match": match_stage},
            {
                "$lookup": {
                    "from": "pricing_matrix",
                    "let": {"customerId": "$customerId", "productId": "$productId"},
                    "pipeline": [
                        {
                            "$match": {
                                "$expr": {
                                    "$and": [
                                        {"$eq": ["$customerId", "$$customerId"]},
                                        {"$eq": ["$productId", "$$productId"]}
                                    ]
                                }
                            }
                        }
                    ],
                    "as": "pricing"
                }
            },
            {
                "$unwind": {
                    "path": "$pricing",
                    "preserveNullAndEmptyArrays": True
                }
            },
            {
                "$addFields": {
                    "cost": {"$ifNull": ["$pricing.cost", 0]},
                    "revenue": {"$multiply": ["$quantity", "$unitPrice"]},
                    "grossProfit": {
                        "$subtract": [
                            {"$multiply": ["$quantity", "$unitPrice"]},
                            {"$multiply": ["$quantity", {"$ifNull": ["$pricing.cost", 0]}]}
                        ]
                    },
                    "profitMargin": {
                        "$cond": {
                            "if": {"$gt": ["$unitPrice", 0]},
                            "then": {
                                "$multiply": [
                                    {
                                        "$divide": [
                                            {
                                                "$subtract": [
                                                    "$unitPrice",
                                                    {"$ifNull": ["$pricing.cost", 0]}
                                                ]
                                            },
                                            "$unitPrice"
                                        ]
                                    },
                                    100
                                ]
                            },
                            "else": 0
                        }
                    }
                }
            },
            {
                "$group": {
                    "_id": {
                        "customerId": "$customerId",
                        "productId": "$productId"
                    },
                    "totalRevenue": {"$sum": "$revenue"},
                    "totalCost": {"$sum": {"$multiply": ["$quantity", "$cost"]}},
                    "totalGrossProfit": {"$sum": "$grossProfit"},
                    "avgMargin": {"$avg": "$profitMargin"},
                    "quantity": {"$sum": "$quantity"}
                }
            },
            {"$sort": {"totalGrossProfit": -1}},
            {"$limit": 100}
        ]

        profit_data = await self.sales_collection.aggregate(profit_pipeline).to_list(100)

        # Enrich with names
        for item in profit_data:
            customer_doc = await self.customers_collection.find_one({"customerId": item["_id"]["customerId"]})
            product_doc = await self.products_collection.find_one({"itemCode": item["_id"]["productId"]})

            item["customerName"] = customer_doc["customerName"] if customer_doc else item["_id"]["customerId"]
            item["productDescription"] = product_doc["itemDescription"] if product_doc else item["_id"]["productId"]

        # Calculate totals
        total_revenue = sum(item["totalRevenue"] for item in profit_data)
        total_cost = sum(item["totalCost"] for item in profit_data)
        total_gross_profit = total_revenue - total_cost
        overall_margin = (total_gross_profit / total_revenue * 100) if total_revenue > 0 else 0

        return {
            "reportType": "Gross Profit Analysis",
            "generatedAt": datetime.utcnow().isoformat(),
            "filters": filters,
            "summary": {
                "totalRevenue": round(total_revenue, 2),
                "totalCost": round(total_cost, 2),
                "totalGrossProfit": round(total_gross_profit, 2),
                "overallMargin": round(overall_margin, 2)
            },
            "profitDetails": [
                {
                    "customerId": item["_id"]["customerId"],
                    "customerName": item["customerName"],
                    "productId": item["_id"]["productId"],
                    "productDescription": item["productDescription"],
                    "revenue": round(item["totalRevenue"], 2),
                    "cost": round(item["totalCost"], 2),
                    "grossProfit": round(item["totalGrossProfit"], 2),
                    "profitMargin": round(item["avgMargin"], 2),
                    "quantity": round(item["quantity"], 2)
                }
                for item in profit_data[:50]
            ]
        }

    # ==========================================
    # REPORT 8: FORECAST ACCURACY
    # ==========================================
    async def generate_forecast_accuracy_data(self, filters: Dict[str, Any]) -> Dict[str, Any]:
        """
        Generate Forecast Accuracy Report Data
        - Historical accuracy metrics
        - Sales rep performance
        - Accuracy trends
        - MAPE (Mean Absolute Percentage Error)
        """
        # Get historical forecasts (submitted/approved only)
        forecasts = await self.forecasts_collection.find({
            "status": {"$in": ["submitted", "approved"]}
        }).to_list(1000)

        accuracy_data = []
        total_mape = 0
        accurate_forecasts = 0
        total_comparisons = 0

        sales_rep_accuracy = {}

        for forecast in forecasts:
            sales_rep_id = forecast.get("salesRepId", "Unknown")
            if sales_rep_id not in sales_rep_accuracy:
                sales_rep_accuracy[sales_rep_id] = {
                    "totalForecasts": 0,
                    "accurateForecasts": 0,
                    "totalMAPE": 0,
                    "comparisons": 0
                }

            for month_forecast in forecast.get("monthlyForecasts", []):
                # Only compare historical data
                if month_forecast.get("isFuture"):
                    continue

                # Get actual sales for this month
                actual_sales = await self.sales_collection.find_one({
                    "customerId": forecast["customerId"],
                    "productId": forecast["productId"],
                    "year": month_forecast["year"],
                    "month": month_forecast["month"]
                })

                if not actual_sales:
                    continue

                forecast_qty = month_forecast.get("quantity", 0)
                actual_qty = actual_sales.get("quantity", 0)

                if forecast_qty == 0:
                    continue

                # Calculate MAPE
                ape = abs((actual_qty - forecast_qty) / forecast_qty) * 100
                total_mape += ape
                total_comparisons += 1

                sales_rep_accuracy[sales_rep_id]["totalMAPE"] += ape
                sales_rep_accuracy[sales_rep_id]["comparisons"] += 1

                # Accurate if within 10% variance
                is_accurate = ape <= 10
                if is_accurate:
                    accurate_forecasts += 1
                    sales_rep_accuracy[sales_rep_id]["accurateForecasts"] += 1

                accuracy_data.append({
                    "salesRepId": sales_rep_id,
                    "customerId": forecast["customerId"],
                    "productId": forecast["productId"],
                    "year": month_forecast["year"],
                    "month": month_forecast["month"],
                    "forecastQty": round(forecast_qty, 2),
                    "actualQty": round(actual_qty, 2),
                    "ape": round(ape, 2),
                    "isAccurate": is_accurate
                })

            sales_rep_accuracy[sales_rep_id]["totalForecasts"] += 1

        # Calculate metrics
        overall_mape = (total_mape / total_comparisons) if total_comparisons > 0 else 0
        overall_accuracy_rate = (accurate_forecasts / total_comparisons * 100) if total_comparisons > 0 else 0

        # Calculate sales rep metrics
        for rep_id, data in sales_rep_accuracy.items():
            data["avgMAPE"] = (data["totalMAPE"] / data["comparisons"]) if data["comparisons"] > 0 else 0
            data["accuracyRate"] = (data["accurateForecasts"] / data["comparisons"] * 100) if data["comparisons"] > 0 else 0

        return {
            "reportType": "Forecast Accuracy",
            "generatedAt": datetime.utcnow().isoformat(),
            "filters": filters,
            "summary": {
                "totalComparisons": total_comparisons,
                "overallMAPE": round(overall_mape, 2),
                "accuracyRate": round(overall_accuracy_rate, 2),
                "accurateForecasts": accurate_forecasts
            },
            "salesRepPerformance": [
                {
                    "salesRepId": rep_id,
                    "totalForecasts": data["totalForecasts"],
                    "comparisons": data["comparisons"],
                    "avgMAPE": round(data["avgMAPE"], 2),
                    "accuracyRate": round(data["accuracyRate"], 2)
                }
                for rep_id, data in sorted(sales_rep_accuracy.items(), key=lambda x: x[1]["accuracyRate"], reverse=True)
            ],
            "accuracyDetails": accuracy_data[:100]  # Limit to 100 for summary
        }

    # ==========================================
    # HELPER METHODS
    # ==========================================
    def _build_sales_match_stage(self, filters: Dict[str, Any]) -> Dict[str, Any]:
        """Build MongoDB match stage from filters"""
        match_stage = {}

        if filters.get("customerId"):
            match_stage["customerId"] = filters["customerId"]

        if filters.get("productId"):
            match_stage["productId"] = filters["productId"]

        if filters.get("year"):
            match_stage["year"] = filters["year"]

        if filters.get("month"):
            match_stage["month"] = filters["month"]  # Fixed: database uses month (integer)

        if filters.get("startDate") or filters.get("endDate"):
            # Date range logic
            pass

        return match_stage

    async def list_reports(
        self,
        skip: int = 0,
        limit: int = 20,
        user_id: Optional[str] = None,
        report_type: Optional[str] = None
    ) -> Dict[str, Any]:
        """List reports with pagination"""
        query = {}

        if user_id:
            query["generatedBy"] = user_id

        if report_type:
            query["reportType"] = report_type

        total = await self.reports_collection.count_documents(query)

        cursor = self.reports_collection.find(query).skip(skip).limit(limit).sort("createdAt", -1)
        reports = []
        async for report_doc in cursor:
            report_doc["_id"] = str(report_doc["_id"])
            reports.append(ReportInDB(**report_doc))

        total_pages = (total + limit - 1) // limit if limit > 0 else 1
        current_page = (skip // limit) + 1 if limit > 0 else 1

        return {
            "reports": reports,
            "total": total,
            "page": current_page,
            "pageSize": limit,
            "totalPages": total_pages,
            "hasNext": skip + limit < total,
            "hasPrev": skip > 0
        }

    async def get_report_by_id(self, report_id: str) -> Optional[ReportInDB]:
        """Get report by ID"""
        try:
            report_doc = await self.reports_collection.find_one({"_id": ObjectId(report_id)})
            if report_doc:
                report_doc["_id"] = str(report_doc["_id"])
                return ReportInDB(**report_doc)
            return None
        except:
            return None

    async def delete_report(self, report_id: str) -> bool:
        """Delete report and associated file"""
        report = await self.get_report_by_id(report_id)
        if not report:
            return False

        # Delete file if exists
        if report.filePath:
            import os
            try:
                if os.path.exists(report.filePath):
                    os.remove(report.filePath)
            except:
                pass

        # Delete from database
        result = await self.reports_collection.delete_one({"_id": ObjectId(report_id)})
        return result.deleted_count > 0
