"""
Audit Log Models
Tracks all critical user actions for compliance and debugging
"""
from pydantic import BaseModel, Field
from typing import Optional, Dict, Any
from datetime import datetime
from enum import Enum


class AuditAction(str, Enum):
    """Audit action types"""
    # User actions
    USER_LOGIN = "user_login"
    USER_LOGOUT = "user_logout"
    USER_CREATED = "user_created"
    USER_UPDATED = "user_updated"
    USER_DELETED = "user_deleted"
    USER_PASSWORD_CHANGED = "user_password_changed"

    # S&OP Cycle actions
    CYCLE_CREATED = "cycle_created"
    CYCLE_UPDATED = "cycle_updated"
    CYCLE_OPENED = "cycle_opened"
    CYCLE_CLOSED = "cycle_closed"
    CYCLE_DELETED = "cycle_deleted"

    # Forecast actions
    FORECAST_CREATED = "forecast_created"
    FORECAST_UPDATED = "forecast_updated"
    FORECAST_SUBMITTED = "forecast_submitted"
    FORECAST_APPROVED = "forecast_approved"
    FORECAST_REJECTED = "forecast_rejected"
    FORECAST_DELETED = "forecast_deleted"

    # Customer/Product actions
    CUSTOMER_CREATED = "customer_created"
    CUSTOMER_UPDATED = "customer_updated"
    CUSTOMER_DELETED = "customer_deleted"
    PRODUCT_CREATED = "product_created"
    PRODUCT_UPDATED = "product_updated"
    PRODUCT_DELETED = "product_deleted"

    # Pricing actions
    PRICING_MATRIX_UPDATED = "pricing_matrix_updated"
    PRICING_BULK_IMPORT = "pricing_bulk_import"

    # Sales history actions
    SALES_HISTORY_IMPORTED = "sales_history_imported"
    SALES_HISTORY_UPDATED = "sales_history_updated"

    # Report actions
    REPORT_GENERATED = "report_generated"
    REPORT_DOWNLOADED = "report_downloaded"
    REPORT_DELETED = "report_deleted"

    # Settings actions
    SETTING_UPDATED = "setting_updated"

    # System actions
    SYSTEM_BACKUP_CREATED = "system_backup_created"
    SYSTEM_RESTORE_PERFORMED = "system_restore_performed"


class AuditSeverity(str, Enum):
    """Severity levels for audit events"""
    INFO = "info"
    WARNING = "warning"
    ERROR = "error"
    CRITICAL = "critical"


class AuditLogCreate(BaseModel):
    """Create audit log entry"""
    action: AuditAction
    userId: Optional[str] = Field(None, description="User who performed the action")
    userEmail: Optional[str] = Field(None, description="Email of user who performed action")
    entityType: Optional[str] = Field(None, description="Type of entity affected (user, cycle, forecast, etc.)")
    entityId: Optional[str] = Field(None, description="ID of affected entity")
    changes: Optional[Dict[str, Any]] = Field(None, description="JSON object of changes made")
    oldValues: Optional[Dict[str, Any]] = Field(None, description="Previous values before change")
    newValues: Optional[Dict[str, Any]] = Field(None, description="New values after change")
    ipAddress: Optional[str] = Field(None, description="IP address of requester")
    userAgent: Optional[str] = Field(None, description="User agent string")
    severity: AuditSeverity = Field(AuditSeverity.INFO, description="Severity level")
    description: Optional[str] = Field(None, description="Human-readable description")
    metadata: Optional[Dict[str, Any]] = Field(None, description="Additional metadata")


class AuditLogInDB(BaseModel):
    """Audit log in database"""
    id: str = Field(..., alias="_id")
    action: AuditAction
    userId: Optional[str] = None
    userEmail: Optional[str] = None
    entityType: Optional[str] = None
    entityId: Optional[str] = None
    changes: Optional[Dict[str, Any]] = None
    oldValues: Optional[Dict[str, Any]] = None
    newValues: Optional[Dict[str, Any]] = None
    ipAddress: Optional[str] = None
    userAgent: Optional[str] = None
    severity: AuditSeverity = AuditSeverity.INFO
    description: Optional[str] = None
    metadata: Optional[Dict[str, Any]] = None
    timestamp: datetime = Field(default_factory=datetime.utcnow)

    class Config:
        populate_by_name = True
        json_encoders = {datetime: lambda v: v.isoformat()}


class AuditLogResponse(BaseModel):
    """Audit log response"""
    id: str
    action: AuditAction
    userId: Optional[str] = None
    userEmail: Optional[str] = None
    entityType: Optional[str] = None
    entityId: Optional[str] = None
    changes: Optional[Dict[str, Any]] = None
    severity: AuditSeverity
    description: Optional[str] = None
    timestamp: datetime
