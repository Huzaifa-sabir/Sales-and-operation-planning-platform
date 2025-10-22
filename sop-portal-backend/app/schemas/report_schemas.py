"""
Report Request/Response Schemas
"""
from pydantic import BaseModel, Field
from typing import List, Optional, Dict, Any
from datetime import datetime

from app.models.report import ReportResponse, ReportType, ReportFormat


class ReportListResponse(BaseModel):
    """Paginated list of reports"""
    reports: List[ReportResponse]
    total: int
    page: int
    pageSize: int
    totalPages: int
    hasNext: bool
    hasPrev: bool


class ReportGenerationResponse(BaseModel):
    """Response after initiating report generation"""
    success: bool = True
    message: str
    reportId: str
    status: str
    estimatedTime: Optional[int] = Field(None, description="Estimated time in seconds")


class MessageResponse(BaseModel):
    """Generic message response"""
    success: bool = True
    message: str


class PowerBIDataResponse(BaseModel):
    """Power BI data export response"""
    dataType: str
    recordCount: int
    generatedAt: datetime
    data: List[Dict[str, Any]]
    metadata: Dict[str, Any] = Field(default_factory=dict)
