"""
Excel Import/Export Router
Handles Excel file upload/download for bulk operations
"""
from typing import Optional
from fastapi import APIRouter, Depends, HTTPException, status, UploadFile, File
from fastapi.responses import StreamingResponse
from motor.motor_asyncio import AsyncIOMotorDatabase
from datetime import datetime

from app.config.database import get_db
from app.services.excel_service import ExcelService
from app.services.sales_history_service import SalesHistoryService
from app.services.customer_service import CustomerService
from app.services.product_service import ProductService
from app.services.matrix_service import MatrixService
from app.models.customer import CustomerCreate
from app.models.product import ProductCreate
from app.models.product_customer_matrix import ProductCustomerMatrixCreate
from app.utils.auth_dependencies import require_admin, get_current_active_user
from app.models.user import UserInDB

router = APIRouter(prefix="/excel", tags=["Excel Import/Export"])


# ==================== TEMPLATE DOWNLOADS ====================

@router.get(
    "/templates/customers",
    summary="Download customer import template",
    description="Download Excel template for customer bulk import"
)
async def download_customer_template(
    current_user: UserInDB = Depends(require_admin)
):
    """Download Excel template for customer import (Admin only)"""
    excel_file = ExcelService.generate_customer_template()

    return StreamingResponse(
        excel_file,
        media_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
        headers={
            "Content-Disposition": f"attachment; filename=customer_import_template_{datetime.now().strftime('%Y%m%d')}.xlsx"
        }
    )


@router.get(
    "/templates/products",
    summary="Download product import template",
    description="Download Excel template for product bulk import"
)
async def download_product_template(
    current_user: UserInDB = Depends(require_admin)
):
    """Download Excel template for product import (Admin only)"""
    excel_file = ExcelService.generate_product_template()

    return StreamingResponse(
        excel_file,
        media_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
        headers={
            "Content-Disposition": f"attachment; filename=product_import_template_{datetime.now().strftime('%Y%m%d')}.xlsx"
        }
    )


@router.get(
    "/templates/matrix",
    summary="Download matrix import template",
    description="Download Excel template for product-customer matrix bulk import"
)
async def download_matrix_template(
    current_user: UserInDB = Depends(require_admin)
):
    """Download Excel template for matrix import (Admin only)"""
    excel_file = ExcelService.generate_matrix_template()

    return StreamingResponse(
        excel_file,
        media_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
        headers={
            "Content-Disposition": f"attachment; filename=matrix_import_template_{datetime.now().strftime('%Y%m%d')}.xlsx"
        }
    )


# ==================== DATA EXPORTS ====================

@router.get(
    "/export/customers",
    summary="Export customers to Excel",
    description="Export all customers to Excel file"
)
async def export_customers(
    isActive: Optional[bool] = None,
    db: AsyncIOMotorDatabase = Depends(get_db),
    current_user: UserInDB = Depends(get_current_active_user)
):
    """Export customers to Excel"""
    try:
        customer_service = CustomerService(db)

        # Get all customers
        result = await customer_service.list_customers(
            skip=0,
            limit=1000,  # Reduced limit to avoid timeout
            is_active=isActive
        )

        # Convert to dict format
        customers_data = [
            {
                "customerId": c.customerId,
                "customerName": c.customerName,
                "contactPerson": c.contactPerson,
                "contactEmail": c.contactEmail,
                "contactPhone": c.contactPhone,
                "location": c.location.model_dump() if c.location else None,
                "paymentTerms": getattr(c, 'paymentTerms', None),
                "creditLimit": getattr(c, 'creditLimit', None),
                "isActive": c.isActive,
                "createdAt": c.createdAt
            }
            for c in result["customers"]
        ]

        excel_file = ExcelService.export_customers(customers_data)

        return StreamingResponse(
            excel_file,
            media_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
            headers={
                "Content-Disposition": f"attachment; filename=customers_export_{datetime.now().strftime('%Y%m%d_%H%M%S')}.xlsx"
            }
        )
    except Exception as e:
        print(f"Export error: {e}")
        import traceback
        traceback.print_exc()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Export failed: {str(e)}"
        )


@router.get(
    "/export/products",
    summary="Export products to Excel",
    description="Export all products to Excel file"
)
async def export_products(
    isActive: Optional[bool] = None,
    db: AsyncIOMotorDatabase = Depends(get_db),
    current_user: UserInDB = Depends(get_current_active_user)
):
    """Export products to Excel"""
    product_service = ProductService(db)

    # Get all products
    result = await product_service.list_products(
        skip=0,
        limit=10000,  # Get all
        is_active=isActive
    )

    # Convert to dict format
    products_data = [
        {
            "itemCode": p.itemCode,
            "description": p.description,
            "group": p.group.model_dump() if p.group else None,
            "manufacturing": p.manufacturing.model_dump() if p.manufacturing else None,
            "pricing": p.pricing.model_dump() if p.pricing else None,
            "weight": p.weight,
            "uom": p.uom,
            "isActive": p.isActive,
            "createdAt": p.createdAt
        }
        for p in result["products"]
    ]

    excel_file = ExcelService.export_products(products_data)

    return StreamingResponse(
        excel_file,
        media_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
        headers={
            "Content-Disposition": f"attachment; filename=products_export_{datetime.now().strftime('%Y%m%d_%H%M%S')}.xlsx"
        }
    )


@router.get(
    "/export/sales-history",
    summary="Export sales history to Excel",
    description="Export filtered sales history records to Excel file"
)
async def export_sales_history(
    customerId: Optional[str] = None,
    productId: Optional[str] = None,
    year: Optional[int] = None,
    month: Optional[int] = None,
    limit: int = 1000,
    db: AsyncIOMotorDatabase = Depends(get_db),
    current_user: UserInDB = Depends(get_current_active_user)
):
    """Export sales history to Excel with optional filters"""
    sales_service = SalesHistoryService(db)

    result = await sales_service.get_sales_history(
        skip=0,
        limit=min(max(limit, 1), 5000),
        customer_id=customerId,
        product_id=productId,
        year=year,
        month=month,
    )

    # Convert result records to dicts
    records = [r.model_dump(by_alias=True) for r in result["records"]]

    excel_file = ExcelService.export_sales_history(records)

    return StreamingResponse(
        excel_file,
        media_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
        headers={
            "Content-Disposition": f"attachment; filename=sales_history_{datetime.now().strftime('%Y%m%d_%H%M%S')}.xlsx"
        }
    )


# ==================== DATA IMPORTS ====================

@router.post(
    "/import/customers",
    summary="Import customers from Excel",
    description="Upload Excel file to bulk import customers. Returns detailed error report."
)
async def import_customers(
    file: UploadFile = File(..., description="Excel file with customer data"),
    db: AsyncIOMotorDatabase = Depends(get_db),
    current_user: UserInDB = Depends(require_admin)
):
    """
    Import customers from Excel file (Admin only)

    Validates each row and provides detailed error reporting.
    Successfully imported customers are added to the database.
    """
    # Validate file type
    if not file.filename.endswith(('.xlsx', '.xls')):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="File must be an Excel file (.xlsx or .xls)"
        )

    try:
        # Parse Excel file
        contents = await file.read()
        result = ExcelService.import_customers(contents)

        if "error" in result:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=result["error"]
            )

        # Import successfully parsed customers
        customer_service = CustomerService(db)
        created = []
        import_errors = []

        for idx, customer_data in enumerate(result["imported"]):
            try:
                # Create customer
                customer_create = CustomerCreate(**customer_data)
                created_customer = await customer_service.create_customer(customer_create)
                created.append({
                    "customerId": created_customer.customerId,
                    "customerName": created_customer.customerName
                })
            except Exception as e:
                import_errors.append({
                    "customerId": customer_data.get("customerId"),
                    "error": str(e)
                })

        return {
            "success": len(import_errors) == 0,
            "message": f"Imported {len(created)} customers successfully",
            "created": created,
            "parseErrors": result["errors"],
            "importErrors": import_errors,
            "totalRows": result["totalRows"],
            "successCount": len(created),
            "errorCount": len(result["errors"]) + len(import_errors)
        }

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error processing file: {str(e)}"
        )


@router.post(
    "/import/products",
    summary="Import products from Excel",
    description="Upload Excel file to bulk import products. Returns detailed error report."
)
async def import_products(
    file: UploadFile = File(..., description="Excel file with product data"),
    db: AsyncIOMotorDatabase = Depends(get_db),
    current_user: UserInDB = Depends(require_admin)
):
    """
    Import products from Excel file (Admin only)

    Validates each row and provides detailed error reporting.
    Successfully imported products are added to the database.
    """
    # Validate file type
    if not file.filename.endswith(('.xlsx', '.xls')):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="File must be an Excel file (.xlsx or .xls)"
        )

    try:
        # Parse Excel file
        contents = await file.read()
        result = ExcelService.import_products(contents)

        if "error" in result:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=result["error"]
            )

        # Import successfully parsed products
        product_service = ProductService(db)
        created = []
        import_errors = []

        for idx, product_data in enumerate(result["imported"]):
            try:
                # Create product
                product_create = ProductCreate(**product_data)
                created_product = await product_service.create_product(product_create)
                created.append({
                    "itemCode": created_product.itemCode,
                    "description": created_product.description
                })
            except Exception as e:
                import_errors.append({
                    "itemCode": product_data.get("itemCode"),
                    "error": str(e)
                })

        return {
            "success": len(import_errors) == 0,
            "message": f"Imported {len(created)} products successfully",
            "created": created,
            "parseErrors": result["errors"],
            "importErrors": import_errors,
            "totalRows": result["totalRows"],
            "successCount": len(created),
            "errorCount": len(result["errors"]) + len(import_errors)
        }

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error processing file: {str(e)}"
        )


@router.post(
    "/import/matrix",
    summary="Import product-customer matrix from Excel",
    description="Upload Excel file to bulk import matrix entries. Returns detailed error report."
)
async def import_matrix(
    file: UploadFile = File(..., description="Excel file with matrix data"),
    db: AsyncIOMotorDatabase = Depends(get_db),
    current_user: UserInDB = Depends(require_admin)
):
    """
    Import product-customer matrix from Excel file (Admin only)

    Validates each row and provides detailed error reporting.
    Successfully imported entries are added to the database.
    """
    # Validate file type
    if not file.filename.endswith(('.xlsx', '.xls')):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="File must be an Excel file (.xlsx or .xls)"
        )

    try:
        # Parse Excel file
        contents = await file.read()
        result = ExcelService.import_matrix(contents)

        if "error" in result:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=result["error"]
            )

        # Import successfully parsed matrix entries
        matrix_service = MatrixService(db)
        created = []
        import_errors = []

        for idx, matrix_data in enumerate(result["imported"]):
            try:
                # Create matrix entry
                matrix_create = ProductCustomerMatrixCreate(**matrix_data)
                created_entry = await matrix_service.create_matrix_entry(matrix_create)
                created.append({
                    "customerId": created_entry.customerId,
                    "productId": created_entry.productId
                })
            except Exception as e:
                import_errors.append({
                    "customerId": matrix_data.get("customerId"),
                    "productId": matrix_data.get("productId"),
                    "error": str(e)
                })

        return {
            "success": len(import_errors) == 0,
            "message": f"Imported {len(created)} matrix entries successfully",
            "created": created,
            "parseErrors": result["errors"],
            "importErrors": import_errors,
            "totalRows": result["totalRows"],
            "successCount": len(created),
            "errorCount": len(result["errors"]) + len(import_errors)
        }

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error processing file: {str(e)}"
        )
