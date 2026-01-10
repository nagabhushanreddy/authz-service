"""
Entity service client for CRUD operations.
"""

import httpx
import logging
from typing import Optional, Dict, Any, List
from uuid import UUID

logger = logging.getLogger(__name__)


class EntityServiceError(Exception):
    """Entity service error."""
    pass


class EntityServiceClient:
    """Client for entity-service communication."""
    
    def __init__(self, base_url: str, timeout: float = 5.0, retry_attempts: int = 3):
        """Initialize entity service client.
        
        Args:
            base_url: Base URL of entity service
            timeout: Request timeout in seconds
            retry_attempts: Number of retry attempts
        """
        self.base_url = base_url.rstrip('/')
        self.timeout = timeout
        self.retry_attempts = retry_attempts
        self.client = httpx.AsyncClient(timeout=timeout)
    
    async def close(self):
        """Close HTTP client."""
        await self.client.aclose()
    
    async def _request(self, method: str, endpoint: str, **kwargs) -> Dict[str, Any]:
        """Make HTTP request with retry logic.
        
        Args:
            method: HTTP method
            endpoint: API endpoint
            **kwargs: Additional request parameters
            
        Returns:
            Response data
            
        Raises:
            EntityServiceError: If request fails
        """
        url = f"{self.base_url}/{endpoint.lstrip('/')}"
        
        for attempt in range(self.retry_attempts):
            try:
                response = await self.client.request(method, url, **kwargs)
                response.raise_for_status()
                return response.json()
            except httpx.HTTPStatusError as e:
                if attempt == self.retry_attempts - 1:
                    logger.error(f"Entity service request failed: {e}")
                    raise EntityServiceError(f"Entity service error: {e.response.status_code}")
                logger.warning(f"Retry {attempt + 1}/{self.retry_attempts} for {url}")
            except Exception as e:
                if attempt == self.retry_attempts - 1:
                    logger.error(f"Entity service request failed: {e}")
                    raise EntityServiceError(f"Entity service error: {str(e)}")
                logger.warning(f"Retry {attempt + 1}/{self.retry_attempts} for {url}")
        
        raise EntityServiceError("Max retries exceeded")
    
    # Role operations
    async def create_role(self, role_data: Dict[str, Any]) -> Dict[str, Any]:
        """Create role in entity service."""
        return await self._request("POST", "/api/v1/entities/roles", json=role_data)
    
    async def get_role(self, role_id: UUID) -> Optional[Dict[str, Any]]:
        """Get role from entity service."""
        try:
            return await self._request("GET", f"/api/v1/entities/roles/{role_id}")
        except EntityServiceError:
            return None
    
    async def list_roles(self, tenant_id: Optional[UUID] = None, 
                        page: int = 1, page_size: int = 50) -> Dict[str, Any]:
        """List roles from entity service."""
        params = {"page": page, "page_size": page_size}
        if tenant_id:
            params["tenant_id"] = str(tenant_id)
        return await self._request("GET", "/api/v1/entities/roles", params=params)
    
    async def update_role(self, role_id: UUID, role_data: Dict[str, Any]) -> Dict[str, Any]:
        """Update role in entity service."""
        return await self._request("PATCH", f"/api/v1/entities/roles/{role_id}", json=role_data)
    
    async def delete_role(self, role_id: UUID) -> bool:
        """Delete role from entity service."""
        try:
            await self._request("DELETE", f"/api/v1/entities/roles/{role_id}")
            return True
        except EntityServiceError:
            return False
    
    # Permission operations
    async def create_permission(self, permission_data: Dict[str, Any]) -> Dict[str, Any]:
        """Create permission in entity service."""
        return await self._request("POST", "/api/v1/entities/permissions", json=permission_data)
    
    async def get_permission(self, permission_id: UUID) -> Optional[Dict[str, Any]]:
        """Get permission from entity service."""
        try:
            return await self._request("GET", f"/api/v1/entities/permissions/{permission_id}")
        except EntityServiceError:
            return None
    
    async def list_permissions(self, resource_type: Optional[str] = None, 
                              action: Optional[str] = None,
                              page: int = 1, page_size: int = 50) -> Dict[str, Any]:
        """List permissions from entity service."""
        params = {"page": page, "page_size": page_size}
        if resource_type:
            params["resource_type"] = resource_type
        if action:
            params["action"] = action
        return await self._request("GET", "/api/v1/entities/permissions", params=params)
    
    async def update_permission(self, permission_id: UUID, permission_data: Dict[str, Any]) -> Dict[str, Any]:
        """Update permission in entity service."""
        return await self._request("PATCH", f"/api/v1/entities/permissions/{permission_id}", 
                                  json=permission_data)
    
    async def delete_permission(self, permission_id: UUID) -> bool:
        """Delete permission from entity service."""
        try:
            await self._request("DELETE", f"/api/v1/entities/permissions/{permission_id}")
            return True
        except EntityServiceError:
            return False
    
    # Policy operations
    async def create_policy(self, policy_data: Dict[str, Any]) -> Dict[str, Any]:
        """Create policy in entity service."""
        return await self._request("POST", "/api/v1/entities/policies", json=policy_data)
    
    async def get_policy(self, policy_id: UUID) -> Optional[Dict[str, Any]]:
        """Get policy from entity service."""
        try:
            return await self._request("GET", f"/api/v1/entities/policies/{policy_id}")
        except EntityServiceError:
            return None
    
    async def list_policies(self, tenant_id: Optional[UUID] = None, 
                           policy_type: Optional[str] = None,
                           active: Optional[bool] = None,
                           page: int = 1, page_size: int = 50) -> Dict[str, Any]:
        """List policies from entity service."""
        params = {"page": page, "page_size": page_size}
        if tenant_id:
            params["tenant_id"] = str(tenant_id)
        if policy_type:
            params["policy_type"] = policy_type
        if active is not None:
            params["active"] = active
        return await self._request("GET", "/api/v1/entities/policies", params=params)
    
    async def update_policy(self, policy_id: UUID, policy_data: Dict[str, Any]) -> Dict[str, Any]:
        """Update policy in entity service."""
        return await self._request("PATCH", f"/api/v1/entities/policies/{policy_id}", 
                                  json=policy_data)
    
    async def delete_policy(self, policy_id: UUID) -> bool:
        """Delete policy from entity service."""
        try:
            await self._request("DELETE", f"/api/v1/entities/policies/{policy_id}")
            return True
        except EntityServiceError:
            return False
    
    # Assignment operations
    async def assign_role_to_user(self, user_id: UUID, assignment_data: Dict[str, Any]) -> Dict[str, Any]:
        """Assign role to user."""
        return await self._request("POST", f"/api/v1/entities/users/{user_id}/roles", 
                                  json=assignment_data)
    
    async def get_user_roles(self, user_id: UUID, tenant_id: Optional[UUID] = None, 
                            active_only: bool = True) -> List[Dict[str, Any]]:
        """Get user roles."""
        params = {"active_only": active_only}
        if tenant_id:
            params["tenant_id"] = str(tenant_id)
        try:
            response = await self._request("GET", f"/api/v1/entities/users/{user_id}/roles", 
                                         params=params)
            return response.get("roles", [])
        except EntityServiceError:
            return []
    
    async def revoke_role_from_user(self, user_id: UUID, role_id: UUID) -> bool:
        """Revoke role from user."""
        try:
            await self._request("DELETE", f"/api/v1/entities/users/{user_id}/roles/{role_id}")
            return True
        except EntityServiceError:
            return False
    
    async def assign_permission_to_role(self, role_id: UUID, assignment_data: Dict[str, Any]) -> Dict[str, Any]:
        """Assign permission to role."""
        return await self._request("POST", f"/api/v1/entities/roles/{role_id}/permissions", 
                                  json=assignment_data)
    
    async def get_role_permissions(self, role_id: UUID) -> List[Dict[str, Any]]:
        """Get role permissions."""
        try:
            response = await self._request("GET", f"/api/v1/entities/roles/{role_id}/permissions")
            return response.get("permissions", [])
        except EntityServiceError:
            return []
    
    async def revoke_permission_from_role(self, role_id: UUID, permission_id: UUID) -> bool:
        """Revoke permission from role."""
        try:
            await self._request("DELETE", 
                              f"/api/v1/entities/roles/{role_id}/permissions/{permission_id}")
            return True
        except EntityServiceError:
            return False


# Global client instance
_client: Optional[EntityServiceClient] = None


def get_entity_client() -> EntityServiceClient:
    """Get global entity service client instance."""
    global _client
    if _client is None:
        from app.config import get_config
        config = get_config()
        _client = EntityServiceClient(
            base_url=config.entity_service.base_url,
            timeout=config.entity_service.timeout,
            retry_attempts=config.entity_service.retry_attempts
        )
    return _client
