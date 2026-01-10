"""
Role service for role management operations.
"""

import logging
from typing import Optional, List, Dict, Any
from uuid import UUID
from datetime import datetime

from app.clients import get_entity_client
from app.cache import get_cache
from app.models.role import RoleCreate, RoleUpdate, RoleResponse, RoleListResponse, PaginationMetadata, PermissionSummary

logger = logging.getLogger(__name__)


class RoleService:
    """Service for role management."""
    
    def __init__(self):
        """Initialize role service."""
        self.entity_client = get_entity_client()
        self.cache = get_cache()
    
    async def create_role(self, role_data: RoleCreate) -> RoleResponse:
        """Create a new role.
        
        Args:
            role_data: Role creation data
            
        Returns:
            Created role
        """
        # Create role in entity service
        role_dict = role_data.model_dump()
        result = await self.entity_client.create_role(role_dict)
        
        # Clear cache for tenant
        self.cache.clear_tenant(str(role_data.tenant_id))
        
        logger.info(f"Created role: {result.get('role_id')}")
        
        return self._to_role_response(result)
    
    async def get_role(self, role_id: UUID) -> Optional[RoleResponse]:
        """Get role by ID.
        
        Args:
            role_id: Role ID
            
        Returns:
            Role if found, None otherwise
        """
        # Check cache
        cached_role = self.cache.get_role(str(role_id))
        if cached_role:
            return RoleResponse(**cached_role)
        
        # Fetch from entity service
        role_dict = await self.entity_client.get_role(role_id)
        if not role_dict:
            return None
        
        # Get permissions
        permissions = await self.entity_client.get_role_permissions(role_id)
        role_dict["permissions"] = permissions
        
        # Cache result
        self.cache.set_role(str(role_id), role_dict)
        
        return self._to_role_response(role_dict)
    
    async def list_roles(self, tenant_id: Optional[UUID] = None, 
                        page: int = 1, page_size: int = 50) -> RoleListResponse:
        """List roles with pagination.
        
        Args:
            tenant_id: Optional tenant ID filter
            page: Page number
            page_size: Items per page
            
        Returns:
            List of roles with pagination
        """
        result = await self.entity_client.list_roles(tenant_id, page, page_size)
        
        roles = [self._to_role_response(r) for r in result.get("roles", [])]
        pagination_data = result.get("pagination", {})
        
        return RoleListResponse(
            roles=roles,
            pagination=PaginationMetadata(**pagination_data) if pagination_data else PaginationMetadata(
                total=len(roles),
                page=page,
                page_size=page_size,
                total_pages=1
            )
        )
    
    async def update_role(self, role_id: UUID, role_data: RoleUpdate) -> RoleResponse:
        """Update role.
        
        Args:
            role_id: Role ID
            role_data: Role update data
            
        Returns:
            Updated role
        """
        # Update in entity service
        role_dict = role_data.model_dump(exclude_unset=True)
        result = await self.entity_client.update_role(role_id, role_dict)
        
        # Clear cache
        self.cache.delete_role(str(role_id))
        tenant_id = result.get("tenant_id")
        if tenant_id:
            self.cache.clear_tenant(tenant_id)
        
        logger.info(f"Updated role: {role_id}")
        
        return self._to_role_response(result)
    
    async def delete_role(self, role_id: UUID) -> bool:
        """Delete role.
        
        Args:
            role_id: Role ID
            
        Returns:
            True if deleted, False otherwise
        """
        # Get role first to get tenant_id for cache clearing
        role = await self.get_role(role_id)
        
        # Delete from entity service
        success = await self.entity_client.delete_role(role_id)
        
        if success:
            # Clear cache
            self.cache.delete_role(str(role_id))
            if role:
                self.cache.clear_tenant(str(role.tenant_id))
            logger.info(f"Deleted role: {role_id}")
        
        return success
    
    def _to_role_response(self, role_dict: Dict[str, Any]) -> RoleResponse:
        """Convert role dict to response model."""
        # Convert permissions to summary format
        permissions = role_dict.get("permissions", [])
        permission_summaries = [
            PermissionSummary(
                permission_id=p.get("permission_id"),
                name=p.get("name"),
                resource_type=p.get("resource_type"),
                action=p.get("action")
            )
            for p in permissions
        ]
        
        return RoleResponse(
            role_id=role_dict.get("role_id"),
            name=role_dict.get("name"),
            description=role_dict.get("description"),
            tenant_id=role_dict.get("tenant_id"),
            permissions=permission_summaries,
            created_at=role_dict.get("created_at", datetime.utcnow()),
            updated_at=role_dict.get("updated_at", datetime.utcnow())
        )


# Global service instance
_service: Optional[RoleService] = None


def get_role_service() -> RoleService:
    """Get global role service instance."""
    global _service
    if _service is None:
        _service = RoleService()
    return _service
