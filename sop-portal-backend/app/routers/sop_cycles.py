"""
S&OP Cycle Management Router
Handles S&OP cycle CRUD, workflow actions, and statistics
"""
from typing import Optional
from fastapi import APIRouter, Depends, HTTPException, status, Query
from motor.motor_asyncio import AsyncIOMotorDatabase

from app.config.database import get_db
from app.models.sop_cycle import SOPCycleCreate, SOPCycleUpdate, SOPCycleResponse
from app.schemas.sop_cycle_schemas import (
    CycleCreateRequest,
    CycleUpdateRequest,
    CycleListResponse,
    CycleActionResponse,
    MessageResponse
)
from app.services.sop_cycle_service import SOPCycleService
from app.utils.auth_dependencies import require_admin, get_current_active_user
from app.models.user import UserInDB

router = APIRouter(prefix="/sop/cycles", tags=["S&OP Cycle Management"])


@router.post(
    "",
    response_model=SOPCycleResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Create a new S&OP cycle",
    description="Create a new S&OP cycle with automatic 16-month planning period. Admin only."
)
async def create_cycle(
    cycle_data: CycleCreateRequest,
    db: AsyncIOMotorDatabase = Depends(get_db),
    current_user: UserInDB = Depends(require_admin)
):
    """
    Create a new S&OP cycle (Admin only)

    - **cycleName**: Optional cycle name (auto-generated if not provided)
    - **startDate**: Optional start date (defaults to current date)
    - **endDate**: Optional end date (defaults to end of month)

    The system automatically:
    - Generates 16-month planning period (4 historical + 1 current + 11 forecast)
    - Calculates submission deadline
    - Sets status to DRAFT
    """
    cycle_service = SOPCycleService(db)

    # Convert request to SOPCycleCreate model
    cycle_create = SOPCycleCreate(
        cycleName=cycle_data.cycleName,
        startDate=cycle_data.startDate,
        endDate=cycle_data.endDate,
        createdBy=current_user.id
    )

    created_cycle = await cycle_service.create_cycle(cycle_create)

    return created_cycle


@router.get(
    "",
    response_model=CycleListResponse,
    summary="List all S&OP cycles",
    description="Get paginated list of S&OP cycles with filtering"
)
async def list_cycles(
    page: int = Query(default=1, ge=1, description="Page number"),
    pageSize: int = Query(default=10, ge=1, le=100, description="Items per page"),
    status: Optional[str] = Query(None, description="Filter by status (draft/open/closed)"),
    year: Optional[int] = Query(None, description="Filter by year"),
    db: AsyncIOMotorDatabase = Depends(get_db),
    current_user: UserInDB = Depends(get_current_active_user)
):
    """
    List S&OP cycles with pagination and filtering

    - **page**: Page number (default: 1)
    - **pageSize**: Items per page (default: 10, max: 100)
    - **status**: Filter by status (draft, open, closed)
    - **year**: Filter by cycle year
    """
    cycle_service = SOPCycleService(db)

    skip = (page - 1) * pageSize

    result = await cycle_service.list_cycles(
        skip=skip,
        limit=pageSize,
        status=status,
        year=year
    )

    return CycleListResponse(
        cycles=result["cycles"],
        total=result["total"],
        page=result["page"],
        pageSize=result["pageSize"],
        totalPages=result["totalPages"],
        hasNext=result["hasNext"],
        hasPrev=result["hasPrev"]
    )


@router.get(
    "/active",
    response_model=SOPCycleResponse,
    summary="Get current open cycle",
    description="Get the currently open S&OP cycle (if any)"
)
async def get_active_cycle(
    db: AsyncIOMotorDatabase = Depends(get_db),
    current_user: UserInDB = Depends(get_current_active_user)
):
    """
    Get the currently active/open cycle

    Returns the cycle that is currently in OPEN status.
    Used by sales reps to submit forecasts.
    """
    cycle_service = SOPCycleService(db)

    current_cycle = await cycle_service.get_current_open_cycle()

    if not current_cycle:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="No open cycle found. Please contact administrator."
        )

    return current_cycle


@router.get(
    "/{cycle_id}",
    response_model=SOPCycleResponse,
    summary="Get cycle by ID",
    description="Get a specific S&OP cycle by ID"
)
async def get_cycle(
    cycle_id: str,
    db: AsyncIOMotorDatabase = Depends(get_db),
    current_user: UserInDB = Depends(get_current_active_user)
):
    """Get S&OP cycle by ID"""
    cycle_service = SOPCycleService(db)

    cycle = await cycle_service.get_cycle_by_id(cycle_id)

    if not cycle:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Cycle not found"
        )

    return cycle


@router.put(
    "/{cycle_id}",
    response_model=SOPCycleResponse,
    summary="Update cycle",
    description="Update S&OP cycle information. Admin only."
)
async def update_cycle(
    cycle_id: str,
    cycle_update: CycleUpdateRequest,
    db: AsyncIOMotorDatabase = Depends(get_db),
    current_user: UserInDB = Depends(require_admin)
):
    """Update S&OP cycle (Admin only)"""
    cycle_service = SOPCycleService(db)

    # Convert request to SOPCycleUpdate model
    update_data = SOPCycleUpdate(**cycle_update.model_dump(exclude_unset=True))

    updated_cycle = await cycle_service.update_cycle(cycle_id, update_data)

    if not updated_cycle:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Cycle not found"
        )

    return updated_cycle


@router.post(
    "/{cycle_id}/open",
    response_model=CycleActionResponse,
    summary="Open cycle",
    description="Open a cycle for forecast submissions. Admin only. Transitions from DRAFT to OPEN."
)
async def open_cycle(
    cycle_id: str,
    db: AsyncIOMotorDatabase = Depends(get_db),
    current_user: UserInDB = Depends(require_admin)
):
    """
    Open a cycle for forecast submissions (Admin only)

    Transitions cycle from DRAFT to OPEN status.
    Validates that:
    - Cycle is in DRAFT status
    - No other cycle is currently OPEN

    Triggers notifications to sales reps.
    """
    cycle_service = SOPCycleService(db)

    opened_cycle = await cycle_service.open_cycle(cycle_id, current_user.id)

    return CycleActionResponse(
        success=True,
        message=f"Cycle '{opened_cycle.cycleName}' has been opened successfully. Sales reps can now submit forecasts.",
        cycle=opened_cycle
    )


@router.post(
    "/{cycle_id}/close",
    response_model=CycleActionResponse,
    summary="Close cycle",
    description="Close a cycle and finalize submissions. Admin only. Transitions from OPEN to CLOSED."
)
async def close_cycle(
    cycle_id: str,
    db: AsyncIOMotorDatabase = Depends(get_db),
    current_user: UserInDB = Depends(require_admin)
):
    """
    Close a cycle and finalize submissions (Admin only)

    Transitions cycle from OPEN to CLOSED status.
    Validates that cycle is in OPEN status.

    Before closing:
    - Updates submission statistics
    - Calculates completion percentage

    After closing:
    - Triggers notifications to admins
    - Cycle data is archived and read-only
    """
    cycle_service = SOPCycleService(db)

    closed_cycle = await cycle_service.close_cycle(cycle_id, current_user.id)

    return CycleActionResponse(
        success=True,
        message=f"Cycle '{closed_cycle.cycleName}' has been closed successfully. Final completion: {closed_cycle.stats.completionPercentage}%",
        cycle=closed_cycle
    )


@router.put(
    "/{cycle_id}/status",
    response_model=CycleActionResponse,
    summary="Update cycle status",
    description="Unified endpoint to update cycle status. Admin only. Supports DRAFT, OPEN, CLOSED transitions."
)
async def update_cycle_status(
    cycle_id: str,
    status_update: dict,
    db: AsyncIOMotorDatabase = Depends(get_db),
    current_user: UserInDB = Depends(require_admin)
):
    """
    Update cycle status - Unified endpoint (Admin only)

    Accepts status in request body: {"status": "OPEN"} or {"status": "CLOSED"}

    This endpoint provides a unified way to change cycle status, internally
    calling the appropriate open_cycle() or close_cycle() methods.
    """
    cycle_service = SOPCycleService(db)

    new_status = status_update.get("status", "").upper()

    if new_status not in ["DRAFT", "OPEN", "CLOSED"]:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid status. Must be DRAFT, OPEN, or CLOSED"
        )

    # Get current cycle to check current status
    cycle = await cycle_service.get_cycle_by_id(cycle_id)
    if not cycle:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Cycle not found"
        )

    # Handle status transitions
    if new_status == "OPEN":
        updated_cycle = await cycle_service.open_cycle(cycle_id, current_user.id)
        message = f"Cycle '{updated_cycle.cycleName}' has been opened successfully. Sales reps can now submit forecasts."
    elif new_status == "CLOSED":
        updated_cycle = await cycle_service.close_cycle(cycle_id, current_user.id)
        message = f"Cycle '{updated_cycle.cycleName}' has been closed successfully. Final completion: {updated_cycle.stats.completionPercentage}%"
    elif new_status == "DRAFT":
        # Transition back to DRAFT (only from OPEN if no submissions)
        if cycle.status != "OPEN":
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Can only transition to DRAFT from OPEN status"
            )
        if cycle.stats.submittedForecasts > 0:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Cannot transition to DRAFT - cycle has submitted forecasts"
            )
        # Update to DRAFT
        update_data = SOPCycleUpdate(status="DRAFT")
        updated_cycle = await cycle_service.update_cycle(cycle_id, update_data)
        message = f"Cycle '{updated_cycle.cycleName}' has been moved back to DRAFT status."

    return CycleActionResponse(
        success=True,
        message=message,
        cycle=updated_cycle
    )


@router.post(
    "/{cycle_id}/refresh-stats",
    response_model=SOPCycleResponse,
    summary="Refresh cycle statistics",
    description="Manually refresh submission statistics for a cycle. Admin only."
)
async def refresh_cycle_statistics(
    cycle_id: str,
    db: AsyncIOMotorDatabase = Depends(get_db),
    current_user: UserInDB = Depends(require_admin)
):
    """
    Refresh cycle submission statistics (Admin only)

    Recalculates:
    - Total forecasts
    - Submitted forecasts
    - Sales rep participation
    - Completion percentage
    """
    cycle_service = SOPCycleService(db)

    # Update statistics
    await cycle_service.update_cycle_statistics(cycle_id)

    # Get updated cycle
    updated_cycle = await cycle_service.get_cycle_by_id(cycle_id)

    if not updated_cycle:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Cycle not found"
        )

    return updated_cycle


@router.delete(
    "/{cycle_id}",
    response_model=MessageResponse,
    summary="Delete cycle",
    description="Delete a cycle (only if in DRAFT status). Admin only."
)
async def delete_cycle(
    cycle_id: str,
    db: AsyncIOMotorDatabase = Depends(get_db),
    current_user: UserInDB = Depends(require_admin)
):
    """
    Delete a cycle (Admin only)

    Can only delete cycles in DRAFT status.
    OPEN and CLOSED cycles cannot be deleted.
    """
    cycle_service = SOPCycleService(db)

    success = await cycle_service.delete_cycle(cycle_id)

    if not success:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Cycle not found"
        )

    return MessageResponse(
        message="Cycle deleted successfully",
        success=True
    )
