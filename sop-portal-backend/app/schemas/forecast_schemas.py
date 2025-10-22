"""
Forecast Request/Response Schemas
"""
from pydantic import BaseModel, Field
from typing import List, Optional
from datetime import datetime

from app.models.forecast import ForecastResponse, ForecastStatus


class ForecastListResponse(BaseModel):
    """Paginated list of forecasts"""
    forecasts: List[ForecastResponse]
    total: int
    page: int
    pageSize: int
    totalPages: int
    hasNext: bool
    hasPrev: bool


class ForecastSubmitResponse(BaseModel):
    """Response after forecast submission"""
    success: bool = True
    message: str
    forecast: ForecastResponse


class ForecastStatisticsResponse(BaseModel):
    """Forecast statistics for a cycle"""
    totalForecasts: int
    draftForecasts: int
    submittedForecasts: int
    approvedForecasts: int
    rejectedForecasts: int
    totalQuantity: float
    totalRevenue: float


class MessageResponse(BaseModel):
    """Generic message response"""
    success: bool = True
    message: str


class BulkImportResponse(BaseModel):
    """Response after bulk forecast import"""
    success: bool = True
    message: str
    imported: int = Field(..., description="Number of forecasts successfully imported")
    failed: int = Field(0, description="Number of forecasts that failed to import")
    errors: List[str] = Field(default_factory=list, description="List of error messages")
