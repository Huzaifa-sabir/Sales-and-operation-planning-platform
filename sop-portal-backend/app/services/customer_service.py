"""
Customer Service Layer
Handles all customer-related business logic and database operations
"""
from typing import Optional, List, Dict, Any
from datetime import datetime
from bson import ObjectId
from motor.motor_asyncio import AsyncIOMotorDatabase
from fastapi import HTTPException, status

from app.models.customer import CustomerCreate, CustomerUpdate, CustomerInDB


class CustomerService:
    """Service class for customer management operations"""

    def __init__(self, db: AsyncIOMotorDatabase):
        self.db = db
        self.collection = db.customers

    async def create_customer(self, customer_data: CustomerCreate) -> CustomerInDB:
        """
        Create a new customer
        Returns created customer
        """
        # Check if customerId already exists
        existing_customer = await self.collection.find_one({"customerId": customer_data.customerId})
        if existing_customer:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Customer ID '{customer_data.customerId}' already exists"
            )

        # Create customer document
        customer_doc = {
            "customerId": customer_data.customerId,
            "customerName": customer_data.customerName,
            "sopCustomerName": getattr(customer_data, 'sopCustomerName', None),
            "salesRepId": customer_data.salesRepId,
            "salesRepName": customer_data.salesRepName,
            "location": customer_data.location.model_dump() if customer_data.location else None,
            "contactPerson": customer_data.contactPerson,
            "contactEmail": customer_data.contactEmail,
            "contactPhone": customer_data.contactPhone,
            "paymentTerms": getattr(customer_data, 'paymentTerms', None),
            "creditLimit": getattr(customer_data, 'creditLimit', None),
            "isActive": True,
            "createdAt": datetime.utcnow(),
            "updatedAt": datetime.utcnow(),
            "metadata": customer_data.metadata or {}
        }

        result = await self.collection.insert_one(customer_doc)
        customer_doc["_id"] = str(result.inserted_id)

        return CustomerInDB(**customer_doc)

    async def get_customer_by_id(self, customer_id: str) -> Optional[CustomerInDB]:
        """Get customer by MongoDB _id"""
        try:
            customer_doc = await self.collection.find_one({"_id": ObjectId(customer_id)})
            if customer_doc:
                customer_doc["_id"] = str(customer_doc["_id"])
                return CustomerInDB(**customer_doc)
            return None
        except Exception:
            return None

    async def get_customer_by_customer_id(self, customer_id: str) -> Optional[CustomerInDB]:
        """Get customer by customerId (business ID like 'PATITO-000001')"""
        customer_doc = await self.collection.find_one({"customerId": customer_id})
        if customer_doc:
            customer_doc["_id"] = str(customer_doc["_id"])
            return CustomerInDB(**customer_doc)
        return None

    async def update_customer(self, customer_id: str, customer_update: CustomerUpdate) -> Optional[CustomerInDB]:
        """Update customer information"""
        # Check if customer exists
        existing_customer = await self.get_customer_by_id(customer_id)
        if not existing_customer:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Customer not found"
            )

        # Build update document
        update_data = customer_update.model_dump(exclude_unset=True)

        # Check if customerId is being changed and if it already exists
        if "customerId" in update_data and update_data["customerId"] != existing_customer.customerId:
            existing_cust_id = await self.collection.find_one({"customerId": update_data["customerId"]})
            if existing_cust_id:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail=f"Customer ID '{update_data['customerId']}' already exists"
                )

        # Convert location to dict if present
        if "location" in update_data and update_data["location"]:
            update_data["location"] = update_data["location"].model_dump()

        if update_data:
            update_data["updatedAt"] = datetime.utcnow()
            await self.collection.update_one(
                {"_id": ObjectId(customer_id)},
                {"$set": update_data}
            )

        return await self.get_customer_by_id(customer_id)

    async def toggle_customer_status(self, customer_id: str) -> Optional[CustomerInDB]:
        """Toggle customer active status (soft delete)"""
        customer = await self.get_customer_by_id(customer_id)
        if not customer:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Customer not found"
            )

        new_status = not customer.isActive
        await self.collection.update_one(
            {"_id": ObjectId(customer_id)},
            {"$set": {"isActive": new_status, "updatedAt": datetime.utcnow()}}
        )

        return await self.get_customer_by_id(customer_id)

    async def delete_customer(self, customer_id: str) -> bool:
        """Soft delete a customer by setting isActive to False"""
        customer = await self.get_customer_by_id(customer_id)
        if not customer:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Customer not found"
            )

        # Soft delete
        result = await self.collection.update_one(
            {"_id": ObjectId(customer_id)},
            {"$set": {"isActive": False, "updatedAt": datetime.utcnow()}}
        )

        return result.modified_count > 0

    async def list_customers(
        self,
        skip: int = 0,
        limit: int = 10,
        is_active: Optional[bool] = None,
        search: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        List customers with pagination and filtering
        Returns dict with customers list, total count, and pagination info
        """
        # Build filter query
        query = {}

        if is_active is not None:
            query["isActive"] = is_active

        if search:
            # Search in customerId, customerName, contactPerson, contactEmail
            query["$or"] = [
                {"customerId": {"$regex": search, "$options": "i"}},
                {"customerName": {"$regex": search, "$options": "i"}},
                {"contactPerson": {"$regex": search, "$options": "i"}},
                {"contactEmail": {"$regex": search, "$options": "i"}}
            ]

        # Get total count
        total = await self.collection.count_documents(query)

        # Get paginated customers
        cursor = self.collection.find(query).skip(skip).limit(limit).sort("customerName", 1)
        customers = []
        async for customer_doc in cursor:
            customer_doc["_id"] = str(customer_doc["_id"])
            customers.append(CustomerInDB(**customer_doc))

        # Calculate pagination info
        total_pages = (total + limit - 1) // limit if limit > 0 else 1
        current_page = (skip // limit) + 1 if limit > 0 else 1

        return {
            "customers": customers,
            "total": total,
            "page": current_page,
            "pageSize": limit,
            "totalPages": total_pages,
            "hasNext": skip + limit < total,
            "hasPrev": skip > 0
        }

    async def get_active_customers(self) -> List[CustomerInDB]:
        """Get all active customers (for dropdowns, etc.)"""
        cursor = self.collection.find({"isActive": True}).sort("customerName", 1)
        customers = []
        async for customer_doc in cursor:
            customer_doc["_id"] = str(customer_doc["_id"])
            customers.append(CustomerInDB(**customer_doc))
        return customers
