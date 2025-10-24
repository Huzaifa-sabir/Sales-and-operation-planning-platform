"""
User Management Router
Handles all user CRUD operations, filtering, and password reset
"""
from typing import Optional
from fastapi import APIRouter, Depends, HTTPException, status, Query
from motor.motor_asyncio import AsyncIOMotorDatabase

from app.config.database import get_db
from app.models.user import UserInDB, UserResponse, UserCreate, UserUpdate
from app.schemas.user_schemas import (
    UserCreateRequest,
    UserCreateResponse,
    UserUpdateRequest,
    UserListResponse,
    PasswordResetRequestSchema,
    PasswordResetConfirmSchema,
    MessageResponse
)
from app.services.user_service import UserService
from app.utils.auth_dependencies import require_admin, get_current_active_user

router = APIRouter(prefix="/users", tags=["User Management"])


@router.post(
    "",
    response_model=UserCreateResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Create a new user",
    description="Create a new user with auto-generated password. Admin only."
)
async def create_user(
    user_data: UserCreateRequest,
    db: AsyncIOMotorDatabase = Depends(get_db),
    current_user: UserInDB = Depends(require_admin)
):
    """
    Create a new user (Admin only)

    - **username**: Unique username (alphanumeric, underscores, hyphens)
    - **email**: Valid email address
    - **fullName**: User's full name
    - **role**: User role (admin or sales_rep)

    Returns the created user with a generated password that should be saved.
    """
    user_service = UserService(db)

    # Convert request to UserCreate model
    user_create = UserCreate(
        username=user_data.username,
        email=user_data.email,
        fullName=user_data.fullName,
        role=user_data.role,
        password=user_data.password  # Pass password from request
    )

    created_user, generated_password = await user_service.create_user(user_create)

    # Convert to UserResponse (excluding sensitive fields)
    user_response = UserResponse(
        id=created_user.id,
        username=created_user.username,
        email=created_user.email,
        fullName=created_user.fullName,
        role=created_user.role,
        isActive=created_user.isActive,
        createdAt=created_user.createdAt,
        updatedAt=created_user.updatedAt,
        lastLogin=created_user.lastLogin,
        loginAttempts=created_user.loginAttempts
    )

    return UserCreateResponse(
        user=user_response,
        generatedPassword=generated_password
    )


@router.get(
    "",
    response_model=UserListResponse,
    summary="List all users",
    description="Get paginated list of users with optional filtering. Admin only."
)
async def list_users(
    page: int = Query(default=1, ge=1, description="Page number"),
    pageSize: int = Query(default=10, ge=1, le=100, description="Items per page"),
    role: Optional[str] = Query(None, description="Filter by role (admin/sales_rep)"),
    isActive: Optional[bool] = Query(None, description="Filter by active status"),
    search: Optional[str] = Query(None, description="Search in username, email, fullName"),
    db: AsyncIOMotorDatabase = Depends(get_db),
    current_user: UserInDB = Depends(require_admin)
):
    """
    List users with pagination and filtering (Admin only)

    - **page**: Page number (default: 1)
    - **pageSize**: Items per page (default: 10, max: 100)
    - **role**: Filter by role (optional)
    - **isActive**: Filter by active status (optional)
    - **search**: Search in username, email, or full name (optional)
    """
    user_service = UserService(db)

    skip = (page - 1) * pageSize

    result = await user_service.list_users(
        skip=skip,
        limit=pageSize,
        role=role,
        is_active=isActive,
        search=search
    )

    # Convert users to UserResponse
    user_responses = [
        UserResponse(
            id=user.id,
            username=user.username,
            email=user.email,
            fullName=user.fullName,
            role=user.role,
            isActive=user.isActive,
            createdAt=user.createdAt,
            updatedAt=user.updatedAt,
            lastLogin=user.lastLogin
        )
        for user in result["users"]
    ]

    return UserListResponse(
        users=user_responses,
        total=result["total"],
        page=result["page"],
        pageSize=result["pageSize"],
        totalPages=result["totalPages"],
        hasNext=result["hasNext"],
        hasPrev=result["hasPrev"]
    )


@router.get(
    "/{user_id}",
    response_model=UserResponse,
    summary="Get user by ID",
    description="Get a specific user by their ID. Admin only."
)
async def get_user(
    user_id: str,
    db: AsyncIOMotorDatabase = Depends(get_db),
    current_user: UserInDB = Depends(require_admin)
):
    """
    Get user by ID (Admin only)

    - **user_id**: User ID
    """
    user_service = UserService(db)
    user = await user_service.get_user_by_id(user_id)

    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )

    return UserResponse(
        id=user.id,
        username=user.username,
        email=user.email,
        fullName=user.fullName,
        role=user.role,
        isActive=user.isActive,
        createdAt=user.createdAt,
        updatedAt=user.updatedAt,
        lastLogin=user.lastLogin
    )


@router.put(
    "/{user_id}",
    response_model=UserResponse,
    summary="Update user",
    description="Update user information. Admin only."
)
async def update_user(
    user_id: str,
    user_update: UserUpdateRequest,
    db: AsyncIOMotorDatabase = Depends(get_db),
    current_user: UserInDB = Depends(require_admin)
):
    """
    Update user information (Admin only)

    - **user_id**: User ID
    - **username**: New username (optional)
    - **email**: New email (optional)
    - **fullName**: New full name (optional)
    - **role**: New role (optional)
    """
    user_service = UserService(db)

    # Convert request to UserUpdate model
    update_data = UserUpdate(
        username=user_update.username,
        email=user_update.email,
        fullName=user_update.fullName,
        role=user_update.role
    )

    updated_user = await user_service.update_user(user_id, update_data)

    if not updated_user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )

    return UserResponse(
        id=updated_user.id,
        username=updated_user.username,
        email=updated_user.email,
        fullName=updated_user.fullName,
        role=updated_user.role,
        isActive=updated_user.isActive,
        createdAt=updated_user.createdAt,
        updatedAt=updated_user.updatedAt,
        lastLogin=updated_user.lastLogin
    )


@router.patch(
    "/{user_id}/toggle-status",
    response_model=UserResponse,
    summary="Toggle user status",
    description="Toggle user active/inactive status. Admin only."
)
async def toggle_user_status(
    user_id: str,
    db: AsyncIOMotorDatabase = Depends(get_db),
    current_user: UserInDB = Depends(require_admin)
):
    """
    Toggle user active/inactive status (Admin only)

    - **user_id**: User ID

    Cannot deactivate the last admin user.
    """
    user_service = UserService(db)
    updated_user = await user_service.toggle_user_status(user_id)

    if not updated_user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )

    return UserResponse(
        id=updated_user.id,
        username=updated_user.username,
        email=updated_user.email,
        fullName=updated_user.fullName,
        role=updated_user.role,
        isActive=updated_user.isActive,
        createdAt=updated_user.createdAt,
        updatedAt=updated_user.updatedAt,
        lastLogin=updated_user.lastLogin
    )


@router.delete(
    "/{user_id}",
    response_model=MessageResponse,
    summary="Delete user",
    description="Delete (deactivate) a user. Admin only."
)
async def delete_user(
    user_id: str,
    db: AsyncIOMotorDatabase = Depends(get_db),
    current_user: UserInDB = Depends(require_admin)
):
    """
    Delete a user (soft delete by deactivating) (Admin only)

    - **user_id**: User ID

    Cannot delete the last admin user.
    """
    user_service = UserService(db)
    success = await user_service.delete_user(user_id)

    if not success:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )

    return MessageResponse(
        message="User deleted successfully",
        success=True
    )


@router.post(
    "/password-reset/request",
    response_model=MessageResponse,
    summary="Request password reset",
    description="Request a password reset token via email"
)
async def request_password_reset(
    request_data: PasswordResetRequestSchema,
    db: AsyncIOMotorDatabase = Depends(get_db)
):
    """
    Request password reset (Public endpoint)

    - **email**: Email address for password reset

    Sends a password reset token to the email if it exists.
    For security, always returns success even if email doesn't exist.
    """
    user_service = UserService(db)
    reset_token = await user_service.generate_password_reset_token(request_data.email)

    # In production, send email with reset token here
    # For now, we'll just log it (in real app, never expose token in response)
    if reset_token:
        print(f"Password reset token for {request_data.email}: {reset_token}")
        # TODO: Send email with reset link containing token

    # Always return success for security (don't reveal if email exists)
    return MessageResponse(
        message="If the email exists, a password reset link has been sent.",
        success=True
    )


@router.post(
    "/password-reset/confirm",
    response_model=MessageResponse,
    summary="Confirm password reset",
    description="Reset password using the reset token"
)
async def confirm_password_reset(
    reset_data: PasswordResetConfirmSchema,
    db: AsyncIOMotorDatabase = Depends(get_db)
):
    """
    Confirm password reset with token (Public endpoint)

    - **token**: Password reset token received via email
    - **newPassword**: New password (min 8 chars, must contain uppercase, lowercase, digit)
    """
    user_service = UserService(db)
    success = await user_service.reset_password_with_token(
        reset_data.token,
        reset_data.newPassword
    )

    return MessageResponse(
        message="Password has been reset successfully. You can now login with your new password.",
        success=True
    )
