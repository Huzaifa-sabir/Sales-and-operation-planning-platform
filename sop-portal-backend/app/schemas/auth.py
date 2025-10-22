"""
Authentication request/response schemas
"""
from pydantic import BaseModel, Field
from typing import Optional


class LoginRequest(BaseModel):
    """Login request schema - accepts either username or email"""
    username: Optional[str] = Field(None, min_length=3, description="Username (deprecated, use email)")
    email: Optional[str] = Field(None, description="Email address")
    password: str = Field(..., min_length=1, description="Password")

    class Config:
        json_schema_extra = {
            "example": {
                "email": "admin@sopportal.com",
                "password": "admin123"
            }
        }


class TokenResponse(BaseModel):
    """Token response schema"""
    accessToken: str = Field(..., alias="access_token", description="JWT access token")
    tokenType: str = Field(default="bearer", alias="token_type", description="Token type")
    user: dict = Field(..., description="User information")

    class Config:
        populate_by_name = True
        json_schema_extra = {
            "example": {
                "accessToken": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
                "tokenType": "bearer",
                "user": {
                    "_id": "507f1f77bcf86cd799439011",
                    "username": "admin",
                    "email": "admin@sopportal.com",
                    "fullName": "Admin User",
                    "role": "admin",
                    "isActive": True
                }
            }
        }


class PasswordChangeRequest(BaseModel):
    """Password change request schema"""
    old_password: str = Field(..., min_length=1, description="Current password")
    new_password: str = Field(..., min_length=8, description="New password")

    class Config:
        json_schema_extra = {
            "example": {
                "old_password": "oldpassword123",
                "new_password": "newpassword123"
            }
        }


class PasswordResetRequest(BaseModel):
    """Password reset request schema (for admin)"""
    new_password: str = Field(..., min_length=8, description="New password")

    class Config:
        json_schema_extra = {
            "example": {
                "new_password": "newpassword123"
            }
        }


class MessageResponse(BaseModel):
    """Generic message response"""
    message: str = Field(..., description="Response message")

    class Config:
        json_schema_extra = {
            "example": {
                "message": "Operation completed successfully"
            }
        }
