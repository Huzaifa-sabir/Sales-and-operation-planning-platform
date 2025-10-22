"""
S&OP Cycle Service Layer
Handles S&OP cycle management, workflow, and statistics
"""
from typing import Optional, List, Dict, Any
from datetime import datetime
from bson import ObjectId
from motor.motor_asyncio import AsyncIOMotorDatabase
from fastapi import HTTPException, status

from app.models.sop_cycle import SOPCycleCreate, SOPCycleUpdate, SOPCycleInDB, CycleStatus
from app.utils.cycle_helpers import (
    calculate_16_month_period,
    generate_cycle_name,
    calculate_submission_deadline
)


class SOPCycleService:
    """Service class for S&OP cycle management"""

    def __init__(self, db: AsyncIOMotorDatabase):
        self.db = db
        self.collection = db.sop_cycles
        self.forecasts_collection = db.forecasts

    async def create_cycle(self, cycle_data: SOPCycleCreate) -> SOPCycleInDB:
        """
        Create a new S&OP cycle
        Returns created cycle
        """
        # Generate cycle name if not provided
        cycle_name = cycle_data.cycleName or generate_cycle_name(cycle_data.startDate or datetime.now())

        # Calculate 16-month period
        start_date = cycle_data.startDate or datetime.now()
        planning_period = calculate_16_month_period(start_date)

        # Calculate submission deadline
        submission_deadline = calculate_submission_deadline(start_date)

        # Create cycle document
        cycle_doc = {
            "cycleName": cycle_name,
            "cycleYear": start_date.year,
            "cycleMonth": start_date.month,
            "status": CycleStatus.DRAFT,
            "dates": {
                "startDate": start_date,
                "endDate": cycle_data.endDate or (start_date.replace(day=28) if start_date.month != 12 else start_date.replace(month=1, year=start_date.year+1, day=31)),
                "submissionDeadline": submission_deadline
            },
            "planningPeriod": planning_period,
            "stats": {
                "totalForecasts": 0,
                "submittedForecasts": 0,
                "totalSalesReps": 0,
                "submittedSalesReps": 0,
                "completionPercentage": 0.0
            },
            "createdAt": datetime.utcnow(),
            "updatedAt": datetime.utcnow(),
            "createdBy": cycle_data.createdBy if hasattr(cycle_data, 'createdBy') else None,
            "openedAt": None,
            "closedAt": None
        }

        result = await self.collection.insert_one(cycle_doc)
        cycle_doc["_id"] = str(result.inserted_id)

        return SOPCycleInDB(**cycle_doc)

    async def get_cycle_by_id(self, cycle_id: str) -> Optional[SOPCycleInDB]:
        """Get cycle by MongoDB _id"""
        try:
            cycle_doc = await self.collection.find_one({"_id": ObjectId(cycle_id)})
            if cycle_doc:
                cycle_doc["_id"] = str(cycle_doc["_id"])
                return SOPCycleInDB(**cycle_doc)
            return None
        except Exception:
            return None

    async def update_cycle(self, cycle_id: str, cycle_update: SOPCycleUpdate) -> Optional[SOPCycleInDB]:
        """Update cycle information"""
        existing_cycle = await self.get_cycle_by_id(cycle_id)
        if not existing_cycle:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Cycle not found"
            )

        # Build update document
        update_data = cycle_update.model_dump(exclude_unset=True)

        if update_data:
            update_data["updatedAt"] = datetime.utcnow()
            await self.collection.update_one(
                {"_id": ObjectId(cycle_id)},
                {"$set": update_data}
            )

        return await self.get_cycle_by_id(cycle_id)

    async def open_cycle(self, cycle_id: str, opened_by: Optional[str] = None) -> SOPCycleInDB:
        """
        Open a cycle (transition from draft to open)
        Validates that cycle can be opened
        """
        cycle = await self.get_cycle_by_id(cycle_id)
        if not cycle:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Cycle not found"
            )

        # Validate status
        if cycle.status != CycleStatus.DRAFT:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Cannot open cycle in {cycle.status} status. Must be in DRAFT status."
            )

        # Check if there's already an open cycle
        existing_open = await self.collection.find_one({"status": CycleStatus.OPEN})
        if existing_open:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Another cycle is already open: {existing_open.get('cycleName')}"
            )

        # Update cycle status to OPEN
        update_data = {
            "status": CycleStatus.OPEN,
            "openedAt": datetime.utcnow(),
            "updatedAt": datetime.utcnow()
        }

        await self.collection.update_one(
            {"_id": ObjectId(cycle_id)},
            {"$set": update_data}
        )

        # TODO: Send notifications to sales reps that cycle is open

        return await self.get_cycle_by_id(cycle_id)

    async def close_cycle(self, cycle_id: str, closed_by: Optional[str] = None) -> SOPCycleInDB:
        """
        Close a cycle (transition from open to closed)
        Validates that cycle can be closed
        """
        cycle = await self.get_cycle_by_id(cycle_id)
        if not cycle:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Cycle not found"
            )

        # Validate status
        if cycle.status != CycleStatus.OPEN:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Cannot close cycle in {cycle.status} status. Must be in OPEN status."
            )

        # Update cycle statistics before closing
        await self.update_cycle_statistics(cycle_id)

        # Update cycle status to CLOSED
        update_data = {
            "status": CycleStatus.CLOSED,
            "closedAt": datetime.utcnow(),
            "updatedAt": datetime.utcnow()
        }

        await self.collection.update_one(
            {"_id": ObjectId(cycle_id)},
            {"$set": update_data}
        )

        # TODO: Send notifications to admins that cycle is closed

        return await self.get_cycle_by_id(cycle_id)

    async def update_cycle_statistics(self, cycle_id: str) -> Dict[str, Any]:
        """
        Update cycle statistics (submission counts, completion percentage)
        """
        # Count forecasts for this cycle
        total_forecasts = await self.forecasts_collection.count_documents({"cycleId": cycle_id})

        # Count submitted forecasts
        submitted_forecasts = await self.forecasts_collection.count_documents({
            "cycleId": cycle_id,
            "status": "submitted"
        })

        # Count unique sales reps who should submit
        # (This would typically come from a user assignment table)
        total_sales_reps_pipeline = [
            {"$match": {"cycleId": cycle_id}},
            {"$group": {"_id": "$salesRepId"}},
            {"$count": "total"}
        ]
        total_reps_result = await self.forecasts_collection.aggregate(total_sales_reps_pipeline).to_list(length=1)
        total_sales_reps = total_reps_result[0]["total"] if total_reps_result else 0

        # Count unique sales reps who have submitted
        submitted_reps_pipeline = [
            {"$match": {"cycleId": cycle_id, "status": "submitted"}},
            {"$group": {"_id": "$salesRepId"}},
            {"$count": "total"}
        ]
        submitted_reps_result = await self.forecasts_collection.aggregate(submitted_reps_pipeline).to_list(length=1)
        submitted_sales_reps = submitted_reps_result[0]["total"] if submitted_reps_result else 0

        # Calculate completion percentage
        completion_percentage = (submitted_forecasts / total_forecasts * 100) if total_forecasts > 0 else 0.0

        # Update cycle statistics
        stats = {
            "totalForecasts": total_forecasts,
            "submittedForecasts": submitted_forecasts,
            "totalSalesReps": total_sales_reps,
            "submittedSalesReps": submitted_sales_reps,
            "completionPercentage": round(completion_percentage, 2)
        }

        await self.collection.update_one(
            {"_id": ObjectId(cycle_id)},
            {"$set": {"stats": stats, "updatedAt": datetime.utcnow()}}
        )

        return stats

    async def list_cycles(
        self,
        skip: int = 0,
        limit: int = 10,
        status: Optional[str] = None,
        year: Optional[int] = None
    ) -> Dict[str, Any]:
        """
        List cycles with filtering and pagination
        """
        query = {}

        if status:
            query["status"] = status

        if year:
            query["cycleYear"] = year

        # Get total count
        total = await self.collection.count_documents(query)

        # Get paginated cycles
        cursor = self.collection.find(query).skip(skip).limit(limit).sort("createdAt", -1)
        cycles = []
        async for cycle_doc in cursor:
            cycle_doc["_id"] = str(cycle_doc["_id"])
            cycles.append(SOPCycleInDB(**cycle_doc))

        # Calculate pagination info
        total_pages = (total + limit - 1) // limit if limit > 0 else 1
        current_page = (skip // limit) + 1 if limit > 0 else 1

        return {
            "cycles": cycles,
            "total": total,
            "page": current_page,
            "pageSize": limit,
            "totalPages": total_pages,
            "hasNext": skip + limit < total,
            "hasPrev": skip > 0
        }

    async def get_current_open_cycle(self) -> Optional[SOPCycleInDB]:
        """
        Get the currently open cycle (if any)
        """
        cycle_doc = await self.collection.find_one({"status": CycleStatus.OPEN})
        if cycle_doc:
            cycle_doc["_id"] = str(cycle_doc["_id"])
            return SOPCycleInDB(**cycle_doc)
        return None

    async def delete_cycle(self, cycle_id: str) -> bool:
        """
        Delete a cycle (only if in DRAFT status)
        """
        cycle = await self.get_cycle_by_id(cycle_id)
        if not cycle:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Cycle not found"
            )

        # Only allow deletion of draft cycles
        if cycle.status != CycleStatus.DRAFT:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Cannot delete cycle in {cycle.status} status. Only DRAFT cycles can be deleted."
            )

        result = await self.collection.delete_one({"_id": ObjectId(cycle_id)})
        return result.deleted_count > 0
