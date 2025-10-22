"""
Product-Customer Matrix API Schemas
Request and response models for matrix management endpoints
"""
from typing import Optional, List
from pydantic import BaseModel, Field

from app.models.product_customer_matrix import ProductCustomerMatrixResponse


class MatrixCreateRequest(BaseModel):
    """Request schema for creating a new matrix entry"""
    customerId: str = Field(..., description="Customer ID")
    productId: str = Field(..., description="Product item code")
    customerPrice: Optional[float] = Field(None, ge=0, description="Customer-specific price")
    minimumOrderQty: Optional[int] = Field(None, ge=0, description="Minimum order quantity")
    maximumOrderQty: Optional[int] = Field(None, ge=0, description="Maximum order quantity")
    leadTimeDays: Optional[int] = Field(None, ge=0, description="Lead time in days")


class MatrixUpdateRequest(BaseModel):
    """Request schema for updating matrix entry"""
    customerPrice: Optional[float] = Field(None, ge=0)
    minimumOrderQty: Optional[int] = Field(None, ge=0)
    maximumOrderQty: Optional[int] = Field(None, ge=0)
    leadTimeDays: Optional[int] = Field(None, ge=0)


class MatrixListResponse(BaseModel):
    """Response schema for paginated matrix list"""
    entries: List[ProductCustomerMatrixResponse]
    total: int = Field(..., description="Total number of entries")
    page: int = Field(..., description="Current page number")
    pageSize: int = Field(..., description="Number of items per page")
    totalPages: int = Field(..., description="Total number of pages")
    hasNext: bool = Field(..., description="Whether there are more pages")
    hasPrev: bool = Field(..., description="Whether there are previous pages")


class BulkMatrixCreateRequest(BaseModel):
    """Request schema for bulk creating matrix entries"""
    entries: List[MatrixCreateRequest] = Field(..., min_length=1, description="List of matrix entries to create")


class BulkMatrixCreateResponse(BaseModel):
    """Response schema for bulk create operation"""
    created: List[ProductCustomerMatrixResponse]
    failed: List[dict]
    totalCreated: int
    totalFailed: int


class MessageResponse(BaseModel):
    """Generic message response"""
    message: str
    success: bool = Field(default=True)
