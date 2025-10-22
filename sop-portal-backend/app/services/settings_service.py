"""
Settings Service
Manages system settings and configurations
"""
from typing import List, Optional, Dict, Any
from motor.motor_asyncio import AsyncIOMotorDatabase
from fastapi import HTTPException, status
from bson import ObjectId
from datetime import datetime

from app.models.settings import (
    SettingCreate,
    SettingUpdate,
    SettingInDB,
    SettingCategory,
    DEFAULT_SETTINGS
)


class SettingsService:
    """Service for managing system settings"""

    def __init__(self, db: AsyncIOMotorDatabase):
        self.db = db
        self.collection = db.settings

    async def initialize_default_settings(self):
        """Initialize default settings if they don't exist"""
        for setting in DEFAULT_SETTINGS:
            existing = await self.collection.find_one({"key": setting["key"]})
            if not existing:
                setting_doc = {
                    **setting,
                    "createdAt": datetime.utcnow(),
                    "updatedAt": datetime.utcnow()
                }
                await self.collection.insert_one(setting_doc)

    async def get_setting_by_key(self, key: str) -> Optional[SettingInDB]:
        """Get setting by key"""
        setting_doc = await self.collection.find_one({"key": key})
        if not setting_doc:
            return None

        setting_doc["_id"] = str(setting_doc["_id"])
        return SettingInDB(**setting_doc)

    async def get_setting_value(self, key: str, default: Any = None) -> Any:
        """Get setting value by key (convenience method)"""
        setting = await self.get_setting_by_key(key)
        return setting.value if setting else default

    async def list_settings(
        self,
        category: Optional[SettingCategory] = None,
        is_public: Optional[bool] = None,
        skip: int = 0,
        limit: int = 100
    ) -> tuple[List[SettingInDB], int]:
        """List settings with filters"""
        query = {}

        if category:
            query["category"] = category

        if is_public is not None:
            query["isPublic"] = is_public

        # Get total count
        total = await self.collection.count_documents(query)

        # Get settings
        cursor = self.collection.find(query).skip(skip).limit(limit).sort("category", 1).sort("key", 1)
        settings_docs = await cursor.to_list(length=limit)

        settings = []
        for doc in settings_docs:
            doc["_id"] = str(doc["_id"])
            settings.append(SettingInDB(**doc))

        return settings, total

    async def create_setting(self, setting_data: SettingCreate, user_id: str) -> SettingInDB:
        """Create new setting"""
        # Check if setting key already exists
        existing = await self.collection.find_one({"key": setting_data.key})
        if existing:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Setting with key '{setting_data.key}' already exists"
            )

        # Create setting document
        setting_doc = {
            **setting_data.model_dump(),
            "createdAt": datetime.utcnow(),
            "updatedAt": datetime.utcnow(),
            "createdBy": user_id,
            "updatedBy": user_id
        }

        result = await self.collection.insert_one(setting_doc)
        setting_doc["_id"] = str(result.inserted_id)

        return SettingInDB(**setting_doc)

    async def update_setting(
        self,
        key: str,
        setting_update: SettingUpdate,
        user_id: str
    ) -> SettingInDB:
        """Update existing setting"""
        # Get existing setting
        setting = await self.get_setting_by_key(key)
        if not setting:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Setting with key '{key}' not found"
            )

        # Check if setting is editable
        if not setting.isEditable:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=f"Setting '{key}' is not editable"
            )

        # Prepare update
        update_data = setting_update.model_dump(exclude_unset=True)
        update_data["updatedAt"] = datetime.utcnow()
        update_data["updatedBy"] = user_id

        # Update in database
        await self.collection.update_one(
            {"key": key},
            {"$set": update_data}
        )

        # Return updated setting
        return await self.get_setting_by_key(key)

    async def delete_setting(self, key: str) -> bool:
        """Delete setting"""
        # Get existing setting
        setting = await self.get_setting_by_key(key)
        if not setting:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Setting with key '{key}' not found"
            )

        # Check if setting is editable (use same permission for deletion)
        if not setting.isEditable:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=f"Setting '{key}' cannot be deleted"
            )

        result = await self.collection.delete_one({"key": key})
        return result.deleted_count > 0

    async def get_public_settings(self) -> Dict[str, Any]:
        """Get all public settings as key-value pairs"""
        settings, _ = await self.list_settings(is_public=True, limit=1000)

        public_settings = {}
        for setting in settings:
            public_settings[setting.key] = setting.value

        return public_settings

    async def get_category_settings(self, category: SettingCategory) -> Dict[str, Any]:
        """Get all settings for a category as key-value pairs"""
        settings, _ = await self.list_settings(category=category, limit=1000)

        category_settings = {}
        for setting in settings:
            category_settings[setting.key] = setting.value

        return category_settings

    async def bulk_update_settings(
        self,
        updates: Dict[str, Any],
        user_id: str
    ) -> List[SettingInDB]:
        """Bulk update multiple settings"""
        updated_settings = []

        for key, value in updates.items():
            try:
                setting_update = SettingUpdate(value=value)
                updated_setting = await self.update_setting(key, setting_update, user_id)
                updated_settings.append(updated_setting)
            except HTTPException:
                # Skip settings that don't exist or aren't editable
                continue

        return updated_settings
