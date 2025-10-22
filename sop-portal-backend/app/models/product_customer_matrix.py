from pydantic import BaseModel, Field
from typing import Optional
from datetime import datetime


class ProductCustomerMatrixBase(BaseModel):
    """Product-Customer relationship matrix"""
    customerId: str = Field(..., description="Customer ID")
    customerName: str = Field(..., description="Customer name")
    productId: str = Field(..., description="Product ID")
    productCode: str = Field(..., description="Product item code")
    productDescription: str = Field(..., description="Product description")
    isActive: bool = Field(default=True, description="Whether relationship is active")
    customerSpecificPrice: Optional[float] = Field(None, ge=0, description="Customer-specific price")
    lastOrderDate: Optional[datetime] = Field(None, description="Last order date")
    totalOrdersQty: Optional[float] = Field(None, ge=0, description="Total orders quantity")
    notes: Optional[str] = Field(None, description="Additional notes")


class ProductCustomerMatrixCreate(ProductCustomerMatrixBase):
    """Model for creating product-customer relationship"""
    pass


class ProductCustomerMatrixUpdate(BaseModel):
    """Model for updating product-customer relationship"""
    isActive: Optional[bool] = None
    customerSpecificPrice: Optional[float] = Field(None, ge=0)
    lastOrderDate: Optional[datetime] = None
    totalOrdersQty: Optional[float] = Field(None, ge=0)
    notes: Optional[str] = None


class ProductCustomerMatrixInDB(ProductCustomerMatrixBase):
    """Product-Customer matrix model as stored in database"""
    id: str = Field(..., alias="_id", description="Matrix document ID")
    createdAt: datetime = Field(default_factory=datetime.utcnow)
    updatedAt: datetime = Field(default_factory=datetime.utcnow)

    class Config:
        populate_by_name = True
        json_schema_extra = {
            "example": {
                "_id": "507f1f77bcf86cd799439011",
                "customerId": "CUST-001",
                "customerName": "ABC Corporation",
                "productId": "507f1f77bcf86cd799439012",
                "productCode": "110001",
                "productDescription": "Peeled Garlic 12x1 LB",
                "isActive": True,
                "customerSpecificPrice": 50.0,
                "lastOrderDate": "2024-10-01T00:00:00Z",
                "totalOrdersQty": 1000.0,
                "createdAt": "2024-01-01T00:00:00Z",
                "updatedAt": "2024-10-01T00:00:00Z"
            }
        }


class ProductCustomerMatrixResponse(ProductCustomerMatrixBase):
    """Product-Customer matrix response model"""
    id: str = Field(..., alias="_id")
    createdAt: datetime
    updatedAt: datetime

    class Config:
        populate_by_name = True
        from_attributes = True
