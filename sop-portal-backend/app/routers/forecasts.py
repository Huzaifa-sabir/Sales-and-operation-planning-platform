"""
Forecast Router
Handles forecast entry, submission, and bulk import endpoints
"""
from typing import Optional
from io import BytesIO
from datetime import datetime
from fastapi import APIRouter, Depends, HTTPException, status, Query, UploadFile, File
from fastapi.responses import StreamingResponse
from motor.motor_asyncio import AsyncIOMotorDatabase

from app.config.database import get_db
from app.models.forecast import (
    ForecastCreate,
    ForecastUpdate,
    ForecastResponse,
    ForecastSubmitRequest,
    ForecastBulkCreateRequest
)
from app.schemas.forecast_schemas import (
    ForecastListResponse,
    ForecastSubmitResponse,
    ForecastStatisticsResponse,
    MessageResponse,
    BulkImportResponse,
    BulkCreateForecastRequest,
    BulkCreateForecastResponse
)
from app.services.forecast_service import ForecastService
from app.services.sop_cycle_service import SOPCycleService
from app.utils.forecast_excel_helper import ForecastExcelImporter
from app.utils.auth_dependencies import get_current_active_user
from app.models.user import UserInDB

router = APIRouter(prefix="/forecasts", tags=["Forecast Entry & Submission"])


@router.post(
    "",
    response_model=ForecastResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Create a new forecast (save as draft)",
    description="Create a new forecast for the current open S&OP cycle"
)
async def create_forecast(
    forecast_data: ForecastCreate,
    db: AsyncIOMotorDatabase = Depends(get_db),
    current_user: UserInDB = Depends(get_current_active_user)
):
    """
    Create a new forecast (saved as DRAFT)

    - **cycleId**: S&OP cycle ID (must be OPEN)
    - **customerId**: Customer ID
    - **productId**: Product ID (item code)
    - **monthlyForecasts**: Array of monthly forecast data (16 months)
    - **useCustomerPrice**: If true, fetches price from pricing matrix
    - **overridePrice**: Optional override price if not using customer price

    Validates:
    - Cycle is in OPEN status
    - No duplicate forecast exists
    - Customer-specific pricing available or override provided
    """
    forecast_service = ForecastService(db)

    created_forecast = await forecast_service.create_forecast(
        forecast_data,
        current_user.id
    )

    return ForecastResponse(
        id=created_forecast.id,
        cycleId=created_forecast.cycleId,
        customerId=created_forecast.customerId,
        productId=created_forecast.productId,
        salesRepId=created_forecast.salesRepId,
        status=created_forecast.status,
        monthlyForecasts=created_forecast.monthlyForecasts,
        useCustomerPrice=created_forecast.useCustomerPrice,
        overridePrice=created_forecast.overridePrice,
        totalQuantity=created_forecast.totalQuantity,
        totalRevenue=created_forecast.totalRevenue,
        version=created_forecast.version,
        previousVersionId=created_forecast.previousVersionId,
        notes=created_forecast.notes,
        createdAt=created_forecast.createdAt,
        updatedAt=created_forecast.updatedAt,
        submittedAt=created_forecast.submittedAt
    )


@router.get(
    "",
    response_model=ForecastListResponse,
    summary="List forecasts",
    description="Get paginated list of forecasts with filtering"
)
async def list_forecasts(
    page: int = Query(default=1, ge=1, description="Page number"),
    pageSize: int = Query(default=100, ge=1, le=500, description="Items per page"),
    cycleId: Optional[str] = Query(None, description="Filter by cycle ID"),
    customerId: Optional[str] = Query(None, description="Filter by customer ID"),
    productId: Optional[str] = Query(None, description="Filter by product ID"),
    status: Optional[str] = Query(None, description="Filter by status (draft/submitted/approved/rejected)"),
    db: AsyncIOMotorDatabase = Depends(get_db),
    current_user: UserInDB = Depends(get_current_active_user)
):
    """
    List forecasts with filtering

    - Sales reps see only their own forecasts
    - Admins see all forecasts
    """
    forecast_service = ForecastService(db)

    skip = (page - 1) * pageSize

    # Sales reps can only see their own forecasts
    sales_rep_filter = None if current_user.role == "admin" else current_user.id

    result = await forecast_service.list_forecasts(
        skip=skip,
        limit=pageSize,
        cycle_id=cycleId,
        sales_rep_id=sales_rep_filter,
        customer_id=customerId,
        product_id=productId,
        status=status
    )

    # Convert to response models
    forecasts_response = [
        ForecastResponse(
            id=f.id,
            cycleId=f.cycleId,
            customerId=f.customerId,
            productId=f.productId,
            salesRepId=f.salesRepId,
            status=f.status,
            monthlyForecasts=f.monthlyForecasts,
            useCustomerPrice=f.useCustomerPrice,
            overridePrice=f.overridePrice,
            totalQuantity=f.totalQuantity,
            totalRevenue=f.totalRevenue,
            version=f.version,
            previousVersionId=f.previousVersionId,
            notes=f.notes,
            createdAt=f.createdAt,
            updatedAt=f.updatedAt,
            submittedAt=f.submittedAt
        )
        for f in result["forecasts"]
    ]

    return ForecastListResponse(
        forecasts=forecasts_response,
        total=result["total"],
        page=result["page"],
        pageSize=result["pageSize"],
        totalPages=result["totalPages"],
        hasNext=result["hasNext"],
        hasPrev=result["hasPrev"]
    )


@router.get(
    "/{forecast_id}",
    response_model=ForecastResponse,
    summary="Get forecast by ID",
    description="Retrieve a specific forecast by ID"
)
async def get_forecast(
    forecast_id: str,
    db: AsyncIOMotorDatabase = Depends(get_db),
    current_user: UserInDB = Depends(get_current_active_user)
):
    """Get forecast by ID"""
    forecast_service = ForecastService(db)

    forecast = await forecast_service.get_forecast_by_id(forecast_id)

    if not forecast:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Forecast not found"
        )

    # Sales reps can only view their own forecasts
    if current_user.role != "admin" and forecast.salesRepId != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You can only view your own forecasts"
        )

    return ForecastResponse(
        id=forecast.id,
        cycleId=forecast.cycleId,
        customerId=forecast.customerId,
        productId=forecast.productId,
        salesRepId=forecast.salesRepId,
        status=forecast.status,
        monthlyForecasts=forecast.monthlyForecasts,
        useCustomerPrice=forecast.useCustomerPrice,
        overridePrice=forecast.overridePrice,
        totalQuantity=forecast.totalQuantity,
        totalRevenue=forecast.totalRevenue,
        version=forecast.version,
        previousVersionId=forecast.previousVersionId,
        notes=forecast.notes,
        createdAt=forecast.createdAt,
        updatedAt=forecast.updatedAt,
        submittedAt=forecast.submittedAt
    )


@router.put(
    "/{forecast_id}",
    response_model=ForecastResponse,
    summary="Update forecast",
    description="Update an existing forecast (only DRAFT forecasts can be edited)"
)
async def update_forecast(
    forecast_id: str,
    forecast_update: ForecastUpdate,
    db: AsyncIOMotorDatabase = Depends(get_db),
    current_user: UserInDB = Depends(get_current_active_user)
):
    """
    Update a forecast (only DRAFT status)

    Prevents editing after submission.
    Recalculates pricing and totals automatically.
    """
    forecast_service = ForecastService(db)

    updated_forecast = await forecast_service.update_forecast(
        forecast_id,
        forecast_update,
        current_user.id
    )

    return ForecastResponse(
        id=updated_forecast.id,
        cycleId=updated_forecast.cycleId,
        customerId=updated_forecast.customerId,
        productId=updated_forecast.productId,
        salesRepId=updated_forecast.salesRepId,
        status=updated_forecast.status,
        monthlyForecasts=updated_forecast.monthlyForecasts,
        useCustomerPrice=updated_forecast.useCustomerPrice,
        overridePrice=updated_forecast.overridePrice,
        totalQuantity=updated_forecast.totalQuantity,
        totalRevenue=updated_forecast.totalRevenue,
        version=updated_forecast.version,
        previousVersionId=updated_forecast.previousVersionId,
        notes=updated_forecast.notes,
        createdAt=updated_forecast.createdAt,
        updatedAt=updated_forecast.updatedAt,
        submittedAt=updated_forecast.submittedAt
    )


@router.post(
    "/{forecast_id}/submit",
    response_model=ForecastSubmitResponse,
    summary="Submit forecast",
    description="Submit a forecast for review (mandatory 12-month check)"
)
async def submit_forecast(
    forecast_id: str,
    db: AsyncIOMotorDatabase = Depends(get_db),
    current_user: UserInDB = Depends(get_current_active_user)
):
    """
    Submit a forecast for approval

    Validations:
    - Forecast must be in DRAFT status
    - Must have at least 12 months of forecast data (mandatory)
    - Changes status to SUBMITTED
    - Forecast becomes read-only after submission

    After submission, the cycle statistics are updated.
    """
    forecast_service = ForecastService(db)

    submitted_forecast = await forecast_service.submit_forecast(forecast_id, current_user.id)

    return ForecastSubmitResponse(
        success=True,
        message=f"Forecast submitted successfully. Total: {submitted_forecast.totalQuantity} units, ${submitted_forecast.totalRevenue} revenue.",
        forecast=ForecastResponse(
            id=submitted_forecast.id,
            cycleId=submitted_forecast.cycleId,
            customerId=submitted_forecast.customerId,
            productId=submitted_forecast.productId,
            salesRepId=submitted_forecast.salesRepId,
            status=submitted_forecast.status,
            monthlyForecasts=submitted_forecast.monthlyForecasts,
            useCustomerPrice=submitted_forecast.useCustomerPrice,
            overridePrice=submitted_forecast.overridePrice,
            totalQuantity=submitted_forecast.totalQuantity,
            totalRevenue=submitted_forecast.totalRevenue,
            version=submitted_forecast.version,
            previousVersionId=submitted_forecast.previousVersionId,
            notes=submitted_forecast.notes,
            createdAt=submitted_forecast.createdAt,
            updatedAt=submitted_forecast.updatedAt,
            submittedAt=submitted_forecast.submittedAt
        )
    )


@router.delete(
    "/{forecast_id}",
    response_model=MessageResponse,
    summary="Delete forecast",
    description="Delete a forecast (only DRAFT forecasts can be deleted)"
)
async def delete_forecast(
    forecast_id: str,
    db: AsyncIOMotorDatabase = Depends(get_db),
    current_user: UserInDB = Depends(get_current_active_user)
):
    """
    Delete a forecast

    Only DRAFT forecasts can be deleted.
    SUBMITTED/APPROVED/REJECTED forecasts cannot be deleted.
    """
    forecast_service = ForecastService(db)

    success = await forecast_service.delete_forecast(forecast_id, current_user.id)

    if not success:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Forecast not found"
        )

    return MessageResponse(
        success=True,
        message="Forecast deleted successfully"
    )


@router.post(
    "/{forecast_id}/approve",
    response_model=ForecastSubmitResponse,
    summary="Approve forecast",
    description="Approve a submitted forecast. Admin/Manager only."
)
async def approve_forecast(
    forecast_id: str,
    comment: Optional[str] = None,
    db: AsyncIOMotorDatabase = Depends(get_db),
    current_user: UserInDB = Depends(get_current_active_user)
):
    """
    Approve a submitted forecast (Admin/Manager only)

    Validates:
    - Forecast must be in SUBMITTED status
    - User must have admin or manager role
    - Changes status to APPROVED
    - Optionally adds approval comment
    """
    # Check permissions
    if current_user.role not in ["admin", "manager"]:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only admins and managers can approve forecasts"
        )

    forecast_service = ForecastService(db)

    # Get forecast
    forecast = await forecast_service.get_forecast_by_id(forecast_id)
    if not forecast:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Forecast not found"
        )

    # Check status
    if forecast.status != "SUBMITTED":
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Cannot approve forecast with status {forecast.status}. Only SUBMITTED forecasts can be approved."
        )

    # Update forecast status
    update_data = ForecastUpdate(
        status="APPROVED",
        notes=f"{forecast.notes}\n[APPROVED by {current_user.fullName}]: {comment or 'No comment'}" if comment else forecast.notes
    )

    approved_forecast = await forecast_service.update_forecast(
        forecast_id,
        update_data,
        current_user.id
    )

    return ForecastSubmitResponse(
        success=True,
        message=f"Forecast approved successfully by {current_user.fullName}.",
        forecast=ForecastResponse(
            id=approved_forecast.id,
            cycleId=approved_forecast.cycleId,
            customerId=approved_forecast.customerId,
            productId=approved_forecast.productId,
            salesRepId=approved_forecast.salesRepId,
            status=approved_forecast.status,
            monthlyForecasts=approved_forecast.monthlyForecasts,
            useCustomerPrice=approved_forecast.useCustomerPrice,
            overridePrice=approved_forecast.overridePrice,
            totalQuantity=approved_forecast.totalQuantity,
            totalRevenue=approved_forecast.totalRevenue,
            version=approved_forecast.version,
            previousVersionId=approved_forecast.previousVersionId,
            notes=approved_forecast.notes,
            createdAt=approved_forecast.createdAt,
            updatedAt=approved_forecast.updatedAt,
            submittedAt=approved_forecast.submittedAt
        )
    )


@router.post(
    "/{forecast_id}/reject",
    response_model=ForecastSubmitResponse,
    summary="Reject forecast",
    description="Reject a submitted forecast with reason. Admin/Manager only."
)
async def reject_forecast(
    forecast_id: str,
    comment: str,
    db: AsyncIOMotorDatabase = Depends(get_db),
    current_user: UserInDB = Depends(get_current_active_user)
):
    """
    Reject a submitted forecast (Admin/Manager only)

    Validates:
    - Forecast must be in SUBMITTED status
    - User must have admin or manager role
    - Changes status to REJECTED
    - Comment is required explaining rejection reason
    """
    # Check permissions
    if current_user.role not in ["admin", "manager"]:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only admins and managers can reject forecasts"
        )

    if not comment or not comment.strip():
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Comment is required when rejecting a forecast"
        )

    forecast_service = ForecastService(db)

    # Get forecast
    forecast = await forecast_service.get_forecast_by_id(forecast_id)
    if not forecast:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Forecast not found"
        )

    # Check status
    if forecast.status != "SUBMITTED":
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Cannot reject forecast with status {forecast.status}. Only SUBMITTED forecasts can be rejected."
        )

    # Update forecast status
    update_data = ForecastUpdate(
        status="REJECTED",
        notes=f"{forecast.notes}\n[REJECTED by {current_user.fullName}]: {comment}"
    )

    rejected_forecast = await forecast_service.update_forecast(
        forecast_id,
        update_data,
        current_user.id
    )

    return ForecastSubmitResponse(
        success=True,
        message=f"Forecast rejected by {current_user.fullName}. Reason: {comment}",
        forecast=ForecastResponse(
            id=rejected_forecast.id,
            cycleId=rejected_forecast.cycleId,
            customerId=rejected_forecast.customerId,
            productId=rejected_forecast.productId,
            salesRepId=rejected_forecast.salesRepId,
            status=rejected_forecast.status,
            monthlyForecasts=rejected_forecast.monthlyForecasts,
            useCustomerPrice=rejected_forecast.useCustomerPrice,
            overridePrice=rejected_forecast.overridePrice,
            totalQuantity=rejected_forecast.totalQuantity,
            totalRevenue=rejected_forecast.totalRevenue,
            version=rejected_forecast.version,
            previousVersionId=rejected_forecast.previousVersionId,
            notes=rejected_forecast.notes,
            createdAt=rejected_forecast.createdAt,
            updatedAt=rejected_forecast.updatedAt,
            submittedAt=rejected_forecast.submittedAt
        )
    )


@router.get(
    "/cycle/{cycle_id}/statistics",
    response_model=ForecastStatisticsResponse,
    summary="Get forecast statistics for a cycle",
    description="Get aggregated forecast statistics for a specific S&OP cycle"
)
async def get_cycle_forecast_statistics(
    cycle_id: str,
    db: AsyncIOMotorDatabase = Depends(get_db),
    current_user: UserInDB = Depends(get_current_active_user)
):
    """
    Get forecast statistics for a cycle

    Returns:
    - Total forecasts (draft, submitted, approved, rejected)
    - Total quantity and revenue (from submitted/approved forecasts)
    """
    forecast_service = ForecastService(db)

    stats = await forecast_service.get_forecast_statistics(cycle_id)

    return ForecastStatisticsResponse(**stats)


@router.post(
    "/bulk-import",
    response_model=BulkImportResponse,
    summary="Bulk import forecasts from Excel",
    description="Import multiple forecasts from an Excel file"
)
async def bulk_import_forecasts(
    cycle_id: str = Query(..., description="S&OP cycle ID for the forecasts"),
    file: UploadFile = File(..., description="Excel file with forecast data"),
    db: AsyncIOMotorDatabase = Depends(get_db),
    current_user: UserInDB = Depends(get_current_active_user)
):
    """
    Bulk import forecasts from Excel file

    Expected Excel format:
    - Column headers: Customer ID, Product ID, Use Customer Price, Override Price, Notes, [Month columns in YYYY-MM format]
    - Data rows with quantities for each month

    The file will be parsed and forecasts created for each row.
    Forecasts are created in DRAFT status.
    """
    # Validate file type
    if not file.filename.endswith(('.xlsx', '.xls')):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="File must be an Excel file (.xlsx or .xls)"
        )

    # Get cycle information for month validation
    cycle_service = SOPCycleService(db)
    cycle = await cycle_service.get_cycle_by_id(cycle_id)

    if not cycle:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="S&OP cycle not found"
        )

    # Read file content
    file_content = await file.read()
    file_stream = BytesIO(file_content)

    # Parse Excel file
    importer = ForecastExcelImporter()
    bulk_forecasts = importer.parse_forecast_excel(
        file_stream,
        cycle.planningPeriod.get("months", [])
    )

    # Import forecasts
    forecast_service = ForecastService(db)
    imported = 0
    failed = 0
    errors = []

    for bulk_data in bulk_forecasts:
        try:
            forecast_create = ForecastCreate(
                cycleId=cycle_id,
                customerId=bulk_data.customerId,
                productId=bulk_data.productId,
                monthlyForecasts=bulk_data.monthlyForecasts,
                useCustomerPrice=bulk_data.useCustomerPrice,
                overridePrice=bulk_data.overridePrice,
                notes=bulk_data.notes
            )

            await forecast_service.create_forecast(forecast_create, current_user.id)
            imported += 1

        except Exception as e:
            failed += 1
            errors.append(f"Row for {bulk_data.customerId}/{bulk_data.productId}: {str(e)}")

    return BulkImportResponse(
        success=True,
        message=f"Bulk import completed. {imported} forecasts imported, {failed} failed.",
        imported=imported,
        failed=failed,
        errors=errors[:10]  # Return first 10 errors
    )


@router.get(
    "/cycle/{cycle_id}/template",
    summary="Download forecast import template",
    description="Download an Excel template for bulk forecast import"
)
async def download_forecast_template(
    cycle_id: str,
    db: AsyncIOMotorDatabase = Depends(get_db),
    current_user: UserInDB = Depends(get_current_active_user)
):
    """
    Download Excel template for bulk forecast import

    The template includes:
    - Proper column headers
    - Month columns based on the cycle's planning period
    - Example data row
    """
    # Get cycle information
    cycle_service = SOPCycleService(db)
    cycle = await cycle_service.get_cycle_by_id(cycle_id)

    if not cycle:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="S&OP cycle not found"
        )

    # Generate template
    importer = ForecastExcelImporter()
    workbook = importer.generate_forecast_template(cycle.planningPeriod.get("months", []))

    # Save to BytesIO
    output = BytesIO()
    workbook.save(output)
    output.seek(0)

    # Return as downloadable file
    return StreamingResponse(
        output,
        media_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
        headers={
            "Content-Disposition": f"attachment; filename=forecast_template_{cycle.cycleName.replace(' ', '_')}.xlsx"
        }
    )


@router.get(
    "/cycle/{cycle_id}/export",
    summary="Export forecasts to Excel",
    description="Export all forecasts for a cycle to Excel file"
)
async def export_forecasts(
    cycle_id: str,
    db: AsyncIOMotorDatabase = Depends(get_db),
    current_user: UserInDB = Depends(get_current_active_user)
):
    """
    Export forecasts to Excel file
    
    Returns an Excel file with all forecasts for the specified cycle.
    """
    # Get cycle
    cycle_service = SOPCycleService(db)
    cycle = await cycle_service.get_cycle_by_id(cycle_id)
    
    if not cycle:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Cycle not found"
        )
    
    # Get forecasts for this cycle
    forecast_service = ForecastService(db)
    forecasts_result = await forecast_service.list_forecasts(
        cycle_id=cycle_id,
        skip=0,
        limit=1000  # Get all forecasts
    )
    forecasts = forecasts_result.get("forecasts", [])
    
    # Generate Excel file
    importer = ForecastExcelImporter()
    workbook = importer.generate_forecast_export(forecasts, cycle.planningPeriod.get("months", []))
    
    # Save to BytesIO
    output = BytesIO()
    workbook.save(output)
    output.seek(0)
    
    # Return as downloadable file
    return StreamingResponse(
        output,
        media_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
        headers={
            "Content-Disposition": f"attachment; filename=forecasts_{cycle.cycleName.replace(' ', '_')}_{datetime.now().strftime('%Y%m%d')}.xlsx"
        }
    )


@router.post(
    "/bulk",
    response_model=BulkCreateForecastResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Bulk create forecasts for one customer",
    description="Create multiple forecasts for one customer at once"
)
async def bulk_create_forecasts(
    bulk_data: BulkCreateForecastRequest,
    db: AsyncIOMotorDatabase = Depends(get_db),
    current_user: UserInDB = Depends(get_current_active_user)
):
    """
    Bulk create forecasts for one customer
    
    Creates or updates multiple forecasts for a single customer.
    All forecasts must be for the same customer and cycle.
    """
    forecast_service = ForecastService(db)
    
    # Create forecasts
    created_forecasts = await forecast_service.bulk_create_forecasts(
        cycle_id=bulk_data.cycleId,
        customer_id=bulk_data.customerId,
        forecasts_data=bulk_data.forecasts,
        sales_rep_id=current_user.id
    )
    
    # Count created vs updated
    created_count = 0
    updated_count = 0
    
    # Convert to response models
    forecasts_response = []
    for f in created_forecasts:
        forecasts_response.append(
            ForecastResponse(
                id=f.id,
                cycleId=f.cycleId,
                customerId=f.customerId,
                productId=f.productId,
                salesRepId=f.salesRepId,
                status=f.status,
                monthlyForecasts=f.monthlyForecasts,
                useCustomerPrice=f.useCustomerPrice,
                overridePrice=f.overridePrice,
                totalQuantity=f.totalQuantity,
                totalRevenue=f.totalRevenue,
                version=f.version,
                previousVersionId=f.previousVersionId,
                notes=f.notes,
                createdAt=f.createdAt,
                updatedAt=f.updatedAt,
                submittedAt=f.submittedAt
            )
        )
        # Check if this was newly created (createdAt == updatedAt) or updated
        if f.createdAt == f.updatedAt:
            created_count += 1
        else:
            updated_count += 1
    
    return BulkCreateForecastResponse(
        success=True,
        message=f"Successfully processed {len(created_forecasts)} forecasts",
        forecasts=forecasts_response,
        created=created_count,
        updated=updated_count
    )
