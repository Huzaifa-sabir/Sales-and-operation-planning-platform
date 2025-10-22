"""
User API Schemas
Request and response models for user management endpoints
"""
from typing import Optional, List
from datetime import datetime
from pydantic import BaseModel, Field, EmailStr, field_validator

from app.models.user import UserRole, UserResponse


class UserCreateRequest(BaseModel):
    """Request schema for creating a new user"""
    username: str = Field(..., min_length=3, max_length=50, description="Unique username")
    email: EmailStr = Field(..., description="User email address")
    fullName: str = Field(..., min_length=1, max_length=100, description="User's full name")
    role: UserRole = Field(..., description="User role (admin or sales_rep)")

    @field_validator('username')
    @classmethod
    def username_alphanumeric(cls, v: str) -> str:
        """Validate username is alphanumeric with underscores/hyphens"""
        if not v.replace('_', '').replace('-', '').isalnum():
            raise ValueError('Username must be alphanumeric (underscores and hyphens allowed)')
        return v.lower()


class UserCreateResponse(BaseModel):
    """Response schema for created user with generated password"""
    user: UserResponse
    generatedPassword: str = Field(..., description="Generated password for the user")
    message: str = Field(default="User created successfully. Please save the password.")


class UserUpdateRequest(BaseModel):
    """Request schema for updating user information"""
    username: Optional[str] = Field(None, min_length=3, max_length=50)
    email: Optional[EmailStr] = None
    fullName: Optional[str] = Field(None, min_length=1, max_length=100)
    role: Optional[UserRole] = None

    @field_validator('username')
    @classmethod
    def username_alphanumeric(cls, v: Optional[str]) -> Optional[str]:
        """Validate username is alphanumeric with underscores/hyphens"""
        if v and not v.replace('_', '').replace('-', '').isalnum():
            raise ValueError('Username must be alphanumeric (underscores and hyphens allowed)')
        return v.lower() if v else None


class UserListResponse(BaseModel):
    """Response schema for paginated user list"""
    users: List[UserResponse]
    total: int = Field(..., description="Total number of users")
    page: int = Field(..., description="Current page number")
    pageSize: int = Field(..., description="Number of items per page")
    totalPages: int = Field(..., description="Total number of pages")
    hasNext: bool = Field(..., description="Whether there are more pages")
    hasPrev: bool = Field(..., description="Whether there are previous pages")


class UserFilterParams(BaseModel):
    """Query parameters for filtering users"""
    page: int = Field(default=1, ge=1, description="Page number")
    pageSize: int = Field(default=10, ge=1, le=100, description="Items per page")
    role: Optional[str] = Field(None, description="Filter by role (admin/sales_rep)")
    isActive: Optional[bool] = Field(None, description="Filter by active status")
    search: Optional[str] = Field(None, description="Search in username, email, fullName")


class PasswordResetRequestSchema(BaseModel):
    """Request schema for password reset"""
    email: EmailStr = Field(..., description="Email address for password reset")


class PasswordResetConfirmSchema(BaseModel):
    """Request schema for confirming password reset"""
    token: str = Field(..., min_length=1, description="Password reset token")
    newPassword: str = Field(..., min_length=8, max_length=100, description="New password")

    @field_validator('newPassword')
    @classmethod
    def password_strength(cls, v: str) -> str:
        """Validate password strength"""
        if len(v) < 8:
            raise ValueError('Password must be at least 8 characters long')
        if not any(c.isupper() for c in v):
            raise ValueError('Password must contain at least one uppercase letter')
        if not any(c.islower() for c in v):
            raise ValueError('Password must contain at least one lowercase letter')
        if not any(c.isdigit() for c in v):
            raise ValueError('Password must contain at least one digit')
        return v


class MessageResponse(BaseModel):
    """Generic message response"""
    message: str
    success: bool = Field(default=True)
