"""
Tests for decision service.
"""

import pytest
from uuid import uuid4

from app.services.decision_service import DecisionService
from app.models.request import AuthorizationRequest, AuthorizationContext, ActionType
from app.models.response import DecisionType


@pytest.mark.unit
def test_decision_service_initialization():
    """Test decision service initialization."""
    service = DecisionService()
    assert service is not None
    assert service.policy_version == "1.0.0"


@pytest.mark.unit
def test_generate_decision_key():
    """Test decision cache key generation."""
    service = DecisionService()
    
    user_id = uuid4()
    tenant_id = uuid4()
    
    request = AuthorizationRequest(
        user_id=user_id,
        resource="loan:12345",
        action=ActionType.READ,
        context=AuthorizationContext(tenant_id=tenant_id)
    )
    
    key1 = service._generate_decision_key(request)
    key2 = service._generate_decision_key(request)
    
    # Same request should generate same key
    assert key1 == key2
    assert len(key1) == 32  # MD5 hash length


@pytest.mark.unit
def test_generate_decision_key_different_requests():
    """Test that different requests generate different keys."""
    service = DecisionService()
    
    user_id = uuid4()
    tenant_id = uuid4()
    
    request1 = AuthorizationRequest(
        user_id=user_id,
        resource="loan:12345",
        action=ActionType.READ,
        context=AuthorizationContext(tenant_id=tenant_id)
    )
    
    request2 = AuthorizationRequest(
        user_id=user_id,
        resource="loan:12345",
        action=ActionType.UPDATE,  # Different action
        context=AuthorizationContext(tenant_id=tenant_id)
    )
    
    key1 = service._generate_decision_key(request1)
    key2 = service._generate_decision_key(request2)
    
    # Different actions should generate different keys
    assert key1 != key2


@pytest.mark.asyncio
async def test_check_authorization_no_roles():
    """Test authorization check when user has no roles (should DENY)."""
    service = DecisionService()
    
    request = AuthorizationRequest(
        user_id=uuid4(),
        resource="loan:12345",
        action=ActionType.READ,
        context=AuthorizationContext()
    )
    
    # Since entity service is not running, user will have no roles
    response = await service.check_authorization(request)
    
    assert response.decision == DecisionType.DENY
    assert "NO_ROLES" in response.reason_codes or "DEFAULT_DENY" in response.reason_codes
    assert response.policy_version == "1.0.0"
    assert response.metadata is not None


@pytest.mark.asyncio
async def test_check_authorization_caching():
    """Test that authorization decisions are cached."""
    service = DecisionService()
    
    request = AuthorizationRequest(
        user_id=uuid4(),
        resource="loan:12345",
        action=ActionType.READ,
        context=AuthorizationContext()
    )
    
    # First call - not cached
    response1 = await service.check_authorization(request)
    
    # Second call - should be cached
    response2 = await service.check_authorization(request)
    
    # Both responses should have same decision
    assert response1.decision == response2.decision
    assert response1.reason_codes == response2.reason_codes
