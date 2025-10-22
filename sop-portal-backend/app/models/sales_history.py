from pydantic import BaseModel, Field
from typing import Optional
from datetime import datetime


class SalesHistoryBase(BaseModel):
    """Base sales history model"""
    customerId: str = Field(..., description="Customer ID")
    customerName: str = Field(..., description="Customer name")
    productId: str = Field(..., description="Product ID")
    productCode: str = Field(..., description="Product item code")
    productDescription: str = Field(..., description="Product description")
    yearMonth: str = Field(..., description="Month in YYYY-MM format")
    year: int = Field(..., description="Year")
    month: int = Field(..., ge=1, le=12, description="Month number (1-12)")
    quantity: float = Field(..., ge=0, description="Quantity sold")
    unitPrice: float = Field(..., ge=0, description="Unit price")
    totalSales: float = Field(..., ge=0, description="Total sales amount")
    costPrice: Optional[float] = Field(None, ge=0, description="Cost price")
    cogs: Optional[float] = Field(None, ge=0, description="Cost of goods sold (alias for costPrice)")
    grossProfit: Optional[float] = Field(None, description="Gross profit")
    grossProfitPercent: Optional[float] = Field(None, description="Gross profit percentage")
    salesRepId: str = Field(..., description="Sales rep ID")
    salesRepName: str = Field(..., description="Sales rep name")


class SalesHistoryCreate(SalesHistoryBase):
    """Model for creating sales history record"""
    pass


class SalesHistoryUpdate(BaseModel):
    """Model for updating sales history record"""
    customerId: Optional[str] = Field(None, description="Customer ID")
    customerName: Optional[str] = Field(None, description="Customer name")
    productId: Optional[str] = Field(None, description="Product ID")
    productCode: Optional[str] = Field(None, description="Product item code")
    productDescription: Optional[str] = Field(None, description="Product description")
    yearMonth: Optional[str] = Field(None, description="Month in YYYY-MM format")
    year: Optional[int] = Field(None, description="Year")
    month: Optional[int] = Field(None, ge=1, le=12, description="Month number (1-12)")
    quantity: Optional[float] = Field(None, ge=0, description="Quantity sold")
    unitPrice: Optional[float] = Field(None, ge=0, description="Unit price")
    totalSales: Optional[float] = Field(None, ge=0, description="Total sales amount")
    costPrice: Optional[float] = Field(None, ge=0, description="Cost price")
    cogs: Optional[float] = Field(None, ge=0, description="Cost of goods sold")
    grossProfit: Optional[float] = Field(None, description="Gross profit")
    grossProfitPercent: Optional[float] = Field(None, description="Gross profit percentage")
    salesRepId: Optional[str] = Field(None, description="Sales rep ID")
    salesRepName: Optional[str] = Field(None, description="Sales rep name")


class SalesHistoryInDB(SalesHistoryBase):
    """Sales history model as stored in database"""
    id: str = Field(..., alias="_id", description="Sales history document ID")
    createdAt: datetime = Field(default_factory=datetime.utcnow)

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
                "yearMonth": "2024-01",
                "year": 2024,
                "month": 1,
                "quantity": 100.0,
                "unitPrice": 52.0,
                "totalSales": 5200.0,
                "costPrice": 40.0,
                "cogs": 40.0,
                "grossProfit": 1200.0,
                "grossProfitPercent": 23.08,
                "salesRepId": "507f1f77bcf86cd799439013",
                "salesRepName": "John Doe",
                "createdAt": "2024-01-01T00:00:00"
            }
        }


class SalesHistoryResponse(SalesHistoryBase):
    """Sales history response model"""
    id: str = Field(..., alias="_id")
    createdAt: datetime

    class Config:
        populate_by_name = True
        from_attributes = True
