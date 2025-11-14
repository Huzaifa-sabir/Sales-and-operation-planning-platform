"""
S&OP Cycle API Schemas
Request and response models for S&OP cycle endpoints
"""
from typing import List, Optional
from datetime import datetime
from pydantic import BaseModel, Field

from app.models.sop_cycle import SOPCycleResponse


class CycleCreateRequest(BaseModel):
    """Request schema for creating a new cycle"""
    cycleName: Optional[str] = Field(None, description="Cycle name (auto-generated if not provided)")
    startDate: Optional[datetime] = Field(None, description="Start date (defaults to current date)")
    endDate: Optional[datetime] = Field(None, description="End date (defaults to end of month)")
    year: Optional[int] = Field(None, description="Explicit year provided by client")
    month: Optional[int] = Field(None, description="Explicit month provided by client")
    planningStartMonth: Optional[datetime] = Field(None, description="Planning start month anchor")


class CycleUpdateRequest(BaseModel):
    """Request schema for updating a cycle"""
    cycleName: Optional[str] = Field(None, min_length=1, max_length=200)
    startDate: Optional[datetime] = None
    endDate: Optional[datetime] = None
    year: Optional[int] = None
    month: Optional[int] = None
    planningStartMonth: Optional[datetime] = None


class CycleListResponse(BaseModel):
    """Response schema for paginated cycle list"""
    cycles: List[SOPCycleResponse]
    total: int = Field(..., description="Total number of cycles")
    page: int = Field(..., description="Current page number")
    pageSize: int = Field(..., description="Number of items per page")
    totalPages: int = Field(..., description="Total number of pages")
    hasNext: bool = Field(..., description="Whether there are more pages")
    hasPrev: bool = Field(..., description="Whether there are previous pages")


class CycleActionResponse(BaseModel):
    """Response schema for cycle actions (open/close)"""
    success: bool = Field(default=True)
    message: str
    cycle: SOPCycleResponse


class MessageResponse(BaseModel):
    """Generic message response"""
    message: str
    success: bool = Field(default=True)
