"""
Excel Import/Export Router
Handles Excel file upload/download for bulk operations
"""
from typing import Optional
from fastapi import APIRouter, Depends, HTTPException, status, UploadFile, File, Query
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


# ==================== EXPORTS ====================

@router.get(
    "/export/customers",
    summary="Export customers to Excel",
    description="Export all customers to Excel file"
)
async def export_customers(
    db: AsyncIOMotorDatabase = Depends(get_db),
    current_user: UserInDB = Depends(require_admin)
):
    """
    Export customers to Excel file (Admin only)
    
    Returns an Excel file with all customers in the system.
    """
    customer_service = CustomerService(db)
    customers_result = await customer_service.list_customers(
        skip=0,
        limit=10000  # Get all customers
    )
    customers = customers_result.get("customers", [])

    # Generate Excel file
    excel_file = ExcelService.export_customers(customers)

    return StreamingResponse(
        excel_file,
        media_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
        headers={
            "Content-Disposition": f"attachment; filename=customers_export_{datetime.now().strftime('%Y%m%d')}.xlsx"
        }
    )


@router.get(
    "/export/products",
    summary="Export products to Excel",
    description="Export all products to Excel file"
)
async def export_products(
    db: AsyncIOMotorDatabase = Depends(get_db),
    current_user: UserInDB = Depends(require_admin)
):
    """
    Export products to Excel file (Admin only)
    
    Returns an Excel file with all products in the system.
    """
    product_service = ProductService(db)
    products_result = await product_service.list_products(
        skip=0,
        limit=10000  # Get all products
    )
    products = products_result.get("products", [])

    # Generate Excel file
    excel_file = ExcelService.export_products(products)

    return StreamingResponse(
        excel_file,
        media_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
        headers={
            "Content-Disposition": f"attachment; filename=products_export_{datetime.now().strftime('%Y%m%d')}.xlsx"
        }
    )


@router.get(
    "/export/sales-history",
    summary="Export sales history to Excel",
    description="Export sales history data to Excel file"
)
async def export_sales_history(
    start_date: Optional[str] = Query(None, description="Start date (YYYY-MM-DD)"),
    end_date: Optional[str] = Query(None, description="End date (YYYY-MM-DD)"),
    db: AsyncIOMotorDatabase = Depends(get_db),
    current_user: UserInDB = Depends(require_admin)
):
    """
    Export sales history to Excel file (Admin only)
    
    Returns an Excel file with sales history data.
    """
    sales_history_service = SalesHistoryService(db)
    sales_data = await sales_history_service.get_sales_history(
        start_date=start_date,
        end_date=end_date,
        limit=100000
    )

    # Generate Excel file
    excel_file = ExcelService.export_sales_history(sales_data.get("data", []))

    return StreamingResponse(
        excel_file,
        media_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
        headers={
            "Content-Disposition": f"attachment; filename=sales_history_export_{datetime.now().strftime('%Y%m%d')}.xlsx"
        }
    )


# ==================== IMPORTS ====================

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
                    "row": idx + 2,  # +2 because Excel rows start at 1 and we skip header
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
                    "itemDescription": created_product.itemDescription
                })
            except Exception as e:
                import_errors.append({
                    "row": idx + 2,
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


@router.post(
    "/import-all",
    summary="Import all data from consolidated Excel file",
    description="Upload consolidated Excel file to import customers, products, matrix, and sales history. Admin only."
)
async def import_all_data(
    file: UploadFile = File(..., description="Consolidated Excel file with customer sheets"),
    db: AsyncIOMotorDatabase = Depends(get_db),
    current_user: UserInDB = Depends(require_admin)
):
    """
    Import all data from consolidated Excel file (Admin only)
    
    This endpoint imports:
    - Customers (from sheet names)
    - Products (from all customer sheets)
    - Product-Customer Matrix (products per customer)
    - Sales History (if available in Summary sheet)
    """
    if not file.filename.endswith(('.xlsx', '.xls')):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="File must be an Excel file (.xlsx or .xls)"
        )
    
    try:
        # Save uploaded file temporarily
        import tempfile
        import os
        with tempfile.NamedTemporaryFile(delete=False, suffix='.xlsx') as tmp_file:
            contents = await file.read()
            tmp_file.write(contents)
            tmp_file_path = tmp_file.name
        
        try:
            # Import using the script
            import sys
            from pathlib import Path
            scripts_path = Path(__file__).parent.parent / 'scripts'
            sys.path.insert(0, str(scripts_path))
            
            from import_excel_data import ExcelDataImporter
            importer = ExcelDataImporter(db)
            
            # Import data
            await importer.import_all_from_file(tmp_file_path)
            
            return {
                "success": True,
                "message": "Data imported successfully",
                "summary": {
                    "customers_created": importer.stats['customers_created'],
                    "customers_updated": importer.stats['customers_updated'],
                    "products_created": importer.stats['products_created'],
                    "products_updated": importer.stats['products_updated'],
                    "matrix_entries_created": importer.stats['matrix_entries_created'],
                    "sales_history_created": importer.stats['sales_history_created'],
                    "errors": len(importer.stats['errors'])
                },
                "errors": importer.stats['errors'][:50]  # First 50 errors
            }
        finally:
            # Clean up temp file
            if os.path.exists(tmp_file_path):
                os.unlink(tmp_file_path)
                
    except Exception as e:
        import traceback
        traceback.print_exc()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error importing data: {str(e)}"
        )
