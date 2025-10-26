"""
Sales History Router
Handles sales history data retrieval, filtering, and analytics
"""
from typing import Optional, List
from datetime import datetime
from fastapi import APIRouter, Depends, Query, HTTPException, status
from motor.motor_asyncio import AsyncIOMotorDatabase

from app.config.database import get_db
from app.schemas.sales_history_schemas import (
    SalesHistoryListResponse,
    SalesStatisticsResponse,
    MonthlySalesResponse,
    TopProductResponse,
    TopCustomerResponse,
    SalesHistoryCreateRequest,
    SalesHistoryUpdateRequest
)
from app.models.sales_history import SalesHistoryResponse, SalesHistoryCreate, SalesHistoryUpdate
from app.services.sales_history_service import SalesHistoryService
from app.utils.auth_dependencies import get_current_active_user, require_admin
from app.models.user import UserInDB

router = APIRouter(prefix="/sales-history", tags=["Sales History"])


@router.get(
    "",
    response_model=SalesHistoryListResponse,
    summary="Get sales history",
    description="Get sales history with filtering by customer, product, date range"
)
async def get_sales_history(
    skip: int = Query(default=0, ge=0, description="Number of records to skip"),
    limit: int = Query(default=100, ge=1, le=1000, description="Number of records to return"),
    page: Optional[int] = Query(None, ge=1, description="Page number (alternative to skip/limit)"),
    pageSize: Optional[int] = Query(None, ge=1, le=1000, description="Items per page (alternative to skip/limit)"),
    customerId: Optional[str] = Query(None, description="Filter by customer ID"),
    productId: Optional[str] = Query(None, description="Filter by product ID (item code)"),
    year: Optional[int] = Query(None, description="Filter by year"),
    month: Optional[int] = Query(None, ge=1, le=12, description="Filter by month (1-12)"),
    db: AsyncIOMotorDatabase = Depends(get_db),
    current_user: UserInDB = Depends(get_current_active_user)
):
    """
    Get sales history with filtering options

    - **skip**: Number of records to skip (default: 0)
    - **limit**: Number of records to return (default: 100, max: 1000)
    - **page**: Page number (alternative to skip/limit, default: 1)
    - **pageSize**: Items per page (alternative to skip/limit, default: 100, max: 1000)
    - **customerId**: Filter by specific customer
    - **productId**: Filter by specific product
    - **year**: Filter by specific year
    - **month**: Filter by specific month (1-12)
    """
    sales_service = SalesHistoryService(db)

    # Support both skip/limit and page/pageSize
    if page is not None and pageSize is not None:
        skip = (page - 1) * pageSize
        limit = pageSize
    
    result = await sales_service.get_sales_history(
        skip=skip,
        limit=limit,
        customer_id=customerId,
        product_id=productId,
        year=year,
        month=month
    )

    return SalesHistoryListResponse(
        records=result["records"],
        total=result["total"],
        page=result["page"],
        pageSize=result["pageSize"],
        totalPages=result["totalPages"],
        hasNext=result["hasNext"],
        hasPrev=result["hasPrev"]
    )


@router.get(
    "/statistics",
    response_model=SalesStatisticsResponse,
    summary="Get sales statistics",
    description="Get aggregated sales statistics (totals, averages, etc.)"
)
async def get_sales_statistics(
    customerId: Optional[str] = Query(None, description="Filter by customer ID"),
    productId: Optional[str] = Query(None, description="Filter by product ID"),
    year: Optional[int] = Query(None, description="Filter by year"),
    month: Optional[int] = Query(None, ge=1, le=12, description="Filter by month (1-12)"),
    db: AsyncIOMotorDatabase = Depends(get_db),
    current_user: UserInDB = Depends(get_current_active_user)
):
    """
    Get aggregated sales statistics

    Returns total quantity, revenue, averages, and other metrics.
    Can be filtered by customer and/or product.
    """
    sales_service = SalesHistoryService(db)

    stats = await sales_service.get_sales_statistics(
        customer_id=customerId,
        product_id=productId,
        year=year,
        month=month
    )

    return SalesStatisticsResponse(**stats)


@router.get(
    "/by-month",
    response_model=List[MonthlySalesResponse],
    summary="Get sales by month",
    description="Get sales data aggregated by month (for charts)"
)
async def get_sales_by_month(
    customerId: Optional[str] = Query(None, description="Filter by customer ID"),
    productId: Optional[str] = Query(None, description="Filter by product ID"),
    months: int = Query(default=12, ge=1, le=24, description="Number of months to retrieve"),
    db: AsyncIOMotorDatabase = Depends(get_db),
    current_user: UserInDB = Depends(get_current_active_user)
):
    """
    Get sales data aggregated by month (for time-series charts)

    - **customerId**: Filter by specific customer
    - **productId**: Filter by specific product
    - **months**: Number of months to retrieve (default: 12, max: 24)

    Returns monthly totals sorted chronologically.
    """
    sales_service = SalesHistoryService(db)

    monthly_data = await sales_service.get_sales_by_month(
        customer_id=customerId,
        product_id=productId,
        months=months
    )

    return [MonthlySalesResponse(**item) for item in monthly_data]


@router.get(
    "/top-products",
    response_model=List[TopProductResponse],
    summary="Get top selling products",
    description="Get top products by total quantity sold"
)
async def get_top_products(
    customerId: Optional[str] = Query(None, description="Filter by customer ID"),
    limit: int = Query(default=10, ge=1, le=50, description="Number of top products to return"),
    months: int = Query(default=12, ge=1, le=24, description="Time period in months"),
    db: AsyncIOMotorDatabase = Depends(get_db),
    current_user: UserInDB = Depends(get_current_active_user)
):
    """
    Get top selling products

    - **customerId**: Filter by specific customer (optional)
    - **limit**: Number of top products to return (default: 10, max: 50)
    - **months**: Time period to analyze (default: 12 months)

    Returns products sorted by total quantity sold.
    """
    sales_service = SalesHistoryService(db)

    top_products = await sales_service.get_top_products(
        customer_id=customerId,
        limit=limit,
        months=months
    )

    return [TopProductResponse(**item) for item in top_products]


@router.get(
    "/top-customers",
    response_model=List[TopCustomerResponse],
    summary="Get top customers",
    description="Get top customers by total revenue"
)
async def get_top_customers(
    productId: Optional[str] = Query(None, description="Filter by product ID"),
    limit: int = Query(default=10, ge=1, le=50, description="Number of top customers to return"),
    months: int = Query(default=12, ge=1, le=24, description="Time period in months"),
    db: AsyncIOMotorDatabase = Depends(get_db),
    current_user: UserInDB = Depends(get_current_active_user)
):
    """
    Get top customers by revenue

    - **productId**: Filter by specific product (optional)
    - **limit**: Number of top customers to return (default: 10, max: 50)
    - **months**: Time period to analyze (default: 12 months)

    Returns customers sorted by total revenue.
    """
    sales_service = SalesHistoryService(db)

    top_customers = await sales_service.get_top_customers(
        product_id=productId,
        limit=limit,
        months=months
    )

    return [TopCustomerResponse(**item) for item in top_customers]


@router.get(
    "/{sales_id}",
    response_model=SalesHistoryResponse,
    summary="Get sales history record by ID",
    description="Get a specific sales history record by ID"
)
async def get_sales_record(
    sales_id: str,
    db: AsyncIOMotorDatabase = Depends(get_db),
    current_user: UserInDB = Depends(get_current_active_user)
):
    """Get a specific sales history record by ID"""
    sales_service = SalesHistoryService(db)

    record = await sales_service.get_by_id(sales_id)

    if not record:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Sales history record not found"
        )

    return SalesHistoryResponse(
        id=record.id,
        customerId=record.customerId,
        productId=record.productId,
        year=record.year,
        month=record.month,
        quantitySold=record.quantitySold,
        unitPrice=record.unitPrice,
        createdAt=record.createdAt,
        updatedAt=record.updatedAt
    )


@router.post(
    "",
    response_model=SalesHistoryResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Create sales history record",
    description="Create a new sales history record. Admin only."
)
async def create_sales_record(
    sales_data: SalesHistoryCreateRequest,
    db: AsyncIOMotorDatabase = Depends(get_db),
    current_user: UserInDB = Depends(require_admin)
):
    """
    Create a new sales history record (Admin only)

    - **customerId**: Customer ID (MongoDB ObjectId)
    - **productId**: Product ID (item code)
    - **year**: Year of the sale
    - **month**: Month of the sale (1-12)
    - **quantitySold**: Quantity sold
    - **unitPrice**: Unit price
    """
    sales_service = SalesHistoryService(db)

    # Convert request to create model
    sales_create = SalesHistoryCreate(
        customerId=sales_data.customerId,
        productId=sales_data.productId,
        year=sales_data.year,
        month=sales_data.month,
        quantitySold=sales_data.quantitySold,
        unitPrice=sales_data.unitPrice
    )

    created_record = await sales_service.create(sales_create)

    return SalesHistoryResponse(
        id=created_record.id,
        customerId=created_record.customerId,
        productId=created_record.productId,
        year=created_record.year,
        month=created_record.month,
        quantitySold=created_record.quantitySold,
        unitPrice=created_record.unitPrice,
        createdAt=created_record.createdAt,
        updatedAt=created_record.updatedAt
    )


@router.put(
    "/{sales_id}",
    response_model=SalesHistoryResponse,
    summary="Update sales history record",
    description="Update an existing sales history record. Admin only."
)
async def update_sales_record(
    sales_id: str,
    sales_data: SalesHistoryUpdateRequest,
    db: AsyncIOMotorDatabase = Depends(get_db),
    current_user: UserInDB = Depends(require_admin)
):
    """
    Update a sales history record (Admin only)

    All fields are optional. Only provided fields will be updated.
    """
    sales_service = SalesHistoryService(db)

    # Convert request to update model
    update_data = SalesHistoryUpdate(**sales_data.model_dump(exclude_unset=True))

    updated_record = await sales_service.update(sales_id, update_data)

    if not updated_record:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Sales history record not found"
        )

    return SalesHistoryResponse(
        id=updated_record.id,
        customerId=updated_record.customerId,
        productId=updated_record.productId,
        year=updated_record.year,
        month=updated_record.month,
        quantitySold=updated_record.quantitySold,
        unitPrice=updated_record.unitPrice,
        createdAt=updated_record.createdAt,
        updatedAt=updated_record.updatedAt
    )


@router.delete(
    "/{sales_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Delete sales history record",
    description="Delete a sales history record. Admin only."
)
async def delete_sales_record(
    sales_id: str,
    db: AsyncIOMotorDatabase = Depends(get_db),
    current_user: UserInDB = Depends(require_admin)
):
    """
    Delete a sales history record (Admin only)

    This is a hard delete and cannot be undone.
    """
    sales_service = SalesHistoryService(db)

    success = await sales_service.delete(sales_id)

    if not success:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Sales history record not found"
        )

    return None
