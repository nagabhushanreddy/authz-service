"""
Policy service for policy management operations.
"""

import logging
from typing import Optional, Dict, Any
from uuid import UUID
from datetime import datetime

from app.clients import get_entity_client
from app.cache import get_cache
from app.models.policy import PolicyCreate, PolicyUpdate, PolicyResponse, PolicyListResponse, PaginationMetadata

logger = logging.getLogger(__name__)


class PolicyService:
    """Service for policy management."""
    
    def __init__(self):
        """Initialize policy service."""
        self.entity_client = get_entity_client()
        self.cache = get_cache()
    
    async def create_policy(self, policy_data: PolicyCreate) -> PolicyResponse:
        """Create a new policy."""
        policy_dict = policy_data.model_dump()
        result = await self.entity_client.create_policy(policy_dict)
        
        # Clear cache for tenant
        self.cache.clear_tenant(str(policy_data.tenant_id))
        
        logger.info(f"Created policy: {result.get('policy_id')}")
        
        return self._to_policy_response(result)
    
    async def get_policy(self, policy_id: UUID) -> Optional[PolicyResponse]:
        """Get policy by ID."""
        # Check cache
        cached_policy = self.cache.get_policy(str(policy_id))
        if cached_policy:
            return PolicyResponse(**cached_policy)
        
        # Fetch from entity service
        policy_dict = await self.entity_client.get_policy(policy_id)
        if not policy_dict:
            return None
        
        # Cache result
        self.cache.set_policy(str(policy_id), policy_dict)
        
        return self._to_policy_response(policy_dict)
    
    async def list_policies(self, tenant_id: Optional[UUID] = None, 
                           policy_type: Optional[str] = None,
                           active: Optional[bool] = None,
                           page: int = 1, page_size: int = 50) -> PolicyListResponse:
        """List policies with pagination."""
        result = await self.entity_client.list_policies(tenant_id, policy_type, active, page, page_size)
        
        policies = [self._to_policy_response(p) for p in result.get("policies", [])]
        pagination_data = result.get("pagination", {})
        
        return PolicyListResponse(
            policies=policies,
            pagination=PaginationMetadata(**pagination_data) if pagination_data else PaginationMetadata(
                total=len(policies),
                page=page,
                page_size=page_size,
                total_pages=1
            )
        )
    
    async def update_policy(self, policy_id: UUID, policy_data: PolicyUpdate) -> PolicyResponse:
        """Update policy."""
        policy_dict = policy_data.model_dump(exclude_unset=True)
        result = await self.entity_client.update_policy(policy_id, policy_dict)
        
        # Clear cache
        self.cache.delete_policy(str(policy_id))
        tenant_id = result.get("tenant_id")
        if tenant_id:
            self.cache.clear_tenant(tenant_id)
        
        logger.info(f"Updated policy: {policy_id}")
        
        return self._to_policy_response(result)
    
    async def delete_policy(self, policy_id: UUID) -> bool:
        """Delete policy."""
        # Get policy first to get tenant_id for cache clearing
        policy = await self.get_policy(policy_id)
        
        # Delete from entity service
        success = await self.entity_client.delete_policy(policy_id)
        
        if success:
            # Clear cache
            self.cache.delete_policy(str(policy_id))
            if policy:
                self.cache.clear_tenant(str(policy.tenant_id))
            logger.info(f"Deleted policy: {policy_id}")
        
        return success
    
    def _to_policy_response(self, policy_dict: Dict[str, Any]) -> PolicyResponse:
        """Convert policy dict to response model."""
        return PolicyResponse(
            policy_id=policy_dict.get("policy_id"),
            name=policy_dict.get("name"),
            description=policy_dict.get("description"),
            tenant_id=policy_dict.get("tenant_id"),
            policy_type=policy_dict.get("policy_type"),
            rules=policy_dict.get("rules", []),
            active=policy_dict.get("active", True),
            version=policy_dict.get("version"),
            created_at=policy_dict.get("created_at", datetime.utcnow()),
            updated_at=policy_dict.get("updated_at", datetime.utcnow())
        )


# Global service instance
_service: Optional[PolicyService] = None


def get_policy_service() -> PolicyService:
    """Get global policy service instance."""
    global _service
    if _service is None:
        _service = PolicyService()
    return _service
