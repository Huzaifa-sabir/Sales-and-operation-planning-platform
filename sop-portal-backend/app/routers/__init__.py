"""
API Router aggregator
"""
from fastapi import APIRouter

from app.routers import auth, users, customers, products, matrix, excel, sales_history, sop_cycles, forecasts, reports, settings, audit_logs

# Create main API router
api_router = APIRouter()

# Include all sub-routers
api_router.include_router(auth.router)
api_router.include_router(users.router)
api_router.include_router(customers.router)
api_router.include_router(products.router)
api_router.include_router(matrix.router)
api_router.include_router(excel.router)
api_router.include_router(sales_history.router)
api_router.include_router(sop_cycles.router)
api_router.include_router(forecasts.router)
api_router.include_router(reports.router)
api_router.include_router(settings.router)
api_router.include_router(audit_logs.router)
