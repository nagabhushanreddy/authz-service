"""
RBAC service for role-based access control.
"""

import logging
from typing import List, Dict, Any, Optional
from uuid import UUID
from app.cache import get_cache
from app.clients import get_entity_client

logger = logging.getLogger(__name__)


class RBACService:
    """Service for RBAC evaluation."""
    
    def __init__(self):
        """Initialize RBAC service."""
        self.cache = get_cache()
        self.entity_client = get_entity_client()
    
    async def get_user_roles(self, user_id: UUID, tenant_id: Optional[UUID] = None) -> List[Dict[str, Any]]:
        """Get all roles for a user.
        
        Args:
            user_id: User ID
            tenant_id: Optional tenant ID for filtering
            
        Returns:
            List of role objects with permissions
        """
        # Check cache first
        cache_key = f"{user_id}:{tenant_id or 'all'}"
        cached_roles = self.cache.get_user_roles(str(user_id), str(tenant_id) if tenant_id else "all")
        if cached_roles is not None:
            logger.debug(f"Cache hit for user roles: {user_id}")
            return cached_roles
        
        # Fetch from entity service
        try:
            roles = await self.entity_client.get_user_roles(user_id, tenant_id, active_only=True)
            
            # Enrich roles with permissions
            enriched_roles = []
            for role in roles:
                role_id = role.get("role_id")
                if role_id:
                    permissions = await self.entity_client.get_role_permissions(UUID(role_id))
                    role["permissions"] = permissions
                enriched_roles.append(role)
            
            # Cache the result
            self.cache.set_user_roles(str(user_id), str(tenant_id) if tenant_id else "all", enriched_roles)
            
            return enriched_roles
        except Exception as e:
            logger.error(f"Failed to fetch user roles: {e}")
            return []
    
    async def has_permission(self, user_id: UUID, resource_type: str, action: str, 
                            tenant_id: Optional[UUID] = None) -> tuple[bool, List[str]]:
        """Check if user has permission via RBAC.
        
        Args:
            user_id: User ID
            resource_type: Resource type
            action: Action
            tenant_id: Optional tenant ID
            
        Returns:
            Tuple of (has_permission, reason_codes)
        """
        roles = await self.get_user_roles(user_id, tenant_id)
        
        if not roles:
            return False, ["NO_ROLES"]
        
        # Check if any role has the required permission
        for role in roles:
            permissions = role.get("permissions", [])
            for perm in permissions:
                if perm.get("resource_type") == resource_type and perm.get("action") == action:
                    logger.info(f"RBAC match: user={user_id}, role={role.get('name')}, "
                              f"permission={perm.get('name')}")
                    return True, ["RBAC_MATCH", f"ROLE_{role.get('name', 'UNKNOWN').upper()}"]
        
        return False, ["NO_PERMISSION"]


# Global service instance
_service: Optional[RBACService] = None


def get_rbac_service() -> RBACService:
    """Get global RBAC service instance."""
    global _service
    if _service is None:
        _service = RBACService()
    return _service
