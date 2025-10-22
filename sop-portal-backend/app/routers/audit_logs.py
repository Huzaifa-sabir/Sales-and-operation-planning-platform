"""
Audit Logs Router
Endpoints for viewing audit logs
"""
from fastapi import APIRouter, Depends, HTTPException, status, Query
from typing import List, Optional
from datetime import datetime

from app.models.user import UserInDB
from app.models.audit_log import AuditLogResponse, AuditAction, AuditSeverity
from app.services.audit_service import AuditService
from app.utils.auth_dependencies import get_current_user, require_admin
from app.config.database import get_db

router = APIRouter(prefix="/audit-logs", tags=["Audit Logs"])


async def get_audit_service():
    """Get audit service"""
    db = await get_db()
    return AuditService(db)


@router.get("", response_model=List[AuditLogResponse])
async def list_audit_logs(
    action: Optional[AuditAction] = None,
    entity_type: Optional[str] = None,
    entity_id: Optional[str] = None,
    severity: Optional[AuditSeverity] = None,
    start_date: Optional[datetime] = None,
    end_date: Optional[datetime] = None,
    skip: int = 0,
    limit: int = 100,
    current_user: UserInDB = Depends(require_admin),
    audit_service: AuditService = Depends(get_audit_service)
):
    """List audit logs with filters (admin only)"""
    logs, total = await audit_service.get_logs(
        action=action,
        entity_type=entity_type,
        entity_id=entity_id,
        severity=severity,
        start_date=start_date,
        end_date=end_date,
        skip=skip,
        limit=limit
    )
    return logs


@router.get("/my-activity", response_model=List[AuditLogResponse])
async def get_my_activity(
    days: int = Query(30, ge=1, le=365),
    current_user: UserInDB = Depends(get_current_user),
    audit_service: AuditService = Depends(get_audit_service)
):
    """Get current user's activity history"""
    return await audit_service.get_user_activity(current_user.id, days=days)


@router.get("/entity/{entity_type}/{entity_id}", response_model=List[AuditLogResponse])
async def get_entity_history(
    entity_type: str,
    entity_id: str,
    current_user: UserInDB = Depends(get_current_user),
    audit_service: AuditService = Depends(get_audit_service)
):
    """Get change history for a specific entity"""
    return await audit_service.get_entity_history(entity_type, entity_id)


@router.get("/critical-events", response_model=List[AuditLogResponse])
async def get_critical_events(
    hours: int = Query(24, ge=1, le=168),
    current_user: UserInDB = Depends(require_admin),
    audit_service: AuditService = Depends(get_audit_service)
):
    """Get recent critical/error events (admin only)"""
    return await audit_service.get_critical_events(hours=hours)


@router.get("/statistics", response_model=dict)
async def get_audit_statistics(
    start_date: Optional[datetime] = None,
    end_date: Optional[datetime] = None,
    current_user: UserInDB = Depends(require_admin),
    audit_service: AuditService = Depends(get_audit_service)
):
    """Get audit log statistics (admin only)"""
    return await audit_service.get_statistics(start_date=start_date, end_date=end_date)
