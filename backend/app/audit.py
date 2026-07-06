"""
Audit Logging Module
Logs security and compliance events for audit trail
Requirements: 3.6, 18.4
"""
from typing import Optional, Dict, Any
from datetime import datetime
import uuid
import logging

logger = logging.getLogger(__name__)


class AuditLogger:
    """
    Audit logging service for security and compliance
    
    Logs events to the audit_logs table including:
    - Content violations (NSFW rejections)
    - Data access events
    - Authentication events
    - Administrative actions
    """
    
    def __init__(self, supabase_client):
        """
        Initialize audit logger
        
        Args:
            supabase_client: Supabase/PostgreSQL client instance (None for demo mode)
        """
        self.supabase = supabase_client
        self.demo_mode = supabase_client is None
    
    async def log_content_violation(
        self,
        user_id: Optional[str],
        nsfw_score: float,
        non_skin_score: float,
        rejection_reason: str,
        ip_address: Optional[str] = None,
        additional_metadata: Optional[Dict[str, Any]] = None
    ) -> str:
        """
        Log content violation (NSFW rejection)
        
        Args:
            user_id: User ID (if authenticated)
            nsfw_score: NSFW detection score
            non_skin_score: Non-skin detection score
            rejection_reason: Reason for rejection
            ip_address: Client IP address
            additional_metadata: Additional context data
            
        Returns:
            Audit log entry ID
        """
        metadata = {
            "nsfw_score": nsfw_score,
            "non_skin_score": non_skin_score,
            "rejection_reason": rejection_reason
        }
        
        if additional_metadata:
            metadata.update(additional_metadata)
        
        return await self._create_audit_log(
            user_id=user_id,
            action="content_violation",
            resource_type="image_upload",
            resource_id=None,
            metadata=metadata,
            ip_address=ip_address
        )
    
    async def log_data_access(
        self,
        user_id: str,
        resource_type: str,
        resource_id: str,
        action: str = "read",
        ip_address: Optional[str] = None,
        additional_metadata: Optional[Dict[str, Any]] = None
    ) -> str:
        """
        Log data access event
        
        Args:
            user_id: User ID accessing the data
            resource_type: Type of resource (e.g., 'medical_report', 'patient_data')
            resource_id: ID of the accessed resource
            action: Action performed (e.g., 'read', 'update', 'delete')
            ip_address: Client IP address
            additional_metadata: Additional context data
            
        Returns:
            Audit log entry ID
        """
        metadata = {
            "action_type": action
        }
        
        if additional_metadata:
            metadata.update(additional_metadata)
        
        return await self._create_audit_log(
            user_id=user_id,
            action=f"data_access_{action}",
            resource_type=resource_type,
            resource_id=resource_id,
            metadata=metadata,
            ip_address=ip_address
        )
    
    async def log_authentication_event(
        self,
        user_id: Optional[str],
        event_type: str,
        success: bool,
        ip_address: Optional[str] = None,
        additional_metadata: Optional[Dict[str, Any]] = None
    ) -> str:
        """
        Log authentication event
        
        Args:
            user_id: User ID (if available)
            event_type: Type of event (e.g., 'login', 'logout', 'signup')
            success: Whether the event was successful
            ip_address: Client IP address
            additional_metadata: Additional context data
            
        Returns:
            Audit log entry ID
        """
        metadata = {
            "event_type": event_type,
            "success": success
        }
        
        if additional_metadata:
            metadata.update(additional_metadata)
        
        return await self._create_audit_log(
            user_id=user_id,
            action=f"auth_{event_type}",
            resource_type="authentication",
            resource_id=None,
            metadata=metadata,
            ip_address=ip_address
        )
    
    async def log_admin_action(
        self,
        admin_user_id: str,
        action: str,
        resource_type: str,
        resource_id: Optional[str] = None,
        ip_address: Optional[str] = None,
        additional_metadata: Optional[Dict[str, Any]] = None
    ) -> str:
        """
        Log administrative action
        
        Args:
            admin_user_id: Admin user ID
            action: Action performed (e.g., 'verify_doctor', 'moderate_content')
            resource_type: Type of resource affected
            resource_id: ID of the affected resource
            ip_address: Client IP address
            additional_metadata: Additional context data
            
        Returns:
            Audit log entry ID
        """
        metadata = additional_metadata or {}
        
        return await self._create_audit_log(
            user_id=admin_user_id,
            action=f"admin_{action}",
            resource_type=resource_type,
            resource_id=resource_id,
            metadata=metadata,
            ip_address=ip_address
        )
    
    async def log_action(
        self,
        user_id: str,
        action: str,
        resource_type: str,
        resource_id: Optional[str] = None,
        metadata: Optional[Dict[str, Any]] = None,
        ip_address: Optional[str] = None
    ) -> str:
        """
        Generic action logging method
        
        Args:
            user_id: User ID performing the action
            action: Action performed
            resource_type: Type of resource affected
            resource_id: ID of the affected resource (optional)
            metadata: Additional context data (optional)
            ip_address: Client IP address (optional)
            
        Returns:
            Audit log entry ID
        """
        return await self._create_audit_log(
            user_id=user_id,
            action=action,
            resource_type=resource_type,
            resource_id=resource_id,
            metadata=metadata or {},
            ip_address=ip_address
        )
    
    async def _create_audit_log(
        self,
        user_id: Optional[str],
        action: str,
        resource_type: str,
        resource_id: Optional[str],
        metadata: Dict[str, Any],
        ip_address: Optional[str]
    ) -> str:
        """
        Create audit log entry in database
        
        Args:
            user_id: User ID (optional)
            action: Action performed
            resource_type: Type of resource
            resource_id: Resource ID (optional)
            metadata: Additional metadata
            ip_address: Client IP address (optional)
            
        Returns:
            Created audit log entry ID
        """
        try:
            # Prepare audit log entry
            audit_entry = {
                "user_id": user_id,
                "action": action,
                "resource_type": resource_type,
                "resource_id": resource_id,
                "metadata": metadata,
                "ip_address": ip_address,
                "created_at": datetime.utcnow().isoformat()
            }
            
            # Demo mode - just log and return UUID
            if self.demo_mode:
                logger.info(f"DEMO MODE: Audit log created: {action} (user: {user_id})")
                return str(uuid.uuid4())
            
            # Insert into database
            result = self.supabase.table("audit_logs").insert(audit_entry).execute()
            
            if result.data and len(result.data) > 0:
                audit_id = result.data[0]["id"]
                logger.info(f"Audit log created: {action} (ID: {audit_id})")
                return audit_id
            else:
                logger.error(f"Failed to create audit log: {action}")
                return str(uuid.uuid4())  # Return a UUID even if insert fails
                
        except Exception as e:
            logger.error(f"Error creating audit log: {str(e)}")
            # Don't fail the main operation if audit logging fails
            return str(uuid.uuid4())
    
    async def get_audit_logs(
        self,
        user_id: Optional[str] = None,
        action: Optional[str] = None,
        resource_type: Optional[str] = None,
        limit: int = 100,
        offset: int = 0
    ) -> list:
        """
        Retrieve audit logs with optional filters
        
        Args:
            user_id: Filter by user ID
            action: Filter by action type
            resource_type: Filter by resource type
            limit: Maximum number of records to return
            offset: Number of records to skip
            
        Returns:
            List of audit log entries
        """
        try:
            query = self.supabase.table("audit_logs").select("*")
            
            if user_id:
                query = query.eq("user_id", user_id)
            
            if action:
                query = query.eq("action", action)
            
            if resource_type:
                query = query.eq("resource_type", resource_type)
            
            query = query.order("created_at", desc=True).limit(limit).offset(offset)
            
            result = query.execute()
            
            return result.data if result.data else []
            
        except Exception as e:
            logger.error(f"Error retrieving audit logs: {str(e)}")
            return []
    
    async def get_content_violations(
        self,
        user_id: Optional[str] = None,
        limit: int = 100
    ) -> list:
        """
        Retrieve content violation logs
        
        Args:
            user_id: Filter by user ID (optional)
            limit: Maximum number of records to return
            
        Returns:
            List of content violation audit logs
        """
        return await self.get_audit_logs(
            user_id=user_id,
            action="content_violation",
            limit=limit
        )


def create_audit_logger(supabase_client) -> AuditLogger:
    """
    Factory function to create audit logger instance
    
    Args:
        supabase_client: Supabase/PostgreSQL client instance
        
    Returns:
        AuditLogger instance
    """
    return AuditLogger(supabase_client)
