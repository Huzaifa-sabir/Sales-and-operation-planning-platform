"""
Product-Customer Matrix Service Layer
Manages which products are available for which customers with customer-specific pricing
"""
from typing import Optional, List, Dict, Any
from datetime import datetime
from bson import ObjectId
from motor.motor_asyncio import AsyncIOMotorDatabase
from fastapi import HTTPException, status

from app.models.product_customer_matrix import (
    ProductCustomerMatrixCreate,
    ProductCustomerMatrixUpdate,
    ProductCustomerMatrixInDB
)


class MatrixService:
    """Service class for product-customer matrix management"""

    def __init__(self, db: AsyncIOMotorDatabase):
        self.db = db
        self.collection = db.product_customer_matrix
        self.customers_collection = db.customers
        self.products_collection = db.products

    async def create_matrix_entry(self, matrix_data: ProductCustomerMatrixCreate) -> ProductCustomerMatrixInDB:
        """
        Create a new product-customer matrix entry
        Returns created matrix entry
        """
        # Verify customer exists
        customer = await self.customers_collection.find_one({"customerId": matrix_data.customerId})
        if not customer:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Customer '{matrix_data.customerId}' not found"
            )

        # Verify product exists
        product = await self.products_collection.find_one({"itemCode": matrix_data.productId})
        if not product:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Product '{matrix_data.productId}' not found"
            )

        # Check if entry already exists
        existing = await self.collection.find_one({
            "customerId": matrix_data.customerId,
            "productId": matrix_data.productId
        })
        if existing:
            # Update existing entry instead of raising error
            update_data = {
                "customerName": matrix_data.customerName,
                "productCode": matrix_data.productCode,
                "productDescription": matrix_data.productDescription,
                "isActive": matrix_data.isActive if matrix_data.isActive is not None else True,
                "customerSpecificPrice": matrix_data.customerSpecificPrice,
                "lastOrderDate": matrix_data.lastOrderDate,
                "totalOrdersQty": matrix_data.totalOrdersQty,
                "notes": matrix_data.notes,
                "updatedAt": datetime.utcnow()
            }
            await self.collection.update_one(
                {"customerId": matrix_data.customerId, "productId": matrix_data.productId},
                {"$set": update_data}
            )
            existing.update(update_data)
            existing["_id"] = str(existing["_id"])
            return ProductCustomerMatrixInDB(**existing)

        # Create matrix document
        matrix_doc = {
            "customerId": matrix_data.customerId,
            "customerName": matrix_data.customerName,
            "productId": matrix_data.productId,
            "productCode": matrix_data.productCode,
            "productDescription": matrix_data.productDescription,
            "isActive": matrix_data.isActive if matrix_data.isActive is not None else True,
            "customerSpecificPrice": matrix_data.customerSpecificPrice,
            "lastOrderDate": matrix_data.lastOrderDate,
            "totalOrdersQty": matrix_data.totalOrdersQty,
            "notes": matrix_data.notes,
            "createdAt": datetime.utcnow(),
            "updatedAt": datetime.utcnow()
        }

        result = await self.collection.insert_one(matrix_doc)
        matrix_doc["_id"] = str(result.inserted_id)

        return ProductCustomerMatrixInDB(**matrix_doc)

    async def get_matrix_entry_by_id(self, matrix_id: str) -> Optional[ProductCustomerMatrixInDB]:
        """Get matrix entry by MongoDB _id"""
        try:
            matrix_doc = await self.collection.find_one({"_id": ObjectId(matrix_id)})
            if matrix_doc:
                matrix_doc["_id"] = str(matrix_doc["_id"])
                return ProductCustomerMatrixInDB(**matrix_doc)
            return None
        except Exception:
            return None

    async def get_matrix_entry(self, customer_id: str, product_id: str) -> Optional[ProductCustomerMatrixInDB]:
        """Get matrix entry by customer and product IDs"""
        matrix_doc = await self.collection.find_one({
            "customerId": customer_id,
            "productId": product_id
        })
        if matrix_doc:
            matrix_doc["_id"] = str(matrix_doc["_id"])
            return ProductCustomerMatrixInDB(**matrix_doc)
        return None

    async def update_matrix_entry(self, matrix_id: str, matrix_update: ProductCustomerMatrixUpdate) -> Optional[ProductCustomerMatrixInDB]:
        """Update matrix entry"""
        # Check if matrix entry exists
        existing = await self.get_matrix_entry_by_id(matrix_id)
        if not existing:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Matrix entry not found"
            )

        # Build update document
        update_data = matrix_update.model_dump(exclude_unset=True)

        if update_data:
            update_data["updatedAt"] = datetime.utcnow()
            await self.collection.update_one(
                {"_id": ObjectId(matrix_id)},
                {"$set": update_data}
            )

        return await self.get_matrix_entry_by_id(matrix_id)

    async def toggle_matrix_status(self, matrix_id: str) -> Optional[ProductCustomerMatrixInDB]:
        """Toggle matrix entry active status"""
        matrix_entry = await self.get_matrix_entry_by_id(matrix_id)
        if not matrix_entry:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Matrix entry not found"
            )

        new_status = not matrix_entry.isActive
        await self.collection.update_one(
            {"_id": ObjectId(matrix_id)},
            {"$set": {"isActive": new_status, "updatedAt": datetime.utcnow()}}
        )

        return await self.get_matrix_entry_by_id(matrix_id)

    async def delete_matrix_entry(self, matrix_id: str) -> bool:
        """Delete matrix entry (hard delete for this collection)"""
        matrix_entry = await self.get_matrix_entry_by_id(matrix_id)
        if not matrix_entry:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Matrix entry not found"
            )

        result = await self.collection.delete_one({"_id": ObjectId(matrix_id)})
        return result.deleted_count > 0

    async def list_matrix_entries(
        self,
        skip: int = 0,
        limit: int = 10,
        customer_id: Optional[str] = None,
        product_id: Optional[str] = None,
        is_active: Optional[bool] = None
    ) -> Dict[str, Any]:
        """
        List matrix entries with pagination and filtering
        Returns dict with entries list, total count, and pagination info
        """
        # Build filter query
        query = {}

        if customer_id:
            query["customerId"] = customer_id

        if product_id:
            query["productId"] = product_id

        if is_active is not None:
            query["isActive"] = is_active

        # Get total count
        total = await self.collection.count_documents(query)

        # Get paginated entries
        cursor = self.collection.find(query).skip(skip).limit(limit).sort([("customerId", 1), ("productId", 1)])
        entries = []
        async for matrix_doc in cursor:
            matrix_doc["_id"] = str(matrix_doc["_id"])
            entries.append(ProductCustomerMatrixInDB(**matrix_doc))

        # Calculate pagination info
        total_pages = (total + limit - 1) // limit if limit > 0 else 1
        current_page = (skip // limit) + 1 if limit > 0 else 1

        return {
            "entries": entries,
            "total": total,
            "page": current_page,
            "pageSize": limit,
            "totalPages": total_pages,
            "hasNext": skip + limit < total,
            "hasPrev": skip > 0
        }

    async def get_products_for_customer(self, customer_id: str) -> List[str]:
        """Get list of product IDs available for a customer"""
        cursor = self.collection.find({"customerId": customer_id, "isActive": True})
        product_ids = []
        async for doc in cursor:
            product_ids.append(doc["productId"])
        return product_ids

    async def get_customers_for_product(self, product_id: str) -> List[str]:
        """Get list of customer IDs that can order a product"""
        cursor = self.collection.find({"productId": product_id, "isActive": True})
        customer_ids = []
        async for doc in cursor:
            customer_ids.append(doc["customerId"])
        return customer_ids

    async def bulk_create_matrix_entries(self, entries: List[ProductCustomerMatrixCreate]) -> Dict[str, Any]:
        """
        Bulk create matrix entries
        Returns summary of created/failed entries
        """
        created = []
        failed = []

        for entry_data in entries:
            try:
                created_entry = await self.create_matrix_entry(entry_data)
                created.append(created_entry)
            except HTTPException as e:
                failed.append({
                    "customerId": entry_data.customerId,
                    "productId": entry_data.productId,
                    "error": e.detail
                })

        return {
            "created": created,
            "failed": failed,
            "totalCreated": len(created),
            "totalFailed": len(failed)
        }
