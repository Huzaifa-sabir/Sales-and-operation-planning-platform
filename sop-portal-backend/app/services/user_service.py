"""
User Service Layer
Handles all user-related business logic and database operations
"""
from typing import Optional, List, Dict, Any
from datetime import datetime
from bson import ObjectId
from motor.motor_asyncio import AsyncIOMotorDatabase
from fastapi import HTTPException, status

from app.models.user import UserCreate, UserUpdate, UserInDB, UserRole
from app.utils.security import hash_password
import secrets
import string


class UserService:
    """Service class for user management operations"""

    def __init__(self, db: AsyncIOMotorDatabase):
        self.db = db
        self.collection = db.users

    async def create_user(self, user_data: UserCreate) -> tuple[UserInDB, str]:
        """
        Create a new user with generated password
        Returns tuple of (created_user, generated_password)
        """
        # Check if username already exists
        existing_user = await self.collection.find_one({"username": user_data.username})
        if existing_user:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Username already exists"
            )

        # Check if email already exists
        if user_data.email:
            existing_email = await self.collection.find_one({"email": user_data.email})
            if existing_email:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="Email already exists"
                )

        # Use provided password or generate a random one
        if user_data.password:
            # Use the password provided by admin
            password_to_use = user_data.password
            was_generated = False
        else:
            # Generate a random password
            password_to_use = self._generate_password()
            was_generated = True

        # Hash the password
        hashed_password = hash_password(password_to_use)

        # Log for debugging (remove in production)
        import logging
        logger = logging.getLogger(__name__)
        logger.info(f"Creating user: {user_data.username}")
        logger.info(f"Password source: {'provided by admin' if not was_generated else 'auto-generated'}")
        logger.info(f"Password to hash: '{password_to_use}'")
        logger.info(f"Password length: {len(password_to_use)}")
        logger.info(f"Hashed password: {hashed_password[:30]}...")
        logger.info(f"Hashed password length: {len(hashed_password)}")

        # Verify the hash works immediately
        from app.utils.security import verify_password
        test_verify = verify_password(password_to_use, hashed_password)
        logger.info(f"Immediate verification test: {test_verify}")

        # Create user document
        user_doc = {
            "username": user_data.username,
            "email": user_data.email,
            "fullName": user_data.fullName,
            "role": user_data.role,
            "hashedPassword": hashed_password,
            "isActive": True,
            "loginAttempts": 0,
            "createdAt": datetime.utcnow(),
            "updatedAt": datetime.utcnow(),
            "lastLogin": None,
            "passwordResetToken": None,
            "passwordResetExpires": None
        }

        result = await self.collection.insert_one(user_doc)
        user_doc["_id"] = str(result.inserted_id)

        logger.info(f"User created successfully with ID: {user_doc['_id']}")

        return UserInDB(**user_doc), password_to_use

    async def get_user_by_id(self, user_id: str) -> Optional[UserInDB]:
        """Get user by ID"""
        try:
            user_doc = await self.collection.find_one({"_id": ObjectId(user_id)})
            if user_doc:
                user_doc["_id"] = str(user_doc["_id"])
                return UserInDB(**user_doc)
            return None
        except Exception:
            return None

    async def get_user_by_username(self, username: str) -> Optional[UserInDB]:
        """Get user by username"""
        user_doc = await self.collection.find_one({"username": username})
        if user_doc:
            user_doc["_id"] = str(user_doc["_id"])
            return UserInDB(**user_doc)
        return None

    async def update_user(self, user_id: str, user_update: UserUpdate) -> Optional[UserInDB]:
        """Update user information"""
        # Check if user exists
        existing_user = await self.get_user_by_id(user_id)
        if not existing_user:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="User not found"
            )

        # Build update document (only include fields that are set)
        update_data = user_update.model_dump(exclude_unset=True)

        # Check if username is being changed and if it already exists
        if "username" in update_data and update_data["username"] != existing_user.username:
            existing_username = await self.collection.find_one({"username": update_data["username"]})
            if existing_username:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="Username already exists"
                )

        # Check if email is being changed and if it already exists
        if "email" in update_data and update_data["email"] != existing_user.email:
            existing_email = await self.collection.find_one({"email": update_data["email"]})
            if existing_email:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="Email already exists"
                )

        if update_data:
            update_data["updatedAt"] = datetime.utcnow()
            await self.collection.update_one(
                {"_id": ObjectId(user_id)},
                {"$set": update_data}
            )

        return await self.get_user_by_id(user_id)

    async def toggle_user_status(self, user_id: str) -> Optional[UserInDB]:
        """Toggle user active status"""
        user = await self.get_user_by_id(user_id)
        if not user:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="User not found"
            )

        # Prevent deactivating the last admin
        if user.role == UserRole.ADMIN and user.isActive:
            admin_count = await self.collection.count_documents({
                "role": UserRole.ADMIN,
                "isActive": True
            })
            if admin_count <= 1:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="Cannot deactivate the last admin user"
                )

        new_status = not user.isActive
        await self.collection.update_one(
            {"_id": ObjectId(user_id)},
            {"$set": {"isActive": new_status, "updatedAt": datetime.utcnow()}}
        )

        return await self.get_user_by_id(user_id)

    async def delete_user(self, user_id: str) -> bool:
        """Delete a user (soft delete by deactivating)"""
        user = await self.get_user_by_id(user_id)
        if not user:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="User not found"
            )

        # Prevent deleting the last admin
        if user.role == UserRole.ADMIN:
            admin_count = await self.collection.count_documents({
                "role": UserRole.ADMIN,
                "isActive": True
            })
            if admin_count <= 1:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="Cannot delete the last admin user"
                )

        # Soft delete by setting isActive to False
        result = await self.collection.update_one(
            {"_id": ObjectId(user_id)},
            {"$set": {"isActive": False, "updatedAt": datetime.utcnow()}}
        )

        return result.modified_count > 0

    async def list_users(
        self,
        skip: int = 0,
        limit: int = 10,
        role: Optional[str] = None,
        is_active: Optional[bool] = None,
        search: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        List users with pagination and filtering
        Returns dict with users list, total count, and pagination info
        """
        # Build filter query
        query = {}

        if role:
            query["role"] = role

        if is_active is not None:
            query["isActive"] = is_active

        if search:
            # Search in username, email, and fullName
            query["$or"] = [
                {"username": {"$regex": search, "$options": "i"}},
                {"email": {"$regex": search, "$options": "i"}},
                {"fullName": {"$regex": search, "$options": "i"}}
            ]

        # Get total count
        total = await self.collection.count_documents(query)

        # Get paginated users
        cursor = self.collection.find(query).skip(skip).limit(limit).sort("createdAt", -1)
        users = []
        async for user_doc in cursor:
            user_doc["_id"] = str(user_doc["_id"])
            users.append(UserInDB(**user_doc))

        # Calculate pagination info
        total_pages = (total + limit - 1) // limit if limit > 0 else 1
        current_page = (skip // limit) + 1 if limit > 0 else 1

        return {
            "users": users,
            "total": total,
            "page": current_page,
            "pageSize": limit,
            "totalPages": total_pages,
            "hasNext": skip + limit < total,
            "hasPrev": skip > 0
        }

    async def generate_password_reset_token(self, email: str) -> Optional[str]:
        """Generate password reset token for user"""
        user_doc = await self.collection.find_one({"email": email})
        if not user_doc:
            # Don't reveal if email exists for security
            return None

        # Generate secure random token
        reset_token = secrets.token_urlsafe(32)

        # Token expires in 1 hour
        from datetime import timedelta
        expires_at = datetime.utcnow() + timedelta(hours=1)

        # Save token to database
        await self.collection.update_one(
            {"_id": user_doc["_id"]},
            {
                "$set": {
                    "passwordResetToken": reset_token,
                    "passwordResetExpires": expires_at,
                    "updatedAt": datetime.utcnow()
                }
            }
        )

        return reset_token

    async def reset_password_with_token(self, token: str, new_password: str) -> bool:
        """Reset password using reset token"""
        user_doc = await self.collection.find_one({
            "passwordResetToken": token,
            "passwordResetExpires": {"$gt": datetime.utcnow()}
        })

        if not user_doc:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Invalid or expired reset token"
            )

        # Update password and clear reset token
        await self.collection.update_one(
            {"_id": user_doc["_id"]},
            {
                "$set": {
                    "hashedPassword": hash_password(new_password),
                    "passwordResetToken": None,
                    "passwordResetExpires": None,
                    "loginAttempts": 0,  # Reset login attempts
                    "updatedAt": datetime.utcnow()
                }
            }
        )

        return True

    def _generate_password(self, length: int = 12) -> str:
        """Generate a secure random password"""
        # Password must contain: uppercase, lowercase, digits, and special chars
        alphabet = string.ascii_letters + string.digits + "!@#$%^&*"
        password = ''.join(secrets.choice(alphabet) for _ in range(length))

        # Ensure it has at least one of each type
        if not any(c.isupper() for c in password):
            password = secrets.choice(string.ascii_uppercase) + password[1:]
        if not any(c.islower() for c in password):
            password = password[0] + secrets.choice(string.ascii_lowercase) + password[2:]
        if not any(c.isdigit() for c in password):
            password = password[:2] + secrets.choice(string.digits) + password[3:]

        return password
