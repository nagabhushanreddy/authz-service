"""
Pytest configuration and fixtures.
"""

import pytest
import asyncio
from typing import AsyncGenerator, Dict, Any
from uuid import uuid4
from httpx import AsyncClient
from fastapi.testclient import TestClient

from main import app
from app.config import get_config
from app.cache import get_cache
from app.models.request import AuthorizationRequest, AuthorizationContext, ActionType


@pytest.fixture(scope="session")
def event_loop():
    """Create event loop for async tests."""
    loop = asyncio.get_event_loop_policy().new_event_loop()
    yield loop
    loop.close()


@pytest.fixture
def test_config():
    """Get test configuration."""
    return get_config()


@pytest.fixture
def test_client():
    """Create test client."""
    return TestClient(app)


@pytest.fixture
async def async_client() -> AsyncGenerator[AsyncClient, None]:
    """Create async test client."""
    async with AsyncClient(app=app, base_url="http://test") as client:
        yield client


@pytest.fixture
def auth_headers(test_config) -> Dict[str, str]:
    """Create authentication headers with valid JWT."""
    # For testing, use API key authentication
    return {
        "X-API-Key": test_config.api.key,
        "X-Correlation-ID": str(uuid4())
    }


@pytest.fixture(autouse=True)
def clear_cache():
    """Clear cache before each test."""
    cache = get_cache()
    cache.clear_all()
    yield
    cache.clear_all()


@pytest.fixture
def sample_user_id():
    """Sample user ID for testing."""
    return uuid4()


@pytest.fixture
def sample_tenant_id():
    """Sample tenant ID for testing."""
    return uuid4()


@pytest.fixture
def sample_role_id():
    """Sample role ID for testing."""
    return uuid4()


@pytest.fixture
def sample_permission_id():
    """Sample permission ID for testing."""
    return uuid4()


@pytest.fixture
def sample_policy_id():
    """Sample policy ID for testing."""
    return uuid4()


@pytest.fixture
def sample_authorization_request(sample_user_id, sample_tenant_id):
    """Sample authorization request."""
    return AuthorizationRequest(
        user_id=sample_user_id,
        resource="loan:12345",
        action=ActionType.READ,
        context=AuthorizationContext(
            tenant_id=sample_tenant_id,
            resource_owner_id=sample_user_id
        )
    )


@pytest.fixture
def sample_role_data(sample_tenant_id):
    """Sample role creation data."""
    return {
        "name": "test_role",
        "description": "Test role",
        "tenant_id": str(sample_tenant_id),
        "permissions": []
    }


@pytest.fixture
def sample_permission_data():
    """Sample permission creation data."""
    return {
        "name": "loan:read",
        "description": "Read loan information",
        "resource_type": "loan",
        "action": "read",
        "conditions": {}
    }


@pytest.fixture
def sample_policy_data(sample_tenant_id):
    """Sample policy creation data."""
    return {
        "name": "test_policy",
        "description": "Test policy",
        "tenant_id": str(sample_tenant_id),
        "policy_type": "rbac",
        "rules": [
            {
                "effect": "allow",
                "conditions": {
                    "resource_type": "loan",
                    "action": "read"
                },
                "priority": 100
            }
        ],
        "active": True,
        "version": "1.0.0"
    }


# Mock entity service responses
@pytest.fixture
def mock_entity_service_role_response(sample_role_id, sample_tenant_id):
    """Mock entity service role response."""
    return {
        "role_id": str(sample_role_id),
        "name": "test_role",
        "description": "Test role",
        "tenant_id": str(sample_tenant_id),
        "permissions": [],
        "created_at": "2026-01-10T10:30:00Z",
        "updated_at": "2026-01-10T10:30:00Z"
    }


@pytest.fixture
def mock_entity_service_permission_response(sample_permission_id):
    """Mock entity service permission response."""
    return {
        "permission_id": str(sample_permission_id),
        "name": "loan:read",
        "description": "Read loan information",
        "resource_type": "loan",
        "action": "read",
        "conditions": {},
        "created_at": "2026-01-10T10:30:00Z",
        "updated_at": "2026-01-10T10:30:00Z"
    }


@pytest.fixture
def mock_entity_service_policy_response(sample_policy_id, sample_tenant_id):
    """Mock entity service policy response."""
    return {
        "policy_id": str(sample_policy_id),
        "name": "test_policy",
        "description": "Test policy",
        "tenant_id": str(sample_tenant_id),
        "policy_type": "rbac",
        "rules": [
            {
                "effect": "allow",
                "conditions": {"resource_type": "loan", "action": "read"},
                "priority": 100
            }
        ],
        "active": True,
        "version": "1.0.0",
        "created_at": "2026-01-10T10:30:00Z",
        "updated_at": "2026-01-10T10:30:00Z"
    }
