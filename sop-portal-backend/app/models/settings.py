"""
System Settings Models
Manages application-wide settings and configurations
"""
from pydantic import BaseModel, Field
from typing import Optional, Dict, Any
from datetime import datetime
from enum import Enum


class SettingCategory(str, Enum):
    """Setting category enum"""
    GENERAL = "general"
    NOTIFICATIONS = "notifications"
    SOP_CYCLE = "sop_cycle"
    EMAIL = "email"
    SECURITY = "security"
    REPORTS = "reports"
    SYSTEM = "system"


class SettingCreate(BaseModel):
    """Create new setting"""
    key: str = Field(..., description="Unique setting key (e.g., 'reminder_days_before_close')")
    value: Any = Field(..., description="Setting value (can be string, number, boolean, or object)")
    category: SettingCategory = Field(..., description="Setting category")
    label: str = Field(..., description="Human-readable label")
    description: Optional[str] = Field(None, description="Detailed description of the setting")
    dataType: str = Field("string", description="Data type: string, number, boolean, object")
    isPublic: bool = Field(False, description="Whether setting is publicly readable (without auth)")
    isEditable: bool = Field(True, description="Whether setting can be edited via API")


class SettingUpdate(BaseModel):
    """Update existing setting"""
    value: Optional[Any] = None
    label: Optional[str] = None
    description: Optional[str] = None
    isPublic: Optional[bool] = None
    isEditable: Optional[bool] = None


class SettingInDB(BaseModel):
    """Setting in database"""
    id: str = Field(..., alias="_id")
    key: str
    value: Any
    category: SettingCategory
    label: str
    description: Optional[str] = None
    dataType: str
    isPublic: bool = False
    isEditable: bool = True
    createdAt: datetime = Field(default_factory=datetime.utcnow)
    updatedAt: datetime = Field(default_factory=datetime.utcnow)
    createdBy: Optional[str] = None
    updatedBy: Optional[str] = None

    class Config:
        populate_by_name = True
        json_encoders = {datetime: lambda v: v.isoformat()}


class SettingResponse(BaseModel):
    """Setting response model"""
    id: str
    key: str
    value: Any
    category: SettingCategory
    label: str
    description: Optional[str] = None
    dataType: str
    isPublic: bool
    isEditable: bool
    createdAt: datetime
    updatedAt: datetime


# Default system settings
DEFAULT_SETTINGS = [
    {
        "key": "reminder_days_before_close",
        "value": 3,
        "category": "sop_cycle",
        "label": "Reminder Days Before Close",
        "description": "Number of days before cycle close to send reminder emails",
        "dataType": "number",
        "isPublic": False,
        "isEditable": True
    },
    {
        "key": "auto_close_cycles",
        "value": True,
        "category": "sop_cycle",
        "label": "Auto-Close Cycles",
        "description": "Automatically close cycles after deadline",
        "dataType": "boolean",
        "isPublic": False,
        "isEditable": True
    },
    {
        "key": "cleanup_temp_files_days",
        "value": 7,
        "category": "system",
        "label": "Cleanup Temporary Files (Days)",
        "description": "Delete temporary files older than X days",
        "dataType": "number",
        "isPublic": False,
        "isEditable": True
    },
    {
        "key": "report_expiry_days",
        "value": 7,
        "category": "reports",
        "label": "Report Expiry Days",
        "description": "Delete generated reports older than X days",
        "dataType": "number",
        "isPublic": False,
        "isEditable": True
    },
    {
        "key": "notification_email_enabled",
        "value": True,
        "category": "notifications",
        "label": "Email Notifications Enabled",
        "description": "Enable/disable all email notifications",
        "dataType": "boolean",
        "isPublic": False,
        "isEditable": True
    },
    {
        "key": "smtp_host",
        "value": "smtp.gmail.com",
        "category": "email",
        "label": "SMTP Host",
        "description": "SMTP server hostname",
        "dataType": "string",
        "isPublic": False,
        "isEditable": True
    },
    {
        "key": "smtp_port",
        "value": 587,
        "category": "email",
        "label": "SMTP Port",
        "description": "SMTP server port",
        "dataType": "number",
        "isPublic": False,
        "isEditable": True
    },
    {
        "key": "from_email",
        "value": "noreply@sopportal.com",
        "category": "email",
        "label": "From Email Address",
        "description": "Email address to send notifications from",
        "dataType": "string",
        "isPublic": False,
        "isEditable": True
    },
    {
        "key": "from_name",
        "value": "S&OP Portal",
        "category": "email",
        "label": "From Name",
        "description": "Display name for outgoing emails",
        "dataType": "string",
        "isPublic": False,
        "isEditable": True
    },
    {
        "key": "max_forecast_months",
        "value": 16,
        "category": "sop_cycle",
        "label": "Maximum Forecast Months",
        "description": "Maximum number of months for forecast entry",
        "dataType": "number",
        "isPublic": True,
        "isEditable": True
    },
    {
        "key": "min_forecast_months_required",
        "value": 12,
        "category": "sop_cycle",
        "label": "Minimum Forecast Months Required",
        "description": "Minimum number of months required for forecast submission",
        "dataType": "number",
        "isPublic": True,
        "isEditable": True
    },
    {
        "key": "rate_limit_requests_per_minute",
        "value": 60,
        "category": "security",
        "label": "Rate Limit (Requests/Minute)",
        "description": "Maximum API requests per minute per user",
        "dataType": "number",
        "isPublic": False,
        "isEditable": True
    },
    {
        "key": "session_timeout_minutes",
        "value": 480,
        "category": "security",
        "label": "Session Timeout (Minutes)",
        "description": "JWT token expiry time in minutes (default: 8 hours)",
        "dataType": "number",
        "isPublic": False,
        "isEditable": True
    },
    {
        "key": "app_name",
        "value": "S&OP Portal",
        "category": "general",
        "label": "Application Name",
        "description": "Display name of the application",
        "dataType": "string",
        "isPublic": True,
        "isEditable": True
    },
    {
        "key": "app_version",
        "value": "1.0.0",
        "category": "general",
        "label": "Application Version",
        "description": "Current version of the application",
        "dataType": "string",
        "isPublic": True,
        "isEditable": False
    },
    {
        "key": "enable_audit_logging",
        "value": True,
        "category": "system",
        "label": "Enable Audit Logging",
        "description": "Log all critical user actions for audit trail",
        "dataType": "boolean",
        "isPublic": False,
        "isEditable": True
    }
]
