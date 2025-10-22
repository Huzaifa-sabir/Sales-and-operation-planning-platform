"""
Audit Logging Service
Tracks all critical user actions for compliance and debugging
"""
from typing import List, Optional, Dict, Any
from motor.motor_asyncio import AsyncIOMotorDatabase
from datetime import datetime, timedelta
from bson import ObjectId

from app.models.audit_log import (
    AuditLogCreate,
    AuditLogInDB,
    AuditAction,
    AuditSeverity
)


class AuditService:
    """Service for audit logging"""

    def __init__(self, db: AsyncIOMotorDatabase):
        self.db = db
        self.collection = db.audit_logs

    async def log(
        self,
        action: AuditAction,
        user_id: Optional[str] = None,
        user_email: Optional[str] = None,
        entity_type: Optional[str] = None,
        entity_id: Optional[str] = None,
        changes: Optional[Dict[str, Any]] = None,
        old_values: Optional[Dict[str, Any]] = None,
        new_values: Optional[Dict[str, Any]] = None,
        ip_address: Optional[str] = None,
        user_agent: Optional[str] = None,
        severity: AuditSeverity = AuditSeverity.INFO,
        description: Optional[str] = None,
        metadata: Optional[Dict[str, Any]] = None
    ) -> AuditLogInDB:
        """
        Log an audit event

        Args:
            action: Type of action performed
            user_id: ID of user who performed action
            user_email: Email of user
            entity_type: Type of entity affected (e.g., 'user', 'cycle', 'forecast')
            entity_id: ID of affected entity
            changes: Dictionary of changes made
            old_values: Previous values before change
            new_values: New values after change
            ip_address: IP address of requester
            user_agent: User agent string
            severity: Severity level
            description: Human-readable description
            metadata: Additional metadata

        Returns:
            Created audit log entry
        """
        log_entry = {
            "action": action.value,
            "userId": user_id,
            "userEmail": user_email,
            "entityType": entity_type,
            "entityId": entity_id,
            "changes": changes,
            "oldValues": old_values,
            "newValues": new_values,
            "ipAddress": ip_address,
            "userAgent": user_agent,
            "severity": severity.value,
            "description": description,
            "metadata": metadata,
            "timestamp": datetime.utcnow()
        }

        result = await self.collection.insert_one(log_entry)
        log_entry["_id"] = str(result.inserted_id)

        return AuditLogInDB(**log_entry)

    async def get_logs(
        self,
        user_id: Optional[str] = None,
        action: Optional[AuditAction] = None,
        entity_type: Optional[str] = None,
        entity_id: Optional[str] = None,
        severity: Optional[AuditSeverity] = None,
        start_date: Optional[datetime] = None,
        end_date: Optional[datetime] = None,
        skip: int = 0,
        limit: int = 100
    ) -> tuple[List[AuditLogInDB], int]:
        """Get audit logs with filters"""
        query = {}

        if user_id:
            query["userId"] = user_id

        if action:
            query["action"] = action.value

        if entity_type:
            query["entityType"] = entity_type

        if entity_id:
            query["entityId"] = entity_id

        if severity:
            query["severity"] = severity.value

        if start_date or end_date:
            query["timestamp"] = {}
            if start_date:
                query["timestamp"]["$gte"] = start_date
            if end_date:
                query["timestamp"]["$lte"] = end_date

        # Get total count
        total = await self.collection.count_documents(query)

        # Get logs (most recent first)
        cursor = self.collection.find(query).sort("timestamp", -1).skip(skip).limit(limit)
        logs_docs = await cursor.to_list(length=limit)

        logs = []
        for doc in logs_docs:
            doc["_id"] = str(doc["_id"])
            logs.append(AuditLogInDB(**doc))

        return logs, total

    async def get_user_activity(
        self,
        user_id: str,
        days: int = 30
    ) -> List[AuditLogInDB]:
        """Get recent activity for a specific user"""
        start_date = datetime.utcnow() - timedelta(days=days)

        logs, _ = await self.get_logs(
            user_id=user_id,
            start_date=start_date,
            limit=100
        )

        return logs

    async def get_entity_history(
        self,
        entity_type: str,
        entity_id: str,
        limit: int = 50
    ) -> List[AuditLogInDB]:
        """Get change history for a specific entity"""
        logs, _ = await self.get_logs(
            entity_type=entity_type,
            entity_id=entity_id,
            limit=limit
        )

        return logs

    async def get_critical_events(
        self,
        hours: int = 24,
        limit: int = 100
    ) -> List[AuditLogInDB]:
        """Get recent critical/error events"""
        start_date = datetime.utcnow() - timedelta(hours=hours)

        query = {
            "severity": {"$in": [AuditSeverity.ERROR.value, AuditSeverity.CRITICAL.value]},
            "timestamp": {"$gte": start_date}
        }

        cursor = self.collection.find(query).sort("timestamp", -1).limit(limit)
        logs_docs = await cursor.to_list(length=limit)

        logs = []
        for doc in logs_docs:
            doc["_id"] = str(doc["_id"])
            logs.append(AuditLogInDB(**doc))

        return logs

    async def get_statistics(
        self,
        start_date: Optional[datetime] = None,
        end_date: Optional[datetime] = None
    ) -> Dict[str, Any]:
        """Get audit log statistics"""
        query = {}

        if start_date or end_date:
            query["timestamp"] = {}
            if start_date:
                query["timestamp"]["$gte"] = start_date
            if end_date:
                query["timestamp"]["$lte"] = end_date

        # Total logs
        total_logs = await self.collection.count_documents(query)

        # Logs by action
        action_pipeline = [
            {"$match": query},
            {"$group": {"_id": "$action", "count": {"$sum": 1}}},
            {"$sort": {"count": -1}}
        ]
        actions_result = await self.collection.aggregate(action_pipeline).to_list(None)

        # Logs by severity
        severity_pipeline = [
            {"$match": query},
            {"$group": {"_id": "$severity", "count": {"$sum": 1}}}
        ]
        severity_result = await self.collection.aggregate(severity_pipeline).to_list(None)

        # Most active users
        user_pipeline = [
            {"$match": query},
            {"$match": {"userId": {"$ne": None}}},
            {"$group": {"_id": "$userId", "count": {"$sum": 1}, "userEmail": {"$first": "$userEmail"}}},
            {"$sort": {"count": -1}},
            {"$limit": 10}
        ]
        users_result = await self.collection.aggregate(user_pipeline).to_list(None)

        return {
            "totalLogs": total_logs,
            "actionBreakdown": actions_result,
            "severityBreakdown": severity_result,
            "mostActiveUsers": users_result
        }

    async def cleanup_old_logs(self, days: int = 90) -> int:
        """Delete audit logs older than specified days"""
        cutoff_date = datetime.utcnow() - timedelta(days=days)

        result = await self.collection.delete_many({
            "timestamp": {"$lt": cutoff_date}
        })

        return result.deleted_count
