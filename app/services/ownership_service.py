"""
Ownership service for resource ownership validation.
"""

import logging
from typing import Optional, List
from uuid import UUID

logger = logging.getLogger(__name__)


class OwnershipService:
    """Service for ownership-based access control."""
    
    def __init__(self):
        """Initialize ownership service."""
        pass
    
    def check_ownership(self, user_id: UUID, resource_owner_id: Optional[UUID], 
                       action: str) -> tuple[bool, List[str]]:
        """Check if user owns the resource.
        
        Args:
            user_id: User ID requesting access
            resource_owner_id: ID of resource owner from context
            action: Action being performed
            
        Returns:
            Tuple of (is_owner, reason_codes)
        """
        if resource_owner_id is None:
            # No ownership information available
            return False, ["NO_OWNER_INFO"]
        
        if str(user_id) == str(resource_owner_id):
            logger.info(f"Ownership match: user={user_id} owns resource")
            return True, ["OWNER_ACCESS", f"OWNER_ACTION_{action.upper()}"]
        
        return False, ["NOT_OWNER"]
    
    def applies_to_action(self, action: str) -> bool:
        """Check if ownership rules apply to this action.
        
        Args:
            action: Action being performed
            
        Returns:
            True if ownership rules should be evaluated
        """
        # Ownership typically applies to read, update, delete
        # but not to create or execute (which are done on types, not instances)
        return action.lower() in ["read", "update", "delete"]


# Global service instance
_service: Optional[OwnershipService] = None


def get_ownership_service() -> OwnershipService:
    """Get global ownership service instance."""
    global _service
    if _service is None:
        _service = OwnershipService()
    return _service
