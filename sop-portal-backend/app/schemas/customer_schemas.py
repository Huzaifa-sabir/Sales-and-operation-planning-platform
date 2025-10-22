"""
Customer API Schemas
Request and response models for customer management endpoints
"""
from typing import Optional, List
from pydantic import BaseModel, Field, EmailStr

from app.models.customer import CustomerLocation, CustomerResponse


class CustomerCreateRequest(BaseModel):
    """Request schema for creating a new customer"""
    customerId: str = Field(..., min_length=1, max_length=50, description="Unique customer ID (e.g., PATITO-000001)")
    customerName: str = Field(..., min_length=1, max_length=200, description="Customer name")
    location: Optional[CustomerLocation] = Field(None, description="Customer location details")
    contactPerson: Optional[str] = Field(None, max_length=100, description="Contact person name")
    contactEmail: Optional[EmailStr] = Field(None, description="Contact email")
    contactPhone: Optional[str] = Field(None, max_length=20, description="Contact phone number")
    paymentTerms: Optional[str] = Field(None, max_length=100, description="Payment terms (e.g., Net 30)")
    creditLimit: Optional[float] = Field(None, ge=0, description="Credit limit")


class CustomerUpdateRequest(BaseModel):
    """Request schema for updating customer information"""
    customerId: Optional[str] = Field(None, min_length=1, max_length=50)
    customerName: Optional[str] = Field(None, min_length=1, max_length=200)
    location: Optional[CustomerLocation] = None
    contactPerson: Optional[str] = Field(None, max_length=100)
    contactEmail: Optional[EmailStr] = None
    contactPhone: Optional[str] = Field(None, max_length=20)
    paymentTerms: Optional[str] = Field(None, max_length=100)
    creditLimit: Optional[float] = Field(None, ge=0)


class CustomerListResponse(BaseModel):
    """Response schema for paginated customer list"""
    customers: List[CustomerResponse]
    total: int = Field(..., description="Total number of customers")
    page: int = Field(..., description="Current page number")
    pageSize: int = Field(..., description="Number of items per page")
    totalPages: int = Field(..., description="Total number of pages")
    hasNext: bool = Field(..., description="Whether there are more pages")
    hasPrev: bool = Field(..., description="Whether there are previous pages")


class MessageResponse(BaseModel):
    """Generic message response"""
    message: str
    success: bool = Field(default=True)
