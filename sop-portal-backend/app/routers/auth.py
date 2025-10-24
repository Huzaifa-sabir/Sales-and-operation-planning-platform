"""
Authentication routes
"""
from datetime import datetime
from fastapi import APIRouter, Depends, HTTPException, status
from motor.motor_asyncio import AsyncIOMotorDatabase

from app.config.database import get_db
from app.config.settings import settings
from app.schemas.auth import (
    LoginRequest,
    TokenResponse,
    PasswordChangeRequest,
    MessageResponse
)
from app.models.user import UserResponse, UserInDB
from app.utils.security import verify_password, hash_password
from app.utils.jwt import create_token_response
from app.utils.auth_dependencies import get_current_active_user

router = APIRouter(prefix="/auth", tags=["Authentication"])


@router.post("/login", response_model=TokenResponse, status_code=status.HTTP_200_OK)
async def login(
    credentials: LoginRequest,
    db: AsyncIOMotorDatabase = Depends(get_db)
):
    """
    User login endpoint

    Returns JWT access token if credentials are valid
    Implements login attempt tracking and account lockout
    Accepts either email or username for backward compatibility
    """
    # Validate that at least one identifier is provided
    if not credentials.email and not credentials.username:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Either email or username must be provided"
        )

    # Find user by email (preferred) or username (for backward compatibility)
    # Also check if username field contains an email address
    query = {}
    if credentials.email:
        query = {"email": credentials.email}
    elif credentials.username:
        # Check if username looks like an email address
        if "@" in credentials.username:
            query = {"email": credentials.username}
        else:
            query = {"username": credentials.username}

    user_doc = await db.users.find_one(query)

    if not user_doc:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect email or password"
        )

    # Check if account is locked due to too many failed attempts
    login_attempts = user_doc.get("loginAttempts", 0)
    if login_attempts >= settings.MAX_LOGIN_ATTEMPTS:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail=f"Account locked due to too many failed login attempts. Please contact administrator."
        )

    # Check if user is active
    if not user_doc.get("isActive", False):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Account is inactive"
        )

    # Verify password
    hashed_password = user_doc.get("hashedPassword", "")

    # Add logging for debugging (remove in production)
    import logging
    logger = logging.getLogger(__name__)
    logger.info(f"Login attempt for user: {user_doc.get('username')} (email: {user_doc.get('email')})")
    logger.info(f"Has password hash: {bool(hashed_password)}")

    if not verify_password(credentials.password, hashed_password):
        logger.warning(f"Password verification failed for user: {user_doc.get('username')}")

        # Increment login attempts
        new_attempts = login_attempts + 1
        await db.users.update_one(
            {"_id": user_doc["_id"]},
            {
                "$set": {"loginAttempts": new_attempts},
                "$currentDate": {"updatedAt": True}
            }
        )

        # Check if account should be locked
        remaining_attempts = settings.MAX_LOGIN_ATTEMPTS - new_attempts
        if remaining_attempts <= 0:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Account locked due to too many failed login attempts"
            )

        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=f"Incorrect username or password. {remaining_attempts} attempts remaining."
        )

    # Reset login attempts on successful login
    await db.users.update_one(
        {"_id": user_doc["_id"]},
        {
            "$set": {
                "loginAttempts": 0,
                "lastLogin": datetime.utcnow()
            },
            "$currentDate": {"updatedAt": True}
        }
    )

    # Create token
    user_id = str(user_doc["_id"])
    username = user_doc["username"]
    role = user_doc["role"]

    token_response = create_token_response(user_id, username, role)

    # Build user response matching frontend expectations
    user_response = {
        "_id": user_id,
        "username": user_doc.get("username", ""),
        "email": user_doc.get("email", ""),
        "fullName": user_doc.get("fullName", ""),
        "role": user_doc.get("role", ""),
        "isActive": user_doc.get("isActive", False),
        "lastLogin": user_doc.get("lastLogin").isoformat() if user_doc.get("lastLogin") else None,
        "createdAt": user_doc.get("createdAt").isoformat() if user_doc.get("createdAt") else None,
        "updatedAt": user_doc.get("updatedAt").isoformat() if user_doc.get("updatedAt") else None,
    }

    # Return response with camelCase field names for frontend
    return TokenResponse(
        accessToken=token_response["access_token"],
        tokenType=token_response["token_type"],
        user=user_response
    )


@router.get("/me", response_model=UserResponse)
async def get_current_user_info(
    current_user: UserInDB = Depends(get_current_active_user)
):
    """
    Get current authenticated user information

    Requires valid JWT token in Authorization header
    """
    return current_user


@router.post("/logout", response_model=MessageResponse)
async def logout(
    current_user: UserInDB = Depends(get_current_active_user)
):
    """
    User logout endpoint

    In a stateless JWT system, logout is handled client-side by removing the token
    This endpoint exists for logging purposes and future token blacklisting
    """
    # In a production system, you might want to:
    # 1. Add token to blacklist (requires Redis or similar)
    # 2. Log the logout event
    # 3. Clear any server-side session data

    return MessageResponse(message="Successfully logged out")


@router.post("/change-password", response_model=MessageResponse)
async def change_password(
    password_data: PasswordChangeRequest,
    current_user: UserInDB = Depends(get_current_active_user),
    db: AsyncIOMotorDatabase = Depends(get_db)
):
    """
    Change current user's password

    Requires valid JWT token and current password
    """
    # Get fresh user data from database
    from bson import ObjectId
    user_doc = await db.users.find_one({"_id": ObjectId(current_user.id)})

    if not user_doc:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )

    # Verify old password
    if not verify_password(password_data.old_password, user_doc.get("hashedPassword", "")):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect current password"
        )

    # Hash new password
    new_hashed_password = hash_password(password_data.new_password)

    # Update password in database
    await db.users.update_one(
        {"_id": user_doc["_id"]},
        {
            "$set": {
                "hashedPassword": new_hashed_password,
                "passwordChangedAt": datetime.utcnow()
            },
            "$currentDate": {"updatedAt": True}
        }
    )

    return MessageResponse(message="Password changed successfully")


@router.post("/refresh", response_model=TokenResponse)
async def refresh_token(
    current_user: UserInDB = Depends(get_current_active_user)
):
    """
    Refresh access token

    Returns a new JWT token with extended expiration
    Requires valid JWT token (not expired)
    """
    # Create new token with fresh expiration
    token_response = create_token_response(
        current_user.id,
        current_user.username,
        current_user.role
    )

    # Add CORS headers to response
    from fastapi import Response
    response = Response(content=token_response.json(), media_type="application/json")
    response.headers["Access-Control-Allow-Origin"] = "https://soptest.netlify.app"
    response.headers["Access-Control-Allow-Credentials"] = "true"
    return response
