"""
Report Generation Router
Handles report generation, listing, download, and deletion
"""
from fastapi import APIRouter, Depends, HTTPException, status, BackgroundTasks
from fastapi.responses import FileResponse
from typing import List, Optional
from datetime import datetime
import os

from app.models.user import UserInDB
from app.models.report import (
    ReportType,
    ReportFormat,
    ReportStatus,
    ReportGenerateRequest,
    ReportInDB
)
from app.schemas.report_schemas import (
    ReportListResponse,
    ReportGenerationResponse
)
from app.services.report_service import ReportService
from app.utils.auth_dependencies import get_current_user
from app.config.database import get_db

# Create router
router = APIRouter(
    prefix="/reports",
    tags=["Reports"]
)

# Dependencies
async def get_report_service():
    """Get report service instance"""
    db = await get_db()
    return ReportService(db)


async def generate_report_task(
    report_service: ReportService,
    report_id: str,
    report_type: ReportType,
    report_format: ReportFormat,
    filters: dict,
    user_id: str
):
    """
    Background task to generate report
    Updates report status and file path after generation
    """
    try:
        # Update status to GENERATING
        await report_service.db["reports"].update_one(
            {"_id": report_id},
            {"$set": {"status": ReportStatus.GENERATING, "updatedAt": datetime.utcnow()}}
        )

        # Generate the report based on type
        file_path = None

        if report_type == ReportType.SALES_SUMMARY:
            # Generate sales summary data
            data = await report_service.generate_sales_summary_data(filters)

            if report_format == ReportFormat.EXCEL:
                from app.utils.excel_report_generator import ExcelReportGenerator
                generator = ExcelReportGenerator()
                file_path = f"storage/reports/sales_summary_{report_id}.xlsx"
                generator.generate_sales_summary_excel(data, file_path)
            elif report_format == ReportFormat.PDF:
                from app.utils.pdf_report_generator import PDFReportGenerator
                generator = PDFReportGenerator()
                file_path = f"storage/reports/sales_summary_{report_id}.pdf"
                generator.generate_sales_summary_pdf(data, file_path)

        elif report_type == ReportType.FORECAST_VS_ACTUAL:
            # Generate forecast vs actual data
            data = await report_service.generate_forecast_vs_actual_data(filters)

            if report_format == ReportFormat.EXCEL:
                from app.utils.excel_report_generator import ExcelReportGenerator
                generator = ExcelReportGenerator()
                file_path = f"storage/reports/forecast_vs_actual_{report_id}.xlsx"
                generator.generate_forecast_vs_actual_excel(data, file_path)

        elif report_type == ReportType.MONTHLY_DASHBOARD:
            # Generate monthly dashboard data
            data = await report_service.generate_monthly_dashboard_data(filters)

            if report_format == ReportFormat.EXCEL:
                from app.utils.excel_report_generator import ExcelReportGenerator
                generator = ExcelReportGenerator()
                file_path = f"storage/reports/monthly_dashboard_{report_id}.xlsx"
                generator.generate_monthly_dashboard_excel(data, file_path)

        elif report_type == ReportType.CUSTOMER_PERFORMANCE:
            # Generate customer performance data
            data = await report_service.generate_customer_performance_data(filters)

            if report_format == ReportFormat.EXCEL:
                from app.utils.excel_report_generator import ExcelReportGenerator
                generator = ExcelReportGenerator()
                file_path = f"storage/reports/customer_performance_{report_id}.xlsx"
                generator.generate_customer_performance_excel(data, file_path)

        elif report_type == ReportType.PRODUCT_ANALYSIS:
            # Generate product analysis data
            data = await report_service.generate_product_analysis_data(filters)

            if report_format == ReportFormat.EXCEL:
                from app.utils.excel_report_generator import ExcelReportGenerator
                generator = ExcelReportGenerator()
                file_path = f"storage/reports/product_analysis_{report_id}.xlsx"
                generator.generate_product_analysis_excel(data, file_path)

        elif report_type == ReportType.CYCLE_SUBMISSION_STATUS:
            # Generate cycle submission status data
            data = await report_service.generate_cycle_submission_status_data(filters)

            if report_format == ReportFormat.EXCEL:
                from app.utils.excel_report_generator import ExcelReportGenerator
                generator = ExcelReportGenerator()
                file_path = f"storage/reports/cycle_submission_status_{report_id}.xlsx"
                generator.generate_cycle_submission_status_excel(data, file_path)

        elif report_type == ReportType.GROSS_PROFIT_ANALYSIS:
            # Generate gross profit analysis data
            data = await report_service.generate_gross_profit_analysis_data(filters)

            if report_format == ReportFormat.EXCEL:
                from app.utils.excel_report_generator import ExcelReportGenerator
                generator = ExcelReportGenerator()
                file_path = f"storage/reports/gross_profit_analysis_{report_id}.xlsx"
                generator.generate_gross_profit_analysis_excel(data, file_path)

        elif report_type == ReportType.FORECAST_ACCURACY:
            # Generate forecast accuracy data
            data = await report_service.generate_forecast_accuracy_data(filters)

            if report_format == ReportFormat.EXCEL:
                from app.utils.excel_report_generator import ExcelReportGenerator
                generator = ExcelReportGenerator()
                file_path = f"storage/reports/forecast_accuracy_{report_id}.xlsx"
                generator.generate_forecast_accuracy_excel(data, file_path)

        else:
            raise ValueError(f"Report type {report_type} not yet implemented")

        # Update report with completed status and file path
        file_name = os.path.basename(file_path) if file_path else None
        download_url = f"/api/v1/reports/{report_id}/download" if file_path else None

        await report_service.db["reports"].update_one(
            {"_id": report_id},
            {
                "$set": {
                    "status": ReportStatus.COMPLETED,
                    "filePath": file_path,
                    "fileName": file_name,
                    "downloadUrl": download_url,
                    "updatedAt": datetime.utcnow()
                }
            }
        )

    except Exception as e:
        # Update status to FAILED with error message
        await report_service.db["reports"].update_one(
            {"_id": report_id},
            {
                "$set": {
                    "status": ReportStatus.FAILED,
                    "error": str(e),
                    "updatedAt": datetime.utcnow()
                }
            }
        )
        print(f"Report generation failed for {report_id}: {str(e)}")


@router.post(
    "/generate",
    response_model=ReportGenerationResponse,
    status_code=status.HTTP_202_ACCEPTED,
    summary="Generate a new report",
    description="Trigger report generation in the background. Returns immediately with report ID."
)
async def generate_report(
    request: ReportGenerateRequest,
    background_tasks: BackgroundTasks,
    current_user: UserInDB = Depends(get_current_user),
    report_service: ReportService = Depends(get_report_service)
):
    """
    Generate a report asynchronously

    - **reportType**: Type of report to generate (sales_summary, forecast_vs_actual, monthly_dashboard)
    - **format**: Output format (EXCEL, PDF, JSON, POWERBI)
    - **filters**: Optional filters (startDate, endDate, customerId, productId, cycleId)
    - **options**: Optional settings (includeCharts, detailLevel)

    Returns report metadata immediately and generates the report in the background.
    Use GET /reports/{reportId} to check status.
    """
    # Phase 3: Support all 8 reports in EXCEL and PDF formats
    if request.format not in [ReportFormat.EXCEL, ReportFormat.PDF]:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Only EXCEL and PDF formats are currently supported. JSON and Power BI export available via separate endpoints."
        )

    # Build filters from request parameters
    filters = {}
    if request.cycleId:
        filters["cycleId"] = request.cycleId
    if request.customerId:
        filters["customerId"] = request.customerId
    if request.productId:
        filters["productId"] = request.productId
    if request.startDate:
        filters["startDate"] = request.startDate
    if request.endDate:
        filters["endDate"] = request.endDate
    if request.year:
        filters["year"] = request.year
    if request.month:
        filters["month"] = request.month

    # Check cache first
    cached_report = await report_service.get_cached_report(
        report_type=request.reportType,
        filters=filters
    )

    if cached_report:
        return ReportGenerationResponse(
            reportId=cached_report.id,
            status=cached_report.status,
            message="Report retrieved from cache",
            downloadUrl=cached_report.downloadUrl
        )

    # Create report metadata
    report = await report_service.create_report_metadata(
        report_type=request.reportType,
        report_format=request.format,
        filters=filters,
        options={"includeCharts": request.includeCharts, "includeRawData": request.includeRawData},
        generated_by=current_user.id
    )

    # Schedule background task to generate report
    background_tasks.add_task(
        generate_report_task,
        report_service,
        report.id,
        request.reportType,
        request.format,
        filters,
        current_user.id
    )

    return ReportGenerationResponse(
        reportId=report.id,
        status=report.status,
        message="Report generation started. Check status using the reportId.",
        downloadUrl=None  # Will be available when completed
    )


@router.get(
    "",
    response_model=ReportListResponse,
    summary="List user's reports",
    description="Get paginated list of reports generated by the current user"
)
async def list_reports(
    skip: int = 0,
    limit: int = 20,
    report_type: Optional[ReportType] = None,
    status_filter: Optional[ReportStatus] = None,
    current_user: UserInDB = Depends(get_current_user),
    report_service: ReportService = Depends(get_report_service)
):
    """
    List reports with pagination and filters

    - **skip**: Number of records to skip (default: 0)
    - **limit**: Number of records to return (default: 20, max: 100)
    - **report_type**: Filter by report type (optional)
    - **status_filter**: Filter by status (optional)
    """
    if limit > 100:
        limit = 100

    result = await report_service.list_reports(
        skip=skip,
        limit=limit,
        user_id=current_user.id,
        report_type=report_type.value if report_type else None
    )

    total_pages = (result["total"] + limit - 1) // limit if limit > 0 else 1
    current_page = (skip // limit) + 1 if limit > 0 else 1
    
    # Convert ReportInDB to ReportResponse format
    from app.models.report import ReportResponse
    report_responses = []
    for report in result["reports"]:
        report_responses.append(ReportResponse(
            id=report.id,
            reportType=report.reportType,
            format=report.format,
            status=report.status,
            fileName=report.fileName,
            downloadUrl=report.downloadUrl,
            fileSize=report.fileSize,
            generatedBy=report.generatedBy,
            generatedAt=report.generatedAt,
            expiresAt=report.expiresAt,
            recordCount=report.recordCount,
            processingTime=report.processingTime,
            error=report.error,
            createdAt=report.createdAt,
            updatedAt=report.updatedAt
        ))
    
    return ReportListResponse(
        reports=report_responses,
        total=result["total"],
        page=current_page,
        pageSize=limit,
        totalPages=total_pages,
        hasNext=current_page < total_pages,
        hasPrev=current_page > 1
    )


@router.get(
    "/{report_id}",
    response_model=ReportInDB,
    summary="Get report by ID",
    description="Get report metadata and status by report ID"
)
async def get_report(
    report_id: str,
    current_user: UserInDB = Depends(get_current_user),
    report_service: ReportService = Depends(get_report_service)
):
    """
    Get report details

    Returns report metadata including status, file path, and download URL if available.
    """
    report = await report_service.get_report_by_id(report_id)

    if not report:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Report not found"
        )

    # Verify user owns this report (or is admin)
    if report.generatedBy != current_user.id and current_user.role != "admin":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You don't have permission to access this report"
        )

    return report


@router.get(
    "/{report_id}/download",
    summary="Download generated report file",
    description="Download the generated report file (Excel, PDF, etc.)",
    response_class=FileResponse
)
async def download_report(
    report_id: str,
    current_user: UserInDB = Depends(get_current_user),
    report_service: ReportService = Depends(get_report_service)
):
    """
    Download report file

    Returns the generated file if available, otherwise returns 404 or 425 (Too Early).
    """
    report = await report_service.get_report_by_id(report_id)

    if not report:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Report not found"
        )

    # Verify user owns this report (or is admin)
    if report.generatedBy != current_user.id and current_user.role != "admin":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You don't have permission to access this report"
        )

    # Check if report is completed
    if report.status != "completed":
        raise HTTPException(
            status_code=status.HTTP_425_TOO_EARLY,
            detail=f"Report is not ready yet. Current status: {report.status}"
        )

    # Check if file exists
    if not report.filePath or not os.path.exists(report.filePath):
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Report file not found"
        )

    # Determine media type based on file extension
    media_type = "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"  # Excel
    if report.filePath.endswith(".pdf"):
        media_type = "application/pdf"
    elif report.filePath.endswith(".json"):
        media_type = "application/json"

    # Return file response
    return FileResponse(
        path=report.filePath,
        filename=report.fileName or os.path.basename(report.filePath),
        media_type=media_type
    )


@router.delete(
    "/{report_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Delete report",
    description="Delete report metadata and associated file"
)
async def delete_report(
    report_id: str,
    current_user: UserInDB = Depends(get_current_user),
    report_service: ReportService = Depends(get_report_service)
):
    """
    Delete a report

    Removes report metadata from database and deletes the generated file if it exists.
    Only the report owner or admin can delete reports.
    """
    report = await report_service.get_report_by_id(report_id)

    if not report:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Report not found"
        )

    # Verify user owns this report (or is admin)
    if report.generatedBy != current_user.id and current_user.role != "admin":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You don't have permission to delete this report"
        )

    # Delete the report (includes file deletion)
    await report_service.delete_report(report_id)

    return None
