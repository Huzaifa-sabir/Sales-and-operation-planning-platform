"""
Authentication dependencies for protected routes
"""
from typing import Optional
from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from motor.motor_asyncio import AsyncIOMotorDatabase

from app.config.database import get_db
from app.utils.jwt import decode_access_token
from app.models.user import UserInDB, UserRole

# HTTP Bearer token scheme
security = HTTPBearer()


async def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(security),
    db: AsyncIOMotorDatabase = Depends(get_db)
) -> UserInDB:
    """
    Get current authenticated user from JWT token

    Args:
        credentials: HTTP Bearer token credentials
        db: Database connection

    Returns:
        Current user from database

    Raises:
        HTTPException: If token is invalid or user not found
    """
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )

    # Extract token
    token = credentials.credentials

    # Decode token
    payload = decode_access_token(token)
    if payload is None:
        raise credentials_exception

    # Get user ID from token
    user_id: str = payload.get("sub")
    if user_id is None:
        raise credentials_exception

    # Get user from database
    from bson import ObjectId
    try:
        user_doc = await db.users.find_one({"_id": ObjectId(user_id)})
    except Exception:
        raise credentials_exception

    if user_doc is None:
        raise credentials_exception

    # Check if user is active
    if not user_doc.get("isActive", False):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="User account is inactive"
        )

    # Convert to UserInDB model
    # Convert ObjectId to string for Pydantic
    user_doc["_id"] = str(user_doc["_id"])
    user = UserInDB(**user_doc)

    return user


async def get_current_active_user(
    current_user: UserInDB = Depends(get_current_user)
) -> UserInDB:
    """
    Get current active user (redundant check, but explicit)

    Args:
        current_user: Current user from get_current_user

    Returns:
        Current active user

    Raises:
        HTTPException: If user is not active
    """
    if not current_user.isActive:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Inactive user"
        )
    return current_user


def require_role(*allowed_roles: UserRole):
    """
    Dependency factory to require specific user roles

    Args:
        *allowed_roles: Roles that are allowed to access the endpoint

    Returns:
        Dependency function that checks user role

    Example:
        @app.get("/admin/users", dependencies=[Depends(require_role(UserRole.ADMIN))])
    """
    async def role_checker(current_user: UserInDB = Depends(get_current_active_user)) -> UserInDB:
        if current_user.role not in allowed_roles:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=f"Access denied. Required role: {', '.join([r.value for r in allowed_roles])}"
            )
        return current_user

    return role_checker


# Convenience dependencies
require_admin = require_role(UserRole.ADMIN)
require_sales_rep = require_role(UserRole.SALES_REP)
require_any_role = require_role(UserRole.ADMIN, UserRole.SALES_REP)
