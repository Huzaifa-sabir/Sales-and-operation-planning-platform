from pydantic import BaseModel, Field
from typing import List, Optional, Dict, Any
from datetime import datetime
from enum import Enum


class ForecastStatus(str, Enum):
    """Forecast status"""
    DRAFT = "draft"
    SUBMITTED = "submitted"
    APPROVED = "approved"
    REJECTED = "rejected"


class MonthlyForecast(BaseModel):
    """Monthly forecast data"""
    year: int = Field(..., description="Year")
    month: int = Field(..., ge=1, le=12, description="Month (1-12)")
    monthLabel: str = Field(..., description="Month in YYYY-MM format")
    quantity: float = Field(0, ge=0, description="Forecasted quantity")
    unitPrice: Optional[float] = Field(None, ge=0, description="Unit price (customer-specific or override)")
    revenue: Optional[float] = Field(None, ge=0, description="Calculated revenue (quantity * unitPrice)")
    notes: Optional[str] = Field(None, description="Notes for this specific month")
    isHistorical: bool = Field(False, description="Whether this is a historical month")
    isCurrent: bool = Field(False, description="Whether this is the current month")
    isFuture: bool = Field(True, description="Whether this is a future forecast month")


class ForecastCreate(BaseModel):
    """Model for creating a forecast"""
    cycleId: str = Field(..., description="S&OP Cycle ID")
    customerId: str = Field(..., description="Customer ID")
    productId: str = Field(..., description="Product ID (item code)")
    monthlyForecasts: List[MonthlyForecast] = Field(default_factory=list, description="Monthly forecast breakdown (16 months)")
    useCustomerPrice: bool = Field(True, description="Use customer-specific price from matrix")
    overridePrice: Optional[float] = Field(None, ge=0, description="Override price if not using customer price")
    notes: Optional[str] = Field(None, description="General notes for this forecast")


class ForecastUpdate(BaseModel):
    """Model for updating a forecast"""
    monthlyForecasts: Optional[List[MonthlyForecast]] = Field(None, description="Updated monthly forecast data")
    useCustomerPrice: Optional[bool] = Field(None, description="Use customer-specific price")
    overridePrice: Optional[float] = Field(None, ge=0, description="Override price")
    notes: Optional[str] = Field(None, description="Updated notes")


class ForecastInDB(BaseModel):
    """Forecast model as stored in database"""
    id: str = Field(..., alias="_id", description="Forecast document ID")
    cycleId: str = Field(..., description="S&OP Cycle ID")
    customerId: str = Field(..., description="Customer ID")
    productId: str = Field(..., description="Product ID (item code)")
    salesRepId: str = Field(..., description="Sales rep user ID")
    status: ForecastStatus = Field(default=ForecastStatus.DRAFT, description="Forecast status")

    # Monthly breakdown (16 months)
    monthlyForecasts: List[MonthlyForecast] = Field(default_factory=list, description="Monthly forecast data")

    # Pricing
    useCustomerPrice: bool = Field(True, description="Use customer-specific price from matrix")
    overridePrice: Optional[float] = Field(None, description="Override price")

    # Calculated totals
    totalQuantity: float = Field(0, description="Sum of all monthly quantities")
    totalRevenue: float = Field(0, description="Sum of all monthly revenues")

    # Version tracking for revisions
    version: int = Field(1, description="Forecast version number")
    previousVersionId: Optional[str] = Field(None, description="Reference to previous version if revised")

    # Notes
    notes: Optional[str] = Field(None, description="General notes")

    # Metadata
    createdAt: datetime = Field(default_factory=datetime.utcnow)
    updatedAt: datetime = Field(default_factory=datetime.utcnow)
    submittedAt: Optional[datetime] = Field(None, description="When forecast was submitted")

    class Config:
        populate_by_name = True
        json_encoders = {datetime: lambda v: v.isoformat()}


class ForecastResponse(BaseModel):
    """Forecast response model"""
    id: str = Field(..., description="Forecast ID")
    cycleId: str = Field(..., description="S&OP Cycle ID")
    customerId: str = Field(..., description="Customer ID")
    productId: str = Field(..., description="Product ID")
    salesRepId: str = Field(..., description="Sales rep user ID")
    status: ForecastStatus = Field(..., description="Forecast status")

    monthlyForecasts: List[MonthlyForecast] = Field(default_factory=list)

    useCustomerPrice: bool = Field(True)
    overridePrice: Optional[float] = None

    totalQuantity: float = Field(0)
    totalRevenue: float = Field(0)

    version: int = Field(1)
    previousVersionId: Optional[str] = None

    notes: Optional[str] = None

    createdAt: datetime
    updatedAt: datetime
    submittedAt: Optional[datetime] = None

    # Optional enriched data (populated from lookups)
    customerName: Optional[str] = None
    productDescription: Optional[str] = None
    salesRepName: Optional[str] = None
    cycleName: Optional[str] = None

    class Config:
        populate_by_name = True
        from_attributes = True


class ForecastSubmitRequest(BaseModel):
    """Request to submit a forecast"""
    forecastId: str = Field(..., description="Forecast ID to submit")


class BulkForecastData(BaseModel):
    """Single forecast data for bulk import"""
    customerId: str
    productId: str
    monthlyForecasts: List[MonthlyForecast]
    useCustomerPrice: bool = True
    overridePrice: Optional[float] = None
    notes: Optional[str] = None


class ForecastBulkCreateRequest(BaseModel):
    """Bulk create forecasts from Excel"""
    cycleId: str = Field(..., description="S&OP cycle ID")
    forecasts: List[BulkForecastData] = Field(..., description="List of forecast data")
