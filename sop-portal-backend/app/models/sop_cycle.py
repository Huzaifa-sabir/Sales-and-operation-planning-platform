from pydantic import BaseModel, Field
from typing import Optional, Dict, Any
from datetime import datetime
from enum import Enum


class CycleStatus(str, Enum):
    """S&OP Cycle status"""
    DRAFT = "draft"
    OPEN = "open"
    CLOSED = "closed"


class CycleDates(BaseModel):
    """S&OP Cycle date ranges"""
    startDate: datetime = Field(..., description="Cycle start date")
    endDate: datetime = Field(..., description="Cycle end date")
    submissionDeadline: datetime = Field(..., description="Submission deadline")


class CycleStats(BaseModel):
    """S&OP Cycle statistics"""
    totalForecasts: int = Field(default=0, description="Total forecast entries")
    submittedForecasts: int = Field(default=0, description="Number of submitted forecasts")
    totalSalesReps: int = Field(default=0, description="Total number of sales reps")
    submittedSalesReps: int = Field(default=0, description="Number of reps who submitted")
    completionPercentage: float = Field(default=0.0, ge=0, le=100, description="Completion percentage")


class SOPCycleBase(BaseModel):
    """Base S&OP Cycle model"""
    cycleName: str = Field(..., description="Cycle name (e.g., 'S&OP Cycle 2025-11')")
    cycleYear: int = Field(..., ge=2020, le=2100, description="Cycle year")
    cycleMonth: int = Field(..., ge=1, le=12, description="Cycle month")
    # Frontend-driven persisted metadata (optional)
    year: Optional[int] = Field(None, ge=2020, le=2100, description="Explicit year provided by client")
    month: Optional[int] = Field(None, ge=1, le=12, description="Explicit month provided by client")
    planningStartMonth: Optional[datetime] = Field(None, description="Client-provided planning start month anchor")
    status: CycleStatus = Field(default=CycleStatus.DRAFT, description="Cycle status")
    dates: CycleDates = Field(..., description="Cycle date ranges")
    planningPeriod: Dict[str, Any] = Field(..., description="16-month planning period details")
    stats: CycleStats = Field(default_factory=CycleStats, description="Cycle statistics")


class SOPCycleCreate(BaseModel):
    """Input model for creating an S&OP cycle (minimal fields)"""
    cycleName: Optional[str] = None
    startDate: Optional[datetime] = None
    endDate: Optional[datetime] = None
    year: Optional[int] = None
    month: Optional[int] = None
    planningStartMonth: Optional[datetime] = None
    createdBy: Optional[str] = None


class SOPCycleUpdate(BaseModel):
    """Model for updating an S&OP cycle"""
    cycleName: Optional[str] = None
    status: Optional[CycleStatus] = None
    dates: Optional[CycleDates] = None
    stats: Optional[CycleStats] = None
    year: Optional[int] = None
    month: Optional[int] = None
    planningStartMonth: Optional[datetime] = None
    # Allow direct date updates (for API convenience)
    startDate: Optional[datetime] = None
    endDate: Optional[datetime] = None


class SOPCycleInDB(SOPCycleBase):
    """S&OP Cycle model as stored in database"""
    id: str = Field(..., alias="_id", description="Cycle document ID")
    createdBy: Optional[str] = Field(None, description="User ID who created cycle")
    createdAt: datetime = Field(default_factory=datetime.utcnow)
    updatedAt: datetime = Field(default_factory=datetime.utcnow)
    openedAt: Optional[datetime] = Field(None, description="When cycle was opened")
    closedAt: Optional[datetime] = Field(None, description="When cycle was closed")

    class Config:
        populate_by_name = True
        json_schema_extra = {
            "example": {
                "_id": "507f1f77bcf86cd799439011",
                "cycleName": "S&OP Cycle 2025-11",
                "cycleYear": 2025,
                "cycleMonth": 11,
                "status": "open",
                "dates": {
                    "startDate": "2025-10-15T00:00:00Z",
                    "endDate": "2025-10-30T00:00:00Z",
                    "submissionDeadline": "2025-10-23T00:00:00Z"
                },
                "planningPeriod": {
                    "startYear": 2025,
                    "startMonth": 7,
                    "endYear": 2026,
                    "endMonth": 10,
                    "totalMonths": 16
                },
                "stats": {
                    "totalForecasts": 2500,
                    "submittedForecasts": 2000,
                    "totalSalesReps": 10,
                    "submittedSalesReps": 8,
                    "completionPercentage": 80.0
                },
                "createdBy": "507f1f77bcf86cd799439012",
                "createdAt": "2025-10-01T00:00:00Z",
                "updatedAt": "2025-10-15T00:00:00Z",
                "openedAt": "2025-10-10T00:00:00Z",
                "closedAt": None
            }
        }


class SOPCycleResponse(SOPCycleBase):
    """S&OP Cycle response model"""
    id: str = Field(..., alias="_id")
    createdBy: Optional[str] = None
    createdAt: datetime
    updatedAt: datetime
    openedAt: Optional[datetime] = None
    closedAt: Optional[datetime] = None

    class Config:
        populate_by_name = True
        from_attributes = True
