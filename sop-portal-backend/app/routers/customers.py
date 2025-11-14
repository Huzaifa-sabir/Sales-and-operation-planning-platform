"""
Customer Management Router
Handles all customer CRUD operations
"""
from typing import Optional
from fastapi import APIRouter, Depends, HTTPException, status, Query
from motor.motor_asyncio import AsyncIOMotorDatabase

from app.config.database import get_db
from app.models.customer import CustomerInDB, CustomerResponse, CustomerCreate, CustomerUpdate
from app.schemas.customer_schemas import (
    CustomerCreateRequest,
    CustomerUpdateRequest,
    CustomerListResponse,
    MessageResponse
)
from app.services.customer_service import CustomerService
from app.utils.auth_dependencies import require_admin, get_current_active_user
from app.models.user import UserInDB

router = APIRouter(prefix="/customers", tags=["Customer Management"])


@router.post(
    "",
    response_model=CustomerResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Create a new customer",
    description="Create a new customer. Admin only."
)
async def create_customer(
    customer_data: CustomerCreateRequest,
    db: AsyncIOMotorDatabase = Depends(get_db),
    current_user: UserInDB = Depends(require_admin)
):
    """
    Create a new customer (Admin only)

    - **customerId**: Unique customer ID (e.g., PATITO-000001)
    - **customerName**: Customer name
    - **location**: Customer location details (optional)
    - **contactPerson**: Contact person name (optional)
    - **contactEmail**: Contact email (optional)
    - **contactPhone**: Contact phone (optional)
    - **paymentTerms**: Payment terms (optional)
    - **creditLimit**: Credit limit (optional)
    """
    customer_service = CustomerService(db)

    # Convert request to CustomerCreate model with required fields
    customer_data_dict = customer_data.model_dump()
    customer_data_dict.update({
        'salesRepId': 'default-rep',  # Default sales rep
        'salesRepName': 'Default Sales Rep',  # Default sales rep name
        'sopCustomerName': customer_data_dict.get('customerName', ''),  # Use customer name as S&OP name
    })
    customer_create = CustomerCreate(**customer_data_dict)

    created_customer = await customer_service.create_customer(customer_create)

    # Convert to CustomerResponse
    return CustomerResponse(
        id=created_customer.id,
        customerId=created_customer.customerId,
        customerName=created_customer.customerName,
        sopCustomerName=getattr(created_customer, 'sopCustomerName', created_customer.customerName),
        salesRepId=getattr(created_customer, 'salesRepId', 'default-rep'),
        salesRepName=getattr(created_customer, 'salesRepName', 'Default Sales Rep'),
        location=created_customer.location,
        contactPerson=created_customer.contactPerson,
        contactEmail=created_customer.contactEmail,
        contactPhone=created_customer.contactPhone,
        paymentTerms=getattr(created_customer, 'paymentTerms', None),
        creditLimit=getattr(created_customer, 'creditLimit', None),
        isActive=created_customer.isActive,
        createdAt=created_customer.createdAt,
        updatedAt=created_customer.updatedAt
    )


@router.get(
    "",
    response_model=CustomerListResponse,
    summary="List all customers",
    description="Get paginated list of customers with optional filtering"
)
async def list_customers(
    page: int = Query(default=1, ge=1, description="Page number"),
    pageSize: int = Query(default=10, ge=1, le=1000, description="Items per page"),
    isActive: Optional[bool] = Query(None, description="Filter by active status"),
    search: Optional[str] = Query(None, description="Search in customerId, customerName, contactPerson, contactEmail"),
    db: AsyncIOMotorDatabase = Depends(get_db),
    current_user: UserInDB = Depends(get_current_active_user)
):
    """
    List customers with pagination and filtering

    - **page**: Page number (default: 1)
    - **pageSize**: Items per page (default: 10, max: 100)
    - **isActive**: Filter by active status (optional)
    - **search**: Search in customer fields (optional)
    """
    customer_service = CustomerService(db)

    skip = (page - 1) * pageSize

    result = await customer_service.list_customers(
        skip=skip,
        limit=pageSize,
        is_active=isActive,
        search=search
    )

    # Convert customers to CustomerResponse
    customer_responses = [
        CustomerResponse(
            id=customer.id,
            customerId=customer.customerId,
            customerName=customer.customerName,
            sopCustomerName=getattr(customer, 'sopCustomerName', customer.customerName),
            salesRepId=getattr(customer, 'salesRepId', 'default-rep'),
            salesRepName=getattr(customer, 'salesRepName', 'Default Sales Rep'),
            location=customer.location,
            contactPerson=customer.contactPerson,
            contactEmail=customer.contactEmail,
            contactPhone=customer.contactPhone,
            paymentTerms=getattr(customer, 'paymentTerms', None),
            creditLimit=getattr(customer, 'creditLimit', None),
            isActive=customer.isActive,
            createdAt=customer.createdAt,
            updatedAt=customer.updatedAt
        )
        for customer in result["customers"]
    ]

    return CustomerListResponse(
        customers=customer_responses,
        total=result["total"],
        page=result["page"],
        pageSize=result["pageSize"],
        totalPages=result["totalPages"],
        hasNext=result["hasNext"],
        hasPrev=result["hasPrev"]
    )


@router.get(
    "/active",
    response_model=list[CustomerResponse],
    summary="Get all active customers",
    description="Get all active customers (for dropdowns, etc.)"
)
async def get_active_customers(
    db: AsyncIOMotorDatabase = Depends(get_db),
    current_user: UserInDB = Depends(get_current_active_user)
):
    """Get all active customers (useful for dropdowns)"""
    customer_service = CustomerService(db)
    customers = await customer_service.get_active_customers()

    return [
        CustomerResponse(
            id=customer.id,
            customerId=customer.customerId,
            customerName=customer.customerName,
            location=customer.location,
            contactPerson=customer.contactPerson,
            contactEmail=customer.contactEmail,
            contactPhone=customer.contactPhone,
            paymentTerms=customer.paymentTerms,
            creditLimit=customer.creditLimit,
            isActive=customer.isActive,
            createdAt=customer.createdAt,
            updatedAt=customer.updatedAt
        )
        for customer in customers
    ]


@router.get(
    "/statistics",
    summary="Get customer statistics",
    description="Get aggregated customer statistics (total, active, YTD sales)"
)
async def get_customer_statistics(
    db: AsyncIOMotorDatabase = Depends(get_db),
    current_user: UserInDB = Depends(get_current_active_user)
):
    """
    Get customer statistics
    
    Returns:
    - total: Total number of customers
    - active: Number of active customers
    - inactive: Number of inactive customers
    - totalYtdSales: Total YTD sales from sales history
    """
    from datetime import datetime
    from app.services.sales_history_service import SalesHistoryService
    
    customer_service = CustomerService(db)
    sales_service = SalesHistoryService(db)
    
    # Get total customers
    total_customers = await db.customers.count_documents({})
    
    # Get active customers
    active_customers = await db.customers.count_documents({"isActive": True})
    
    # Get inactive customers
    inactive_customers = total_customers - active_customers
    
    # Calculate YTD sales from sales history
    current_year = datetime.now().year
    ytd_sales_stats = await sales_service.get_sales_statistics(year=current_year)
    total_ytd_sales = ytd_sales_stats.get("totalRevenue", 0)
    
    return {
        "total": total_customers,
        "active": active_customers,
        "inactive": inactive_customers,
        "totalYtdSales": round(total_ytd_sales, 2)
    }


@router.get(
    "/{customer_id}",
    response_model=CustomerResponse,
    summary="Get customer by ID",
    description="Get a specific customer by their ID"
)
async def get_customer(
    customer_id: str,
    db: AsyncIOMotorDatabase = Depends(get_db),
    current_user: UserInDB = Depends(get_current_active_user)
):
    """Get customer by ID"""
    customer_service = CustomerService(db)
    customer = await customer_service.get_customer_by_id(customer_id)

    if not customer:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Customer not found"
        )

    return CustomerResponse(
        id=customer.id,
        customerId=customer.customerId,
        customerName=customer.customerName,
        location=customer.location,
        contactPerson=customer.contactPerson,
        contactEmail=customer.contactEmail,
        contactPhone=customer.contactPhone,
        paymentTerms=customer.paymentTerms,
        creditLimit=customer.creditLimit,
        isActive=customer.isActive,
        createdAt=customer.createdAt,
        updatedAt=customer.updatedAt
    )


@router.put(
    "/{customer_id}",
    response_model=CustomerResponse,
    summary="Update customer",
    description="Update customer information. Admin only."
)
async def update_customer(
    customer_id: str,
    customer_update: CustomerUpdateRequest,
    db: AsyncIOMotorDatabase = Depends(get_db),
    current_user: UserInDB = Depends(require_admin)
):
    """Update customer information (Admin only)"""
    customer_service = CustomerService(db)

    # Convert request to CustomerUpdate model
    update_data = CustomerUpdate(**customer_update.model_dump(exclude_unset=True))

    updated_customer = await customer_service.update_customer(customer_id, update_data)

    if not updated_customer:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Customer not found"
        )

    return CustomerResponse(
        id=updated_customer.id,
        customerId=updated_customer.customerId,
        customerName=updated_customer.customerName,
        location=updated_customer.location,
        contactPerson=updated_customer.contactPerson,
        contactEmail=updated_customer.contactEmail,
        contactPhone=updated_customer.contactPhone,
        paymentTerms=updated_customer.paymentTerms,
        creditLimit=updated_customer.creditLimit,
        isActive=updated_customer.isActive,
        createdAt=updated_customer.createdAt,
        updatedAt=updated_customer.updatedAt
    )


@router.patch(
    "/{customer_id}/toggle-status",
    response_model=CustomerResponse,
    summary="Toggle customer status",
    description="Toggle customer active/inactive status. Admin only."
)
async def toggle_customer_status(
    customer_id: str,
    db: AsyncIOMotorDatabase = Depends(get_db),
    current_user: UserInDB = Depends(require_admin)
):
    """Toggle customer active/inactive status (Admin only)"""
    customer_service = CustomerService(db)
    updated_customer = await customer_service.toggle_customer_status(customer_id)

    if not updated_customer:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Customer not found"
        )

    return CustomerResponse(
        id=updated_customer.id,
        customerId=updated_customer.customerId,
        customerName=updated_customer.customerName,
        location=updated_customer.location,
        contactPerson=updated_customer.contactPerson,
        contactEmail=updated_customer.contactEmail,
        contactPhone=updated_customer.contactPhone,
        paymentTerms=updated_customer.paymentTerms,
        creditLimit=updated_customer.creditLimit,
        isActive=updated_customer.isActive,
        createdAt=updated_customer.createdAt,
        updatedAt=updated_customer.updatedAt
    )


@router.delete(
    "/{customer_id}",
    response_model=MessageResponse,
    summary="Delete customer",
    description="Soft delete a customer. Admin only."
)
async def delete_customer(
    customer_id: str,
    db: AsyncIOMotorDatabase = Depends(get_db),
    current_user: UserInDB = Depends(require_admin)
):
    """Soft delete a customer (Admin only)"""
    customer_service = CustomerService(db)
    success = await customer_service.delete_customer(customer_id)

    if not success:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Customer not found"
        )

    return MessageResponse(
        message="Customer deleted successfully",
        success=True
    )
