"""
Decision service for policy evaluation and authorization decisions.
"""

import logging
import hashlib
from typing import Dict, Any, List, Optional
from uuid import UUID
from datetime import datetime

from app.models.request import AuthorizationRequest
from app.models.response import DecisionType, AuthorizationResponse, ResponseMetadata
from app.cache import get_cache
from app.services.rbac_service import get_rbac_service
from app.services.abac_service import get_abac_service
from app.services.ownership_service import get_ownership_service
from app.middleware import get_correlation_id

logger = logging.getLogger(__name__)


class DecisionService:
    """Service for authorization decision evaluation."""
    
    def __init__(self):
        """Initialize decision service."""
        self.cache = get_cache()
        self.rbac_service = get_rbac_service()
        self.abac_service = get_abac_service()
        self.ownership_service = get_ownership_service()
        self.policy_version = "1.0.0"  # Should be loaded from config/policy store
    
    async def check_authorization(self, request: AuthorizationRequest) -> AuthorizationResponse:
        """Check authorization for a request.
        
        Args:
            request: Authorization request
            
        Returns:
            Authorization response with decision
        """
        # Generate decision cache key
        decision_key = self._generate_decision_key(request)
        
        # Check decision cache
        cached_decision = self.cache.get_decision(decision_key)
        if cached_decision:
            logger.debug(f"Cache hit for decision: {decision_key}")
            return AuthorizationResponse(**cached_decision)
        
        # Evaluate authorization
        decision, reason_codes, evaluated_policies = await self._evaluate(request)
        
        # Create response
        response = AuthorizationResponse(
            decision=decision,
            reason_codes=reason_codes,
            policy_version=self.policy_version,
            evaluated_policies=evaluated_policies,
            metadata=ResponseMetadata(
                timestamp=datetime.utcnow(),
                correlation_id=get_correlation_id() or None
            )
        )
        
        # Cache decision
        self.cache.set_decision(decision_key, response.model_dump())
        
        # Log decision for audit
        logger.info(
            f"Authorization decision: user={request.user_id}, "
            f"resource={request.resource}, action={request.action}, "
            f"decision={decision.value}, reasons={reason_codes}"
        )
        
        return response
    
    async def _evaluate(self, request: AuthorizationRequest) -> tuple[DecisionType, List[str], List[str]]:
        """Evaluate authorization request using policy engine.
        
        Args:
            request: Authorization request
            
        Returns:
            Tuple of (decision, reason_codes, evaluated_policy_ids)
        """
        reason_codes = []
        evaluated_policies = []
        
        # Extract resource type and action
        resource_parts = request.resource.split(":")
        resource_type = resource_parts[0] if resource_parts else request.resource
        action = request.action.value
        
        # Get context
        context = request.context.model_dump() if request.context else {}
        tenant_id = context.get("tenant_id")
        resource_owner_id = context.get("resource_owner_id")
        
        # Step 1: Evaluate RBAC (Role-Based Access Control)
        has_rbac_permission, rbac_reasons = await self.rbac_service.has_permission(
            request.user_id,
            resource_type,
            action,
            UUID(tenant_id) if tenant_id else None
        )
        
        reason_codes.extend(rbac_reasons)
        evaluated_policies.append("rbac_policy")
        
        if not has_rbac_permission:
            # No RBAC permission, deny by default
            return DecisionType.DENY, reason_codes or ["DEFAULT_DENY"], evaluated_policies
        
        # Step 2: Evaluate ABAC (Attribute-Based Access Control)
        # Get permission conditions from user roles and evaluate against context
        abac_result, abac_reasons = self.abac_service.evaluate_conditions({}, context)
        reason_codes.extend(abac_reasons)
        evaluated_policies.append("abac_policy")
        
        if not abac_result:
            return DecisionType.DENY, reason_codes, evaluated_policies
        
        # Step 3: Evaluate Ownership
        if self.ownership_service.applies_to_action(action):
            if resource_owner_id:
                is_owner, owner_reasons = self.ownership_service.check_ownership(
                    request.user_id,
                    UUID(resource_owner_id) if resource_owner_id else None,
                    action
                )
                reason_codes.extend(owner_reasons)
                evaluated_policies.append("ownership_policy")
                
                if not is_owner and not has_rbac_permission:
                    # Not owner and no special permission
                    return DecisionType.DENY, reason_codes, evaluated_policies
        
        # All checks passed, allow access
        return DecisionType.ALLOW, reason_codes or ["ALLOW"], evaluated_policies
    
    def _generate_decision_key(self, request: AuthorizationRequest) -> str:
        """Generate cache key for decision.
        
        Args:
            request: Authorization request
            
        Returns:
            Cache key string
        """
        # Include relevant parts in key
        context = request.context.model_dump() if request.context else {}
        tenant_id = context.get("tenant_id", "")
        
        key_parts = [
            str(request.user_id),
            request.resource,
            request.action.value,
            str(tenant_id)
        ]
        
        key_string = ":".join(key_parts)
        # Hash for shorter keys
        return hashlib.md5(key_string.encode()).hexdigest()


# Global service instance
_service: Optional[DecisionService] = None


def get_decision_service() -> DecisionService:
    """Get global decision service instance."""
    global _service
    if _service is None:
        _service = DecisionService()
    return _service
