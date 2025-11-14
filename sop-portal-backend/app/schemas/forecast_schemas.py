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


class BulkCreateForecastRequest(BaseModel):
    """Request to create multiple forecasts for one customer"""
    cycleId: str = Field(..., description="S&OP cycle ID")
    customerId: str = Field(..., description="Customer ID")
    forecasts: List[dict] = Field(..., description="List of forecast data: [{productId, monthlyForecasts, useCustomerPrice?, overridePrice?, notes?}]")


class BulkCreateForecastResponse(BaseModel):
    """Response after bulk forecast creation"""
    success: bool = True
    message: str
    forecasts: List[ForecastResponse] = Field(..., description="List of created/updated forecasts")
    created: int = Field(..., description="Number of forecasts created")
    updated: int = Field(..., description="Number of forecasts updated")
