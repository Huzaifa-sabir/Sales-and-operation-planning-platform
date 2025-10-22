"""
Settings Router
CRUD endpoints for system settings
"""
from fastapi import APIRouter, Depends, HTTPException, status
from typing import List, Optional

from app.models.user import UserInDB
from app.models.settings import (
    SettingCreate,
    SettingUpdate,
    SettingResponse,
    SettingCategory
)
from pydantic import BaseModel
from app.services.settings_service import SettingsService
from app.utils.auth_dependencies import get_current_user, require_admin
from app.config.database import get_db

router = APIRouter(prefix="/settings", tags=["System Settings"])


class SettingsListResponse(BaseModel):
    """Response for settings list"""
    settings: List[SettingResponse]
    total: int


async def get_settings_service():
    """Get settings service"""
    db = await get_db()
    return SettingsService(db)


@router.get("/public", response_model=dict)
async def get_public_settings(
    settings_service: SettingsService = Depends(get_settings_service)
):
    """Get all public settings (no auth required)"""
    return await settings_service.get_public_settings()


@router.get("")
async def list_settings(
    category: Optional[SettingCategory] = None,
    skip: int = 0,
    limit: int = 100,
    current_user: UserInDB = Depends(get_current_user),
    settings_service: SettingsService = Depends(get_settings_service)
):
    """List all settings (admin only)"""
    if current_user.role != "admin":
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Admin access required")

    settings, total = await settings_service.list_settings(category=category, skip=skip, limit=limit)
    return {
        "settings": settings,
        "total": total
    }


@router.get("/{key}", response_model=SettingResponse)
async def get_setting(
    key: str,
    current_user: UserInDB = Depends(get_current_user),
    settings_service: SettingsService = Depends(get_settings_service)
):
    """Get setting by key"""
    setting = await settings_service.get_setting_by_key(key)
    if not setting:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Setting not found")

    if not setting.isPublic and current_user.role != "admin":
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Admin access required")

    return setting


@router.post("", response_model=SettingResponse, status_code=status.HTTP_201_CREATED)
async def create_setting(
    setting_data: SettingCreate,
    current_user: UserInDB = Depends(require_admin),
    settings_service: SettingsService = Depends(get_settings_service)
):
    """Create new setting (admin only)"""
    return await settings_service.create_setting(setting_data, current_user.id)


@router.put("/{key}", response_model=SettingResponse)
async def update_setting(
    key: str,
    setting_update: SettingUpdate,
    current_user: UserInDB = Depends(require_admin),
    settings_service: SettingsService = Depends(get_settings_service)
):
    """Update setting (admin only)"""
    return await settings_service.update_setting(key, setting_update, current_user.id)


@router.delete("/{key}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_setting(
    key: str,
    current_user: UserInDB = Depends(require_admin),
    settings_service: SettingsService = Depends(get_settings_service)
):
    """Delete setting (admin only)"""
    await settings_service.delete_setting(key)
    return None
