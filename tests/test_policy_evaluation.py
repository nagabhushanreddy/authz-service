"""
Tests for policy evaluation logic.
"""

import pytest
from uuid import uuid4

from app.services.rbac_service import RBACService
from app.services.abac_service import ABACService
from app.services.ownership_service import OwnershipService


@pytest.mark.unit
def test_rbac_service_initialization():
    """Test RBAC service initialization."""
    service = RBACService()
    assert service is not None


@pytest.mark.asyncio
async def test_rbac_get_user_roles_no_roles():
    """Test getting user roles when user has none."""
    service = RBACService()
    
    user_id = uuid4()
    roles = await service.get_user_roles(user_id)
    
    # Entity service not running, should return empty list
    assert isinstance(roles, list)
    assert len(roles) == 0


@pytest.mark.asyncio
async def test_rbac_has_permission_no_roles():
    """Test permission check when user has no roles."""
    service = RBACService()
    
    user_id = uuid4()
    has_perm, reasons = await service.has_permission(user_id, "loan", "read")
    
    assert has_perm is False
    assert "NO_ROLES" in reasons


@pytest.mark.unit
def test_abac_service_initialization():
    """Test ABAC service initialization."""
    service = ABACService()
    assert service is not None


@pytest.mark.unit
def test_abac_evaluate_empty_conditions():
    """Test ABAC evaluation with empty conditions."""
    service = ABACService()
    
    matches, reasons = service.evaluate_conditions({}, {})
    
    assert matches is True
    assert isinstance(reasons, list)


@pytest.mark.unit
def test_abac_evaluate_simple_conditions():
    """Test ABAC evaluation with simple equality conditions."""
    service = ABACService()
    
    conditions = {"department": "finance", "level": "senior"}
    context = {"department": "finance", "level": "senior"}
    
    matches, reasons = service.evaluate_conditions(conditions, context)
    
    assert matches is True
    assert len(reasons) > 0


@pytest.mark.unit
def test_abac_evaluate_failed_conditions():
    """Test ABAC evaluation when conditions don't match."""
    service = ABACService()
    
    conditions = {"department": "finance"}
    context = {"department": "engineering"}
    
    matches, reasons = service.evaluate_conditions(conditions, context)
    
    assert matches is False
    assert any("FAILED" in r for r in reasons)


@pytest.mark.unit
def test_abac_evaluate_complex_condition_gt():
    """Test ABAC evaluation with greater than operator."""
    service = ABACService()
    
    result = service._evaluate_complex_condition(
        "amount",
        {"operator": "gt", "value": 1000},
        1500
    )
    
    assert result is True


@pytest.mark.unit
def test_abac_evaluate_complex_condition_in():
    """Test ABAC evaluation with 'in' operator."""
    service = ABACService()
    
    result = service._evaluate_complex_condition(
        "status",
        {"operator": "in", "value": ["active", "pending"]},
        "active"
    )
    
    assert result is True


@pytest.mark.unit
def test_ownership_service_initialization():
    """Test ownership service initialization."""
    service = OwnershipService()
    assert service is not None


@pytest.mark.unit
def test_ownership_check_is_owner():
    """Test ownership check when user is owner."""
    service = OwnershipService()
    
    user_id = uuid4()
    is_owner, reasons = service.check_ownership(user_id, user_id, "read")
    
    assert is_owner is True
    assert "OWNER_ACCESS" in reasons


@pytest.mark.unit
def test_ownership_check_not_owner():
    """Test ownership check when user is not owner."""
    service = OwnershipService()
    
    user_id = uuid4()
    owner_id = uuid4()
    
    is_owner, reasons = service.check_ownership(user_id, owner_id, "read")
    
    assert is_owner is False
    assert "NOT_OWNER" in reasons


@pytest.mark.unit
def test_ownership_check_no_owner_info():
    """Test ownership check with no owner information."""
    service = OwnershipService()
    
    user_id = uuid4()
    is_owner, reasons = service.check_ownership(user_id, None, "read")
    
    assert is_owner is False
    assert "NO_OWNER_INFO" in reasons


@pytest.mark.unit
def test_ownership_applies_to_action():
    """Test which actions ownership rules apply to."""
    service = OwnershipService()
    
    assert service.applies_to_action("read") is True
    assert service.applies_to_action("update") is True
    assert service.applies_to_action("delete") is True
    assert service.applies_to_action("create") is False
    assert service.applies_to_action("execute") is False
