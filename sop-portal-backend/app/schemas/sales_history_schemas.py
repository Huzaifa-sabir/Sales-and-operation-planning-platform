"""
Sales History API Schemas
Request and response models for sales history endpoints
"""
from typing import List, Optional
from datetime import datetime
from pydantic import BaseModel, Field

from app.models.sales_history import SalesHistoryResponse


class SalesHistoryListResponse(BaseModel):
    """Response schema for paginated sales history list"""
    records: List[SalesHistoryResponse]
    total: int = Field(..., description="Total number of records")
    page: int = Field(..., description="Current page number")
    pageSize: int = Field(..., description="Number of items per page")
    totalPages: int = Field(..., description="Total number of pages")
    hasNext: bool = Field(..., description="Whether there are more pages")
    hasPrev: bool = Field(..., description="Whether there are previous pages")


class SalesStatisticsResponse(BaseModel):
    """Response schema for sales statistics"""
    totalQuantity: float = Field(..., description="Total quantity sold")
    totalRevenue: float = Field(..., description="Total revenue")
    avgQuantity: float = Field(..., description="Average quantity per transaction")
    avgUnitPrice: float = Field(..., description="Average unit price")
    recordCount: int = Field(..., description="Number of sales records")
    minQuantity: float = Field(..., description="Minimum quantity in a transaction")
    maxQuantity: float = Field(..., description="Maximum quantity in a transaction")


class MonthlySalesResponse(BaseModel):
    """Response schema for monthly aggregated sales"""
    year: int
    month: int
    monthLabel: str = Field(..., description="Month in YYYY-MM format")
    totalQuantity: float
    totalRevenue: float
    recordCount: int


class TopProductResponse(BaseModel):
    """Response schema for top products"""
    productId: str
    totalQuantity: float
    totalRevenue: float
    avgUnitPrice: float


class TopCustomerResponse(BaseModel):
    """Response schema for top customers"""
    customerId: str
    totalQuantity: float
    totalRevenue: float
    avgUnitPrice: float


class SalesHistoryCreateRequest(BaseModel):
    """Request schema for creating a sales history record"""
    customerId: str = Field(..., description="Customer ID")
    productId: str = Field(..., description="Product ID (item code)")
    year: int = Field(..., ge=2000, le=2100, description="Year of the sale")
    month: int = Field(..., ge=1, le=12, description="Month of the sale (1-12)")
    quantitySold: float = Field(..., gt=0, description="Quantity sold")
    unitPrice: float = Field(..., gt=0, description="Unit price")


class SalesHistoryUpdateRequest(BaseModel):
    """Request schema for updating a sales history record"""
    customerId: Optional[str] = Field(None, description="Customer ID")
    productId: Optional[str] = Field(None, description="Product ID (item code)")
    year: Optional[int] = Field(None, ge=2000, le=2100, description="Year of the sale")
    month: Optional[int] = Field(None, ge=1, le=12, description="Month of the sale (1-12)")
    quantitySold: Optional[float] = Field(None, gt=0, description="Quantity sold")
    unitPrice: Optional[float] = Field(None, gt=0, description="Unit price")
