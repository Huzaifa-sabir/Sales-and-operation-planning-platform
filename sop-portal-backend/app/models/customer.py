from pydantic import BaseModel, Field
from typing import Optional, Dict, Any
from datetime import datetime


class CustomerLocation(BaseModel):
    """Customer location information"""
    address: Optional[str] = None
    city: Optional[str] = None
    state: Optional[str] = None
    zipCode: Optional[str] = None
    country: Optional[str] = None


class CustomerBase(BaseModel):
    """Base customer model"""
    customerId: str = Field(..., description="Unique customer ID")
    customerName: str = Field(..., min_length=1, description="Customer legal name")
    sopCustomerName: Optional[str] = Field(None, description="Customer name for S&OP reports")
    salesRepId: str = Field(..., description="Assigned sales rep user ID")
    salesRepName: str = Field(..., description="Sales rep name for display")
    location: CustomerLocation = Field(default_factory=CustomerLocation, description="Customer location")
    contactPerson: Optional[str] = Field(None, description="Primary contact person")
    contactEmail: Optional[str] = Field(None, description="Contact email")
    contactPhone: Optional[str] = Field(None, description="Contact phone")
    paymentTerms: Optional[str] = Field(None, description="Payment terms (e.g., Net 30)")
    isActive: bool = Field(default=True, description="Whether customer is active")
    metadata: Optional[Dict[str, Any]] = Field(default=None, description="Additional metadata")


class CustomerCreate(CustomerBase):
    """Model for creating a customer"""
    pass


class CustomerUpdate(BaseModel):
    """Model for updating a customer"""
    customerName: Optional[str] = Field(None, min_length=1)
    sopCustomerName: Optional[str] = None
    salesRepId: Optional[str] = None
    salesRepName: Optional[str] = None
    location: Optional[CustomerLocation] = None
    contactPerson: Optional[str] = None
    contactEmail: Optional[str] = None
    contactPhone: Optional[str] = None
    paymentTerms: Optional[str] = None
    isActive: Optional[bool] = None
    metadata: Optional[Dict[str, Any]] = None


class CustomerInDB(CustomerBase):
    """Customer model as stored in database"""
    id: str = Field(..., alias="_id", description="Customer document ID")
    createdAt: datetime = Field(default_factory=datetime.utcnow)
    updatedAt: datetime = Field(default_factory=datetime.utcnow)

    class Config:
        populate_by_name = True
        json_schema_extra = {
            "example": {
                "_id": "507f1f77bcf86cd799439011",
                "customerId": "CUST-001",
                "customerName": "ABC Corporation",
                "sopCustomerName": "ABC Corp",
                "salesRepId": "507f1f77bcf86cd799439012",
                "salesRepName": "John Doe",
                "location": {
                    "city": "Miami",
                    "state": "FL",
                    "country": "USA"
                },
                "isActive": True,
                "createdAt": "2024-01-01T00:00:00",
                "updatedAt": "2024-01-01T00:00:00"
            }
        }


class CustomerResponse(CustomerBase):
    """Customer response model"""
    id: str = Field(..., alias="_id")
    createdAt: datetime
    updatedAt: datetime

    class Config:
        populate_by_name = True
        from_attributes = True
