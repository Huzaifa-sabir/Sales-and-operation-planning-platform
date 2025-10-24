"""
Product Management Router
Handles all product CRUD operations with customer-specific filtering
"""
from typing import Optional
from fastapi import APIRouter, Depends, HTTPException, status, Query
from motor.motor_asyncio import AsyncIOMotorDatabase

from app.config.database import get_db
from app.models.product import ProductInDB, ProductResponse, ProductCreate, ProductUpdate
from app.schemas.product_schemas import (
    ProductCreateRequest,
    ProductUpdateRequest,
    ProductListResponse,
    MessageResponse
)
from app.services.product_service import ProductService
from app.utils.auth_dependencies import require_admin, get_current_active_user
from app.models.user import UserInDB

router = APIRouter(prefix="/products", tags=["Product Management"])


@router.post(
    "",
    response_model=ProductResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Create a new product",
    description="Create a new product. Admin only."
)
async def create_product(
    product_data: ProductCreateRequest,
    db: AsyncIOMotorDatabase = Depends(get_db),
    current_user: UserInDB = Depends(require_admin)
):
    """
    Create a new product (Admin only)

    - **itemCode**: Unique item code (e.g., 110001)
    - **itemDescription**: Product description
    - **group**: Product group/category (optional)
    - **manufacturing**: Manufacturing details (optional)
    - **pricing**: Pricing information (optional)
    - **inventory**: Inventory details (optional)
    """
    product_service = ProductService(db)

    # Convert request to ProductCreate model
    product_create = ProductCreate(**product_data.model_dump())

    created_product = await product_service.create_product(product_create)

    # Convert to ProductResponse
    return ProductResponse(
        id=created_product.id,
        itemCode=created_product.itemCode,
        itemDescription=created_product.itemDescription,
        group=created_product.group,
        manufacturing=created_product.manufacturing,
        pricing=created_product.pricing,
        weight=created_product.weight,
        uom=created_product.uom,
        isActive=created_product.isActive,
        createdAt=created_product.createdAt,
        updatedAt=created_product.updatedAt
    )


@router.get(
    "",
    response_model=ProductListResponse,
    summary="List all products",
    description="Get paginated list of products with optional filtering. Supports customer-specific filtering."
)
async def list_products(
    page: int = Query(default=1, ge=1, description="Page number"),
    limit: int = Query(default=10, ge=1, le=100, description="Items per page", alias="limit"),
    pageSize: Optional[int] = Query(None, ge=1, le=100, description="Items per page (alternative param)"),
    isActive: Optional[bool] = Query(None, description="Filter by active status", alias="isActive"),
    is_active: Optional[bool] = Query(None, description="Filter by active status (alternative)"),
    search: Optional[str] = Query(None, description="Search in itemCode, itemDescription"),
    customerId: Optional[str] = Query(None, description="Filter by customer", alias="customerId"),
    customer_id: Optional[str] = Query(None, description="Filter by customer (alternative)"),
    group_code: Optional[str] = Query(None, description="Filter by group code"),
    groupCode: Optional[str] = Query(None, description="Filter by group code (alternative)", alias="groupCode"),
    location: Optional[str] = Query(None, description="Filter by manufacturing location"),
    db: AsyncIOMotorDatabase = Depends(get_db),
    current_user: UserInDB = Depends(get_current_active_user)
):
    """
    List products with pagination and filtering

    - **page**: Page number (default: 1)
    - **limit/pageSize**: Items per page (default: 10, max: 100)
    - **isActive/is_active**: Filter by active status (optional)
    - **search**: Search in product fields (optional)
    - **customerId/customer_id**: Filter by customer - returns only products available for this customer with customer-specific pricing (optional)
    - **groupCode/group_code**: Filter by group code (optional)
    - **location**: Filter by manufacturing location (optional)
    """
    try:
        product_service = ProductService(db)

        # Use limit if provided, otherwise use pageSize
        items_per_page = limit if limit != 10 else (pageSize or limit)

        # Use the provided parameter (priority to camelCase)
        active_filter = isActive if isActive is not None else is_active
        customer_filter = customerId if customerId else customer_id
        group_filter = groupCode if groupCode else group_code

        skip = (page - 1) * items_per_page

        result = await product_service.list_products(
            skip=skip,
            limit=items_per_page,
            is_active=active_filter,
            search=search,
            customer_id=customer_filter,
            group_code=group_filter,
            location=location
        )

        # Convert products to ProductResponse
        product_responses = [
            ProductResponse(
                id=product.id,
                itemCode=product.itemCode,
                itemDescription=product.itemDescription,
                group=product.group,
                manufacturing=product.manufacturing,
                pricing=product.pricing,
                weight=product.weight,
                uom=product.uom,
                isActive=product.isActive,
                createdAt=product.createdAt,
                updatedAt=product.updatedAt
            )
            for product in result["products"]
        ]

        return ProductListResponse(
            products=product_responses,
            total=result["total"],
            page=result["page"],
            pageSize=result["pageSize"],
            totalPages=result["totalPages"],
            hasNext=result["hasNext"],
            hasPrev=result["hasPrev"]
        )
    except Exception as e:
        # Log the error for debugging
        import logging
        logger = logging.getLogger(__name__)
        logger.error(f"Error listing products: {str(e)}", exc_info=True)

        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to list products: {str(e)}"
        )


@router.get(
    "/active",
    response_model=list[ProductResponse],
    summary="Get all active products",
    description="Get all active products (for dropdowns, etc.). Supports customer-specific filtering."
)
async def get_active_products(
    customerId: Optional[str] = Query(None, description="Filter by customer"),
    db: AsyncIOMotorDatabase = Depends(get_db),
    current_user: UserInDB = Depends(get_current_active_user)
):
    """
    Get all active products (useful for dropdowns)

    - **customerId**: If provided, returns only products available for this customer with customer-specific pricing
    """
    product_service = ProductService(db)
    products = await product_service.get_active_products(customer_id=customerId)

    return [
        ProductResponse(
            id=product.id,
            itemCode=product.itemCode,
            itemDescription=product.itemDescription,
            group=product.group,
            manufacturing=product.manufacturing,
            pricing=product.pricing,
            weight=product.weight,
            uom=product.uom,
            isActive=product.isActive,
            createdAt=product.createdAt,
            updatedAt=product.updatedAt
        )
        for product in products
    ]


@router.get(
    "/{product_id}",
    response_model=ProductResponse,
    summary="Get product by ID",
    description="Get a specific product by their ID"
)
async def get_product(
    product_id: str,
    db: AsyncIOMotorDatabase = Depends(get_db),
    current_user: UserInDB = Depends(get_current_active_user)
):
    """Get product by ID"""
    product_service = ProductService(db)
    product = await product_service.get_product_by_id(product_id)

    if not product:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Product not found"
        )

    return ProductResponse(
        id=product.id,
        itemCode=product.itemCode,
        itemDescription=product.itemDescription,
        group=product.group,
        manufacturing=product.manufacturing,
        pricing=product.pricing,
        weight=product.weight,
        uom=product.uom,
        isActive=product.isActive,
        createdAt=product.createdAt,
        updatedAt=product.updatedAt
    )


@router.put(
    "/{product_id}",
    response_model=ProductResponse,
    summary="Update product",
    description="Update product information. Admin only."
)
async def update_product(
    product_id: str,
    product_update: ProductUpdateRequest,
    db: AsyncIOMotorDatabase = Depends(get_db),
    current_user: UserInDB = Depends(require_admin)
):
    """Update product information (Admin only)"""
    product_service = ProductService(db)

    # Convert request to ProductUpdate model
    update_data = ProductUpdate(**product_update.model_dump(exclude_unset=True))

    updated_product = await product_service.update_product(product_id, update_data)

    if not updated_product:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Product not found"
        )

    return ProductResponse(
        id=updated_product.id,
        itemCode=updated_product.itemCode,
        itemDescription=updated_product.itemDescription,
        group=updated_product.group,
        manufacturing=updated_product.manufacturing,
        pricing=updated_product.pricing,
        weight=updated_product.weight,
        uom=updated_product.uom,
        isActive=updated_product.isActive,
        createdAt=updated_product.createdAt,
        updatedAt=updated_product.updatedAt
    )


@router.patch(
    "/{product_id}/toggle-status",
    response_model=ProductResponse,
    summary="Toggle product status",
    description="Toggle product active/inactive status. Admin only."
)
async def toggle_product_status(
    product_id: str,
    db: AsyncIOMotorDatabase = Depends(get_db),
    current_user: UserInDB = Depends(require_admin)
):
    """Toggle product active/inactive status (Admin only)"""
    product_service = ProductService(db)
    updated_product = await product_service.toggle_product_status(product_id)

    if not updated_product:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Product not found"
        )

    return ProductResponse(
        id=updated_product.id,
        itemCode=updated_product.itemCode,
        itemDescription=updated_product.itemDescription,
        group=updated_product.group,
        manufacturing=updated_product.manufacturing,
        pricing=updated_product.pricing,
        weight=updated_product.weight,
        uom=updated_product.uom,
        isActive=updated_product.isActive,
        createdAt=updated_product.createdAt,
        updatedAt=updated_product.updatedAt
    )


@router.delete(
    "/{product_id}",
    response_model=MessageResponse,
    summary="Delete product",
    description="Soft delete a product. Admin only."
)
async def delete_product(
    product_id: str,
    db: AsyncIOMotorDatabase = Depends(get_db),
    current_user: UserInDB = Depends(require_admin)
):
    """Soft delete a product (Admin only)"""
    product_service = ProductService(db)
    success = await product_service.delete_product(product_id)

    if not success:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Product not found"
        )

    return MessageResponse(
        message="Product deleted successfully",
        success=True
    )
