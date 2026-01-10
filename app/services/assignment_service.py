"""
Assignment service for user-role and role-permission assignments.
"""

import logging
from typing import List, Dict, Any, Optional
from uuid import UUID
from datetime import datetime

from app.clients import get_entity_client
from app.cache import get_cache
from app.models.assignment import (
    UserRoleAssignmentCreate, 
    UserRoleAssignmentResponse,
    RolePermissionAssignmentCreate,
    RolePermissionAssignmentResponse
)
from app.models.role import RoleResponse, PermissionSummary
from app.models.permission import PermissionResponse

logger = logging.getLogger(__name__)


class AssignmentService:
    """Service for assignment management."""
    
    def __init__(self):
        """Initialize assignment service."""
        self.entity_client = get_entity_client()
        self.cache = get_cache()
    
    # User-Role assignments
    async def assign_role_to_user(self, user_id: UUID, assignment_data: UserRoleAssignmentCreate) -> UserRoleAssignmentResponse:
        """Assign role to user."""
        assignment_dict = assignment_data.model_dump()
        result = await self.entity_client.assign_role_to_user(user_id, assignment_dict)
        
        # Clear cache for user
        self.cache.clear_user(str(user_id))
        self.cache.clear_tenant(str(assignment_data.tenant_id))
        
        logger.info(f"Assigned role {assignment_data.role_id} to user {user_id}")
        
        return UserRoleAssignmentResponse(
            assignment_id=result.get("assignment_id"),
            user_id=user_id,
            role_id=assignment_data.role_id,
            tenant_id=assignment_data.tenant_id,
            valid_from=assignment_data.valid_from,
            valid_until=assignment_data.valid_until,
            created_at=result.get("created_at", datetime.utcnow())
        )
    
    async def get_user_roles(self, user_id: UUID, tenant_id: Optional[UUID] = None, 
                            active_only: bool = True) -> List[RoleResponse]:
        """Get roles assigned to user."""
        roles = await self.entity_client.get_user_roles(user_id, tenant_id, active_only)
        
        # Convert to RoleResponse format
        role_responses = []
        for role in roles:
            permissions = await self.entity_client.get_role_permissions(UUID(role.get("role_id")))
            permission_summaries = [
                PermissionSummary(
                    permission_id=p.get("permission_id"),
                    name=p.get("name"),
                    resource_type=p.get("resource_type"),
                    action=p.get("action")
                )
                for p in permissions
            ]
            
            role_responses.append(RoleResponse(
                role_id=role.get("role_id"),
                name=role.get("name"),
                description=role.get("description"),
                tenant_id=role.get("tenant_id"),
                permissions=permission_summaries,
                created_at=role.get("created_at", datetime.utcnow()),
                updated_at=role.get("updated_at", datetime.utcnow())
            ))
        
        return role_responses
    
    async def revoke_role_from_user(self, user_id: UUID, role_id: UUID) -> bool:
        """Revoke role from user."""
        success = await self.entity_client.revoke_role_from_user(user_id, role_id)
        
        if success:
            # Clear cache for user
            self.cache.clear_user(str(user_id))
            logger.info(f"Revoked role {role_id} from user {user_id}")
        
        return success
    
    # Role-Permission assignments
    async def assign_permission_to_role(self, role_id: UUID, 
                                       assignment_data: RolePermissionAssignmentCreate) -> RolePermissionAssignmentResponse:
        """Assign permission to role."""
        assignment_dict = assignment_data.model_dump()
        result = await self.entity_client.assign_permission_to_role(role_id, assignment_dict)
        
        # Clear cache
        self.cache.delete_role(str(role_id))
        self.cache.clear_all()
        
        logger.info(f"Assigned permission {assignment_data.permission_id} to role {role_id}")
        
        return RolePermissionAssignmentResponse(
            assignment_id=result.get("assignment_id"),
            role_id=role_id,
            permission_id=assignment_data.permission_id,
            created_at=result.get("created_at", datetime.utcnow())
        )
    
    async def get_role_permissions(self, role_id: UUID) -> List[PermissionResponse]:
        """Get permissions assigned to role."""
        permissions = await self.entity_client.get_role_permissions(role_id)
        
        # Convert to PermissionResponse format
        return [
            PermissionResponse(
                permission_id=p.get("permission_id"),
                name=p.get("name"),
                description=p.get("description"),
                resource_type=p.get("resource_type"),
                action=p.get("action"),
                conditions=p.get("conditions", {}),
                created_at=p.get("created_at", datetime.utcnow()),
                updated_at=p.get("updated_at", datetime.utcnow())
            )
            for p in permissions
        ]
    
    async def revoke_permission_from_role(self, role_id: UUID, permission_id: UUID) -> bool:
        """Revoke permission from role."""
        success = await self.entity_client.revoke_permission_from_role(role_id, permission_id)
        
        if success:
            # Clear cache
            self.cache.delete_role(str(role_id))
            self.cache.clear_all()
            logger.info(f"Revoked permission {permission_id} from role {role_id}")
        
        return success


# Global service instance
_service: Optional[AssignmentService] = None


def get_assignment_service() -> AssignmentService:
    """Get global assignment service instance."""
    global _service
    if _service is None:
        _service = AssignmentService()
    return _service
