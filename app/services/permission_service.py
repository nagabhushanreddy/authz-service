"""
Permission service for permission management operations.
"""

import logging
from typing import Optional, Dict, Any
from uuid import UUID
from datetime import datetime, timezone

from app.clients import get_entity_client
from app.cache import get_cache
from app.models.permission import PermissionCreate, PermissionUpdate, PermissionResponse, PermissionListResponse, PaginationMetadata

logger = logging.getLogger(__name__)


class PermissionService:
    """Service for permission management."""
    
    def __init__(self):
        """Initialize permission service."""
        self.entity_client = get_entity_client()
        self.cache = get_cache()
    
    async def create_permission(self, permission_data: PermissionCreate) -> PermissionResponse:
        """Create a new permission."""
        permission_dict = permission_data.model_dump()
        result = await self.entity_client.create_permission(permission_dict)
        
        # Clear cache
        self.cache.clear_all()
        
        logger.info(f"Created permission: {result.get('permission_id')}")
        
        return self._to_permission_response(result)
    
    async def get_permission(self, permission_id: UUID) -> Optional[PermissionResponse]:
        """Get permission by ID."""
        permission_dict = await self.entity_client.get_permission(permission_id)
        if not permission_dict:
            return None
        
        return self._to_permission_response(permission_dict)
    
    async def list_permissions(self, resource_type: Optional[str] = None, 
                              action: Optional[str] = None,
                              page: int = 1, page_size: int = 50) -> PermissionListResponse:
        """List permissions with pagination."""
        result = await self.entity_client.list_permissions(resource_type, action, page, page_size)
        
        permissions = [self._to_permission_response(p) for p in result.get("permissions", [])]
        pagination_data = result.get("pagination", {})
        
        return PermissionListResponse(
            permissions=permissions,
            pagination=PaginationMetadata(**pagination_data) if pagination_data else PaginationMetadata(
                total=len(permissions),
                page=page,
                page_size=page_size,
                total_pages=1
            )
        )
    
    async def update_permission(self, permission_id: UUID, permission_data: PermissionUpdate) -> PermissionResponse:
        """Update permission."""
        permission_dict = permission_data.model_dump(exclude_unset=True)
        result = await self.entity_client.update_permission(permission_id, permission_dict)
        
        # Clear cache
        self.cache.clear_all()
        
        logger.info(f"Updated permission: {permission_id}")
        
        return self._to_permission_response(result)
    
    async def delete_permission(self, permission_id: UUID) -> bool:
        """Delete permission."""
        success = await self.entity_client.delete_permission(permission_id)
        
        if success:
            # Clear cache
            self.cache.clear_all()
            logger.info(f"Deleted permission: {permission_id}")
        
        return success
    
    def _to_permission_response(self, permission_dict: Dict[str, Any]) -> PermissionResponse:
        """Convert permission dict to response model."""
        return PermissionResponse(
            permission_id=permission_dict.get("permission_id"),
            name=permission_dict.get("name"),
            description=permission_dict.get("description"),
            resource_type=permission_dict.get("resource_type"),
            action=permission_dict.get("action"),
            conditions=permission_dict.get("conditions", {}),
            created_at=permission_dict.get("created_at", datetime.now(timezone.utc)),
            updated_at=permission_dict.get("updated_at", datetime.now(timezone.utc))
        )


# Global service instance
_service: Optional[PermissionService] = None


def get_permission_service() -> PermissionService:
    """Get global permission service instance."""
    global _service
    if _service is None:
        _service = PermissionService()
    return _service
