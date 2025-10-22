from pydantic import BaseModel, EmailStr, Field
from typing import Optional, Dict, Any
from datetime import datetime
from enum import Enum


class UserRole(str, Enum):
    """User role enumeration"""
    ADMIN = "admin"
    SALES_REP = "sales_rep"


class UserBase(BaseModel):
    """Base user model with common fields"""
    username: str = Field(..., min_length=3, max_length=50, description="Unique username")
    email: EmailStr = Field(..., description="User email address")
    fullName: str = Field(..., min_length=1, max_length=100, description="Full name of user")
    role: UserRole = Field(default=UserRole.SALES_REP, description="User role")
    isActive: bool = Field(default=True, description="Whether user is active")
    metadata: Optional[Dict[str, Any]] = Field(default=None, description="Additional user metadata")


class UserCreate(UserBase):
    """Model for creating a new user"""
    password: Optional[str] = Field(None, min_length=8, description="User password (optional, will be auto-generated if not provided)")


class UserUpdate(BaseModel):
    """Model for updating a user"""
    email: Optional[EmailStr] = None
    fullName: Optional[str] = Field(None, min_length=1, max_length=100)
    role: Optional[UserRole] = None
    isActive: Optional[bool] = None
    metadata: Optional[Dict[str, Any]] = None


class UserInDB(UserBase):
    """User model as stored in database"""
    id: str = Field(..., alias="_id", description="User ID")
    hashedPassword: str = Field(..., description="Hashed password")
    loginAttempts: int = Field(default=0, description="Failed login attempts")
    lastLogin: Optional[datetime] = Field(default=None, description="Last login timestamp")
    passwordChangedAt: Optional[datetime] = Field(default=None, description="Password last changed")
    createdAt: datetime = Field(default_factory=datetime.utcnow, description="Creation timestamp")
    updatedAt: datetime = Field(default_factory=datetime.utcnow, description="Last update timestamp")

    class Config:
        populate_by_name = True
        json_schema_extra = {
            "example": {
                "_id": "507f1f77bcf86cd799439011",
                "username": "jdoe",
                "email": "john.doe@example.com",
                "fullName": "John Doe",
                "role": "sales_rep",
                "isActive": True,
                "hashedPassword": "$2b$12$...",
                "loginAttempts": 0,
                "createdAt": "2024-01-01T00:00:00",
                "updatedAt": "2024-01-01T00:00:00"
            }
        }


class UserResponse(UserBase):
    """User response model (without sensitive data)"""
    id: str = Field(..., alias="_id", description="User ID")
    loginAttempts: int = Field(default=0)
    lastLogin: Optional[datetime] = None
    createdAt: datetime
    updatedAt: datetime

    class Config:
        populate_by_name = True
        from_attributes = True
