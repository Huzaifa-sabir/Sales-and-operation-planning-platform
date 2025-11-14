"""
Product Service Layer
Handles all product-related business logic and database operations
"""
from typing import Optional, List, Dict, Any
from datetime import datetime
from bson import ObjectId
from motor.motor_asyncio import AsyncIOMotorDatabase
from fastapi import HTTPException, status

from app.models.product import ProductCreate, ProductUpdate, ProductInDB


class ProductService:
    """Service class for product management operations"""

    def __init__(self, db: AsyncIOMotorDatabase):
        self.db = db
        self.collection = db.products
        self.matrix_collection = db.product_customer_matrix

    async def create_product(self, product_data: ProductCreate) -> ProductInDB:
        """
        Create a new product
        Returns created product
        """
        # Check if itemCode already exists
        existing_product = await self.collection.find_one({"itemCode": product_data.itemCode})
        if existing_product:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Item code '{product_data.itemCode}' already exists"
            )

        # Create product document
        # Ensure pricing has required fields
        pricing_data = None
        if product_data.pricing:
            pricing_data = product_data.pricing.model_dump()
            if "avgPrice" not in pricing_data or pricing_data.get("avgPrice") is None:
                pricing_data["avgPrice"] = 0.0
            if "currency" not in pricing_data:
                pricing_data["currency"] = "USD"
        
        product_doc = {
            "itemCode": product_data.itemCode,
            "itemDescription": product_data.itemDescription,
            "group": product_data.group.model_dump() if product_data.group else None,
            "manufacturing": product_data.manufacturing.model_dump() if product_data.manufacturing else None,
            "pricing": pricing_data,
            "weight": product_data.weight,
            "uom": product_data.uom,
            "isActive": True,
            "createdAt": datetime.utcnow(),
            "updatedAt": datetime.utcnow(),
            "metadata": product_data.metadata or {}
        }

        result = await self.collection.insert_one(product_doc)
        product_doc["_id"] = str(result.inserted_id)

        return ProductInDB(**product_doc)

    async def get_product_by_id(self, product_id: str) -> Optional[ProductInDB]:
        """Get product by MongoDB _id"""
        try:
            product_doc = await self.collection.find_one({"_id": ObjectId(product_id)})
            if product_doc:
                product_doc["_id"] = str(product_doc["_id"])
                # Handle field name migration
                if "description" in product_doc and "itemDescription" not in product_doc:
                    product_doc["itemDescription"] = product_doc["description"]
                # Ensure pricing has required fields
                if product_doc.get("pricing"):
                    if "avgPrice" not in product_doc["pricing"] or product_doc["pricing"].get("avgPrice") is None:
                        product_doc["pricing"]["avgPrice"] = 0.0
                    if "currency" not in product_doc["pricing"]:
                        product_doc["pricing"]["currency"] = "USD"
                return ProductInDB(**product_doc)
            return None
        except Exception:
            return None

    async def get_product_by_item_code(self, item_code: str) -> Optional[ProductInDB]:
        """Get product by itemCode (business ID like '110001')"""
        product_doc = await self.collection.find_one({"itemCode": item_code})
        if product_doc:
            product_doc["_id"] = str(product_doc["_id"])
            # Handle field name migration
            if "description" in product_doc and "itemDescription" not in product_doc:
                product_doc["itemDescription"] = product_doc["description"]
            # Ensure pricing has required fields
            if product_doc.get("pricing"):
                if "avgPrice" not in product_doc["pricing"] or product_doc["pricing"].get("avgPrice") is None:
                    product_doc["pricing"]["avgPrice"] = 0.0
                if "currency" not in product_doc["pricing"]:
                    product_doc["pricing"]["currency"] = "USD"
            return ProductInDB(**product_doc)
        return None

    async def update_product(self, product_id: str, product_update: ProductUpdate) -> Optional[ProductInDB]:
        """Update product information"""
        # Check if product exists
        existing_product = await self.get_product_by_id(product_id)
        if not existing_product:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Product not found"
            )

        # Build update document
        update_data = product_update.model_dump(exclude_unset=True)

        # Check if itemCode is being changed and if it already exists
        if "itemCode" in update_data and update_data["itemCode"] != existing_product.itemCode:
            existing_item = await self.collection.find_one({"itemCode": update_data["itemCode"]})
            if existing_item:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail=f"Item code '{update_data['itemCode']}' already exists"
                )

        # Convert nested objects to dicts if present
        for field in ["group", "manufacturing", "pricing"]:
            if field in update_data and update_data[field]:
                update_data[field] = update_data[field].model_dump()
                # Ensure pricing has required fields
                if field == "pricing" and update_data[field]:
                    if "avgPrice" not in update_data[field] or update_data[field].get("avgPrice") is None:
                        update_data[field]["avgPrice"] = 0.0
                    if "currency" not in update_data[field]:
                        update_data[field]["currency"] = "USD"

        if update_data:
            update_data["updatedAt"] = datetime.utcnow()
            await self.collection.update_one(
                {"_id": ObjectId(product_id)},
                {"$set": update_data}
            )

        return await self.get_product_by_id(product_id)

    async def toggle_product_status(self, product_id: str) -> Optional[ProductInDB]:
        """Toggle product active status (soft delete)"""
        product = await self.get_product_by_id(product_id)
        if not product:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Product not found"
            )

        new_status = not product.isActive
        await self.collection.update_one(
            {"_id": ObjectId(product_id)},
            {"$set": {"isActive": new_status, "updatedAt": datetime.utcnow()}}
        )

        return await self.get_product_by_id(product_id)

    async def delete_product(self, product_id: str) -> bool:
        """Soft delete a product by setting isActive to False"""
        product = await self.get_product_by_id(product_id)
        if not product:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Product not found"
            )

        # Soft delete
        result = await self.collection.update_one(
            {"_id": ObjectId(product_id)},
            {"$set": {"isActive": False, "updatedAt": datetime.utcnow()}}
        )

        return result.modified_count > 0

    async def list_products(
        self,
        skip: int = 0,
        limit: int = 10,
        is_active: Optional[bool] = None,
        search: Optional[str] = None,
        customer_id: Optional[str] = None,
        group_code: Optional[str] = None,
        location: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        List products with pagination and filtering
        If customer_id is provided, only return products available for that customer

        Returns dict with products list, total count, and pagination info
        """
        # Build filter query
        query = {}

        if is_active is not None:
            query["isActive"] = is_active

        # Group code filter
        if group_code:
            query["group.code"] = group_code

        # Manufacturing location filter
        if location:
            query["manufacturing.location"] = location

        # Customer-specific filtering
        if customer_id:
            # Get products available for this customer from matrix
            matrix_docs = await self.matrix_collection.find(
                {"customerId": customer_id, "isActive": True}
            ).to_list(length=None)

            product_ids = [doc["productId"] for doc in matrix_docs]

            # Debug: Log the filtering
            import logging
            logger = logging.getLogger(__name__)
            logger.debug(f"Filtering products for customer_id={customer_id}, found {len(product_ids)} products in matrix: {product_ids[:10]}")

            if product_ids:
                # Filter products to only those in the matrix
                query["itemCode"] = {"$in": product_ids}
            else:
                # No products available for this customer
                logger.debug(f"No active products found in matrix for customer_id={customer_id}")
                return {
                    "products": [],
                    "total": 0,
                    "page": 1,
                    "pageSize": limit,
                    "totalPages": 0,
                    "hasNext": False,
                    "hasPrev": False
                }

        if search:
            # Search in itemCode, itemDescription
            # If customer_id is set, we need to combine search with the existing itemCode filter
            if customer_id and "itemCode" in query:
                # Customer filter already applied, add search to filter within those products
                search_query = {
                    "$or": [
                        {"itemCode": {"$regex": search, "$options": "i"}},
                        {"itemDescription": {"$regex": search, "$options": "i"}}
                    ]
                }
                # Combine with existing query using $and
                query = {"$and": [query, search_query]}
            else:
                # No customer filter, just add search
                query["$or"] = [
                    {"itemCode": {"$regex": search, "$options": "i"}},
                    {"itemDescription": {"$regex": search, "$options": "i"}}
                ]

        # Get total count
        total = await self.collection.count_documents(query)

        # Get paginated products
        cursor = self.collection.find(query).skip(skip).limit(limit).sort("itemCode", 1)
        products = []
        async for product_doc in cursor:
            product_doc["_id"] = str(product_doc["_id"])

            # Handle field name migration: 'description' -> 'itemDescription'
            if "description" in product_doc and "itemDescription" not in product_doc:
                product_doc["itemDescription"] = product_doc["description"]

            # If customer_id is provided, get customer-specific pricing
            if customer_id:
                matrix_doc = await self.matrix_collection.find_one({
                    "customerId": customer_id,
                    "productId": product_doc["itemCode"]
                })
                if matrix_doc and matrix_doc.get("customerPrice"):
                    # Add customer-specific pricing to product
                    if not product_doc.get("pricing"):
                        product_doc["pricing"] = {}
                    # Ensure avgPrice exists (required field)
                    if "avgPrice" not in product_doc["pricing"] or product_doc["pricing"].get("avgPrice") is None:
                        product_doc["pricing"]["avgPrice"] = 0.0
                    if "currency" not in product_doc["pricing"]:
                        product_doc["pricing"]["currency"] = "USD"
                    product_doc["pricing"]["customerSpecificPrice"] = matrix_doc["customerPrice"]
            
            # Ensure pricing has required fields before creating ProductInDB
            if product_doc.get("pricing"):
                if "avgPrice" not in product_doc["pricing"] or product_doc["pricing"].get("avgPrice") is None:
                    product_doc["pricing"]["avgPrice"] = 0.0
                if "currency" not in product_doc["pricing"]:
                    product_doc["pricing"]["currency"] = "USD"

            products.append(ProductInDB(**product_doc))

        # Calculate pagination info
        total_pages = (total + limit - 1) // limit if limit > 0 else 1
        current_page = (skip // limit) + 1 if limit > 0 else 1

        return {
            "products": products,
            "total": total,
            "page": current_page,
            "pageSize": limit,
            "totalPages": total_pages,
            "hasNext": skip + limit < total,
            "hasPrev": skip > 0
        }

    async def get_active_products(self, customer_id: Optional[str] = None) -> List[ProductInDB]:
        """
        Get all active products (for dropdowns, etc.)
        If customer_id is provided, only return products available for that customer
        """
        query = {"isActive": True}

        # Customer-specific filtering
        if customer_id:
            matrix_docs = await self.matrix_collection.find(
                {"customerId": customer_id, "isActive": True}
            ).to_list(length=None)

            product_ids = [doc["productId"] for doc in matrix_docs]

            if product_ids:
                query["itemCode"] = {"$in": product_ids}
            else:
                return []

        cursor = self.collection.find(query).sort("itemCode", 1)
        products = []
        async for product_doc in cursor:
            product_doc["_id"] = str(product_doc["_id"])

            # Handle field name migration
            if "description" in product_doc and "itemDescription" not in product_doc:
                product_doc["itemDescription"] = product_doc["description"]

            # Get customer-specific pricing if customer_id provided
            if customer_id:
                matrix_doc = await self.matrix_collection.find_one({
                    "customerId": customer_id,
                    "productId": product_doc["itemCode"]
                })
                if matrix_doc and matrix_doc.get("customerPrice"):
                    if not product_doc.get("pricing"):
                        product_doc["pricing"] = {}
                    # Ensure avgPrice exists (required field)
                    if "avgPrice" not in product_doc["pricing"] or product_doc["pricing"].get("avgPrice") is None:
                        product_doc["pricing"]["avgPrice"] = 0.0
                    if "currency" not in product_doc["pricing"]:
                        product_doc["pricing"]["currency"] = "USD"
                    product_doc["pricing"]["customerSpecificPrice"] = matrix_doc["customerPrice"]
            
            # Ensure pricing has required fields before creating ProductInDB
            if product_doc.get("pricing"):
                if "avgPrice" not in product_doc["pricing"] or product_doc["pricing"].get("avgPrice") is None:
                    product_doc["pricing"]["avgPrice"] = 0.0
                if "currency" not in product_doc["pricing"]:
                    product_doc["pricing"]["currency"] = "USD"

            products.append(ProductInDB(**product_doc))

        return products
