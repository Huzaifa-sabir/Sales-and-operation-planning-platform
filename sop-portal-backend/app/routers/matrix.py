"""
Product-Customer Matrix Router
Handles product-customer matrix CRUD operations
"""
from typing import Optional
from fastapi import APIRouter, Depends, HTTPException, status, Query
from motor.motor_asyncio import AsyncIOMotorDatabase

from app.config.database import get_db
from app.models.product_customer_matrix import (
    ProductCustomerMatrixInDB,
    ProductCustomerMatrixResponse,
    ProductCustomerMatrixCreate,
    ProductCustomerMatrixUpdate
)
from app.schemas.matrix_schemas import (
    MatrixCreateRequest,
    MatrixUpdateRequest,
    MatrixListResponse,
    BulkMatrixCreateRequest,
    BulkMatrixCreateResponse,
    MessageResponse
)
from app.services.matrix_service import MatrixService
from app.utils.auth_dependencies import require_admin, get_current_active_user
from app.models.user import UserInDB

router = APIRouter(prefix="/matrix", tags=["Product-Customer Matrix"])


@router.post(
    "",
    response_model=ProductCustomerMatrixResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Create a matrix entry",
    description="Create a new product-customer matrix entry. Admin only."
)
async def create_matrix_entry(
    matrix_data: MatrixCreateRequest,
    db: AsyncIOMotorDatabase = Depends(get_db),
    current_user: UserInDB = Depends(require_admin)
):
    """
    Create a new product-customer matrix entry (Admin only)

    - **customerId**: Customer ID
    - **productId**: Product item code
    - **customerPrice**: Customer-specific price (optional)
    - **minimumOrderQty**: Minimum order quantity (optional)
    - **maximumOrderQty**: Maximum order quantity (optional)
    - **leadTimeDays**: Lead time in days (optional)
    """
    matrix_service = MatrixService(db)

    # Get customer and product info to populate required fields
    customer = await matrix_service.customers_collection.find_one({"customerId": matrix_data.customerId})
    if not customer:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Customer '{matrix_data.customerId}' not found"
        )
    
    product = await matrix_service.products_collection.find_one({"itemCode": matrix_data.productId})
    if not product:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Product '{matrix_data.productId}' not found"
        )

    # Convert request to MatrixCreate model with required fields
    matrix_create_data = matrix_data.model_dump()
    # Map customerPrice to customerSpecificPrice if provided
    if "customerPrice" in matrix_create_data:
        matrix_create_data["customerSpecificPrice"] = matrix_create_data.pop("customerPrice")
    
    matrix_create_data["customerName"] = customer.get("customerName", customer.get("customerId", ""))
    matrix_create_data["productCode"] = product.get("itemCode", matrix_data.productId)
    matrix_create_data["productDescription"] = product.get("itemDescription", product.get("description", ""))
    
    matrix_create = ProductCustomerMatrixCreate(**matrix_create_data)

    created_matrix = await matrix_service.create_matrix_entry(matrix_create)

    # Convert to MatrixResponse
    return ProductCustomerMatrixResponse(
        id=created_matrix.id,
        customerId=created_matrix.customerId,
        customerName=created_matrix.customerName,
        productId=created_matrix.productId,
        productCode=created_matrix.productCode,
        productDescription=created_matrix.productDescription,
        isActive=created_matrix.isActive,
        customerSpecificPrice=created_matrix.customerSpecificPrice,
        lastOrderDate=created_matrix.lastOrderDate,
        totalOrdersQty=created_matrix.totalOrdersQty,
        notes=created_matrix.notes,
        createdAt=created_matrix.createdAt,
        updatedAt=created_matrix.updatedAt
    )


@router.post(
    "/bulk",
    response_model=BulkMatrixCreateResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Bulk create matrix entries",
    description="Create multiple product-customer matrix entries at once. Admin only."
)
async def bulk_create_matrix_entries(
    bulk_data: BulkMatrixCreateRequest,
    db: AsyncIOMotorDatabase = Depends(get_db),
    current_user: UserInDB = Depends(require_admin)
):
    """
    Bulk create product-customer matrix entries (Admin only)

    - **entries**: List of matrix entries to create
    """
    matrix_service = MatrixService(db)

    # Convert requests to MatrixCreate models, populating required fields
    matrix_creates = []
    for entry in bulk_data.entries:
        # Get customer and product info
        customer = await matrix_service.customers_collection.find_one({"customerId": entry.customerId})
        if not customer:
            continue
        
        product = await matrix_service.products_collection.find_one({"itemCode": entry.productId})
        if not product:
            continue
        
        # Build matrix create data with required fields
        matrix_create_data = entry.model_dump()
        # Map customerPrice to customerSpecificPrice if provided
        if "customerPrice" in matrix_create_data:
            matrix_create_data["customerSpecificPrice"] = matrix_create_data.pop("customerPrice")
        
        matrix_create_data["customerName"] = customer.get("customerName", customer.get("customerId", ""))
        matrix_create_data["productCode"] = product.get("itemCode", entry.productId)
        matrix_create_data["productDescription"] = product.get("itemDescription", product.get("description", ""))
        
        matrix_creates.append(ProductCustomerMatrixCreate(**matrix_create_data))

    result = await matrix_service.bulk_create_matrix_entries(matrix_creates)

    # Convert created entries to MatrixResponse
    created_responses = [
        ProductCustomerMatrixResponse(
            id=entry.id,
            customerId=entry.customerId,
            customerName=entry.customerName,
            productId=entry.productId,
            productCode=entry.productCode,
            productDescription=entry.productDescription,
            isActive=entry.isActive,
            customerSpecificPrice=entry.customerSpecificPrice,
            lastOrderDate=entry.lastOrderDate,
            totalOrdersQty=entry.totalOrdersQty,
            notes=entry.notes,
            createdAt=entry.createdAt,
            updatedAt=entry.updatedAt
        )
        for entry in result["created"]
    ]

    return BulkMatrixCreateResponse(
        created=created_responses,
        failed=result["failed"],
        totalCreated=result["totalCreated"],
        totalFailed=result["totalFailed"]
    )


@router.get(
    "",
    response_model=MatrixListResponse,
    summary="List matrix entries",
    description="Get paginated list of matrix entries with optional filtering"
)
async def list_matrix_entries(
    page: int = Query(default=1, ge=1, description="Page number"),
    pageSize: int = Query(default=10, ge=1, le=100, description="Items per page"),
    customerId: Optional[str] = Query(None, description="Filter by customer ID"),
    productId: Optional[str] = Query(None, description="Filter by product ID"),
    isActive: Optional[bool] = Query(None, description="Filter by active status"),
    db: AsyncIOMotorDatabase = Depends(get_db),
    current_user: UserInDB = Depends(get_current_active_user)
):
    """
    List matrix entries with pagination and filtering

    - **page**: Page number (default: 1)
    - **pageSize**: Items per page (default: 10, max: 100)
    - **customerId**: Filter by customer (optional)
    - **productId**: Filter by product (optional)
    - **isActive**: Filter by active status (optional)
    """
    matrix_service = MatrixService(db)

    skip = (page - 1) * pageSize

    result = await matrix_service.list_matrix_entries(
        skip=skip,
        limit=pageSize,
        customer_id=customerId,
        product_id=productId,
        is_active=isActive
    )

    # Convert entries to MatrixResponse
    matrix_responses = [
        ProductCustomerMatrixResponse(
            id=entry.id,
            customerId=entry.customerId,
            customerName=entry.customerName,
            productId=entry.productId,
            productCode=entry.productCode,
            productDescription=entry.productDescription,
            isActive=entry.isActive,
            customerSpecificPrice=entry.customerSpecificPrice,
            lastOrderDate=entry.lastOrderDate,
            totalOrdersQty=entry.totalOrdersQty,
            notes=entry.notes,
            createdAt=entry.createdAt,
            updatedAt=entry.updatedAt
        )
        for entry in result["entries"]
    ]

    return MatrixListResponse(
        entries=matrix_responses,
        total=result["total"],
        page=result["page"],
        pageSize=result["pageSize"],
        totalPages=result["totalPages"],
        hasNext=result["hasNext"],
        hasPrev=result["hasPrev"]
    )


@router.get(
    "/{matrix_id}",
    response_model=ProductCustomerMatrixResponse,
    summary="Get matrix entry by ID",
    description="Get a specific matrix entry by ID"
)
async def get_matrix_entry(
    matrix_id: str,
    db: AsyncIOMotorDatabase = Depends(get_db),
    current_user: UserInDB = Depends(get_current_active_user)
):
    """Get matrix entry by ID"""
    matrix_service = MatrixService(db)
    matrix_entry = await matrix_service.get_matrix_entry_by_id(matrix_id)

    if not matrix_entry:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Matrix entry not found"
        )

    return ProductCustomerMatrixResponse(
        id=matrix_entry.id,
        customerId=matrix_entry.customerId,
        customerName=matrix_entry.customerName,
        productId=matrix_entry.productId,
        productCode=matrix_entry.productCode,
        productDescription=matrix_entry.productDescription,
        isActive=matrix_entry.isActive,
        customerSpecificPrice=matrix_entry.customerSpecificPrice,
        lastOrderDate=matrix_entry.lastOrderDate,
        totalOrdersQty=matrix_entry.totalOrdersQty,
        notes=matrix_entry.notes,
        createdAt=matrix_entry.createdAt,
        updatedAt=matrix_entry.updatedAt
    )


@router.put(
    "/{matrix_id}",
    response_model=ProductCustomerMatrixResponse,
    summary="Update matrix entry",
    description="Update matrix entry information. Admin only."
)
async def update_matrix_entry(
    matrix_id: str,
    matrix_update: MatrixUpdateRequest,
    db: AsyncIOMotorDatabase = Depends(get_db),
    current_user: UserInDB = Depends(require_admin)
):
    """Update matrix entry (Admin only)"""
    matrix_service = MatrixService(db)

    # Convert request to MatrixUpdate model, mapping customerPrice to customerSpecificPrice
    update_dict = matrix_update.model_dump(exclude_unset=True)
    if "customerPrice" in update_dict:
        update_dict["customerSpecificPrice"] = update_dict.pop("customerPrice")
    
    update_data = ProductCustomerMatrixUpdate(**update_dict)

    updated_matrix = await matrix_service.update_matrix_entry(matrix_id, update_data)

    if not updated_matrix:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Matrix entry not found"
        )

    return ProductCustomerMatrixResponse(
        id=updated_matrix.id,
        customerId=updated_matrix.customerId,
        customerName=updated_matrix.customerName,
        productId=updated_matrix.productId,
        productCode=updated_matrix.productCode,
        productDescription=updated_matrix.productDescription,
        isActive=updated_matrix.isActive,
        customerSpecificPrice=updated_matrix.customerSpecificPrice,
        lastOrderDate=updated_matrix.lastOrderDate,
        totalOrdersQty=updated_matrix.totalOrdersQty,
        notes=updated_matrix.notes,
        createdAt=updated_matrix.createdAt,
        updatedAt=updated_matrix.updatedAt
    )


@router.patch(
    "/{matrix_id}/toggle-status",
    response_model=ProductCustomerMatrixResponse,
    summary="Toggle matrix entry status",
    description="Toggle matrix entry active/inactive status. Admin only."
)
async def toggle_matrix_status(
    matrix_id: str,
    db: AsyncIOMotorDatabase = Depends(get_db),
    current_user: UserInDB = Depends(require_admin)
):
    """Toggle matrix entry active/inactive status (Admin only)"""
    matrix_service = MatrixService(db)
    updated_matrix = await matrix_service.toggle_matrix_status(matrix_id)

    if not updated_matrix:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Matrix entry not found"
        )

    return ProductCustomerMatrixResponse(
        id=updated_matrix.id,
        customerId=updated_matrix.customerId,
        customerName=updated_matrix.customerName,
        productId=updated_matrix.productId,
        productCode=updated_matrix.productCode,
        productDescription=updated_matrix.productDescription,
        isActive=updated_matrix.isActive,
        customerSpecificPrice=updated_matrix.customerSpecificPrice,
        lastOrderDate=updated_matrix.lastOrderDate,
        totalOrdersQty=updated_matrix.totalOrdersQty,
        notes=updated_matrix.notes,
        createdAt=updated_matrix.createdAt,
        updatedAt=updated_matrix.updatedAt
    )


@router.delete(
    "/{matrix_id}",
    response_model=MessageResponse,
    summary="Delete matrix entry",
    description="Delete a matrix entry. Admin only."
)
async def delete_matrix_entry(
    matrix_id: str,
    db: AsyncIOMotorDatabase = Depends(get_db),
    current_user: UserInDB = Depends(require_admin)
):
    """Delete a matrix entry (Admin only)"""
    matrix_service = MatrixService(db)
    success = await matrix_service.delete_matrix_entry(matrix_id)

    if not success:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Matrix entry not found"
        )

    return MessageResponse(
        message="Matrix entry deleted successfully",
        success=True
    )
