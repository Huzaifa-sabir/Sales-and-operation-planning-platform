"""
Product API Schemas
Request and response models for product management endpoints
"""
from typing import Optional, List
from pydantic import BaseModel, Field

from app.models.product import (
    ProductGroup,
    ProductManufacturing,
    ProductPricing,
    ProductResponse
)


class ProductCreateRequest(BaseModel):
    """Request schema for creating a new product"""
    itemCode: str = Field(..., min_length=1, max_length=50, description="Unique item code (e.g., 110001)")
    itemDescription: str = Field(..., min_length=1, max_length=500, description="Product description")
    group: Optional[ProductGroup] = Field(None, description="Product group/category")
    manufacturing: Optional[ProductManufacturing] = Field(None, description="Manufacturing details")
    pricing: Optional[ProductPricing] = Field(None, description="Pricing information")
    weight: Optional[float] = Field(None, ge=0, description="Product weight")
    uom: Optional[str] = Field(None, description="Unit of measure (CS, BAG, etc.)")


class ProductUpdateRequest(BaseModel):
    """Request schema for updating product information"""
    itemCode: Optional[str] = Field(None, min_length=1, max_length=50)
    itemDescription: Optional[str] = Field(None, min_length=1, max_length=500)
    group: Optional[ProductGroup] = None
    manufacturing: Optional[ProductManufacturing] = None
    pricing: Optional[ProductPricing] = None
    weight: Optional[float] = Field(None, ge=0)
    uom: Optional[str] = None


class ProductListResponse(BaseModel):
    """Response schema for paginated product list"""
    products: List[ProductResponse]
    total: int = Field(..., description="Total number of products")
    page: int = Field(..., description="Current page number")
    pageSize: int = Field(..., description="Number of items per page")
    totalPages: int = Field(..., description="Total number of pages")
    hasNext: bool = Field(..., description="Whether there are more pages")
    hasPrev: bool = Field(..., description="Whether there are previous pages")


class MessageResponse(BaseModel):
    """Generic message response"""
    message: str
    success: bool = Field(default=True)
