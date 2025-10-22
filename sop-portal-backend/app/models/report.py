"""
Report Data Models
Handles report generation, storage, and metadata
"""
from typing import Optional, Dict, Any, List
from datetime import datetime
from pydantic import BaseModel, Field
from enum import Enum


class ReportType(str, Enum):
    """Report type enumeration"""
    SALES_SUMMARY = "sales_summary"
    FORECAST_VS_ACTUAL = "forecast_vs_actual"
    CUSTOMER_PERFORMANCE = "customer_performance"
    PRODUCT_ANALYSIS = "product_analysis"
    CYCLE_SUBMISSION_STATUS = "cycle_submission_status"
    GROSS_PROFIT_ANALYSIS = "gross_profit_analysis"
    FORECAST_ACCURACY = "forecast_accuracy"
    MONTHLY_DASHBOARD = "monthly_dashboard"


class ReportFormat(str, Enum):
    """Report output format"""
    EXCEL = "excel"
    PDF = "pdf"
    JSON = "json"
    POWERBI = "powerbi"


class ReportStatus(str, Enum):
    """Report generation status"""
    PENDING = "pending"
    GENERATING = "generating"
    COMPLETED = "completed"
    FAILED = "failed"


class ReportGenerateRequest(BaseModel):
    """Request to generate a report"""
    reportType: ReportType = Field(..., description="Type of report to generate")
    format: ReportFormat = Field(default=ReportFormat.EXCEL, description="Output format")

    # Filter parameters
    cycleId: Optional[str] = Field(None, description="Filter by specific S&OP cycle")
    customerId: Optional[str] = Field(None, description="Filter by specific customer")
    productId: Optional[str] = Field(None, description="Filter by specific product")
    startDate: Optional[datetime] = Field(None, description="Start date for date range")
    endDate: Optional[datetime] = Field(None, description="End date for date range")
    year: Optional[int] = Field(None, description="Filter by specific year")
    month: Optional[int] = Field(None, ge=1, le=12, description="Filter by specific month")

    # Report options
    includeCharts: bool = Field(True, description="Include charts in Excel/PDF reports")
    includeRawData: bool = Field(False, description="Include raw data sheet in Excel reports")


class ReportInDB(BaseModel):
    """Report metadata stored in database"""
    id: str = Field(..., alias="_id", description="Report ID")
    reportType: ReportType
    format: ReportFormat
    status: ReportStatus = ReportStatus.PENDING

    # Request parameters
    filters: Dict[str, Any] = Field(default_factory=dict, description="Filter parameters used")
    options: Dict[str, Any] = Field(default_factory=dict, description="Report options")

    # File information
    fileName: Optional[str] = Field(None, description="Generated file name")
    filePath: Optional[str] = Field(None, description="File storage path")
    fileSize: Optional[int] = Field(None, description="File size in bytes")
    downloadUrl: Optional[str] = Field(None, description="Download URL")

    # Generation metadata
    generatedBy: str = Field(..., description="User ID who requested the report")
    generatedAt: Optional[datetime] = Field(None, description="When report was generated")
    expiresAt: Optional[datetime] = Field(None, description="When report download expires")

    # Statistics
    recordCount: Optional[int] = Field(None, description="Number of records in report")
    processingTime: Optional[float] = Field(None, description="Processing time in seconds")

    # Error information
    error: Optional[str] = Field(None, description="Error message if generation failed")

    createdAt: datetime = Field(default_factory=datetime.utcnow)
    updatedAt: datetime = Field(default_factory=datetime.utcnow)

    class Config:
        populate_by_name = True
        json_encoders = {datetime: lambda v: v.isoformat()}


class ReportResponse(BaseModel):
    """Report response model"""
    id: str
    reportType: ReportType
    format: ReportFormat
    status: ReportStatus

    fileName: Optional[str] = None
    downloadUrl: Optional[str] = None
    fileSize: Optional[int] = None

    generatedBy: str
    generatedAt: Optional[datetime] = None
    expiresAt: Optional[datetime] = None

    recordCount: Optional[int] = None
    processingTime: Optional[float] = None

    error: Optional[str] = None

    createdAt: datetime
    updatedAt: datetime


class PowerBIExportRequest(BaseModel):
    """Request for Power BI data export"""
    dataType: str = Field(..., description="Type of data to export (sales, forecasts, customers, etc.)")
    cycleId: Optional[str] = Field(None, description="Filter by cycle")
    startDate: Optional[datetime] = Field(None)
    endDate: Optional[datetime] = Field(None)


class ScheduledReportCreate(BaseModel):
    """Create scheduled report"""
    reportType: ReportType
    format: ReportFormat

    # Schedule configuration
    scheduleType: str = Field(..., description="daily, weekly, monthly")
    scheduleTime: str = Field(..., description="Time to run (HH:MM)")
    scheduleDay: Optional[int] = Field(None, description="Day of week (1-7) or month (1-31)")

    # Report configuration
    filters: Dict[str, Any] = Field(default_factory=dict)
    options: Dict[str, Any] = Field(default_factory=dict)

    # Recipients
    emailRecipients: List[str] = Field(default_factory=list, description="Email addresses to send report to")

    isActive: bool = Field(True, description="Whether schedule is active")
