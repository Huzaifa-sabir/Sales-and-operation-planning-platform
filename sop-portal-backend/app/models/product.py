from pydantic import BaseModel, Field
from typing import Optional, Dict, Any
from datetime import datetime


class ProductGroup(BaseModel):
    """Product group classification"""
    code: str = Field(..., description="Product group code")
    subgroup: Optional[str] = Field(None, description="Product subgroup")
    desc: Optional[str] = Field(None, description="Group description")


class ProductManufacturing(BaseModel):
    """Product manufacturing details"""
    location: str = Field(..., description="Manufacturing location")
    line: Optional[str] = Field(None, description="Production line")


class ProductPricing(BaseModel):
    """Product pricing information"""
    avgPrice: float = Field(..., ge=0, description="Average selling price")
    costPrice: Optional[float] = Field(None, ge=0, description="Cost price")
    currency: str = Field(default="USD", description="Currency code")


class ProductBase(BaseModel):
    """Base product model"""
    itemCode: str = Field(..., description="Unique item code")
    itemDescription: str = Field(..., min_length=1, description="Product description")
    group: ProductGroup = Field(..., description="Product group")
    manufacturing: ProductManufacturing = Field(..., description="Manufacturing info")
    weight: Optional[float] = Field(None, ge=0, description="Product weight")
    uom: str = Field(..., description="Unit of measure (CS, BAG, etc.)")
    pricing: ProductPricing = Field(..., description="Pricing information")
    isActive: bool = Field(default=True, description="Whether product is active")
    metadata: Optional[Dict[str, Any]] = Field(default=None, description="Additional metadata")


class ProductCreate(ProductBase):
    """Model for creating a product"""
    pass


class ProductUpdate(BaseModel):
    """Model for updating a product"""
    itemDescription: Optional[str] = Field(None, min_length=1)
    group: Optional[ProductGroup] = None
    manufacturing: Optional[ProductManufacturing] = None
    weight: Optional[float] = Field(None, ge=0)
    uom: Optional[str] = None
    pricing: Optional[ProductPricing] = None
    isActive: Optional[bool] = None
    metadata: Optional[Dict[str, Any]] = None


class ProductInDB(ProductBase):
    """Product model as stored in database"""
    id: str = Field(..., alias="_id", description="Product document ID")
    createdAt: datetime = Field(default_factory=datetime.utcnow)
    updatedAt: datetime = Field(default_factory=datetime.utcnow)

    class Config:
        populate_by_name = True
        json_schema_extra = {
            "example": {
                "_id": "507f1f77bcf86cd799439011",
                "itemCode": "110001",
                "itemDescription": "Peeled Garlic 12x1 LB",
                "group": {
                    "code": "G1",
                    "subgroup": "G1S7",
                    "desc": "Group 1-2"
                },
                "manufacturing": {
                    "location": "Miami",
                    "line": "Peeled Garlic Repack"
                },
                "weight": 12.0,
                "uom": "CS",
                "pricing": {
                    "avgPrice": 52.0,
                    "currency": "USD"
                },
                "isActive": True,
                "createdAt": "2024-01-01T00:00:00",
                "updatedAt": "2024-01-01T00:00:00"
            }
        }


class ProductResponse(ProductBase):
    """Product response model"""
    id: str = Field(..., alias="_id")
    createdAt: datetime
    updatedAt: datetime

    class Config:
        populate_by_name = True
        from_attributes = True
