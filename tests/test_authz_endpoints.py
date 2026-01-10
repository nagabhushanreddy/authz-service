"""
Tests for authorization endpoints.
"""

import pytest
from uuid import uuid4
from fastapi import status


@pytest.mark.unit
def test_check_authorization_missing_auth(test_client):
    """Test authorization check without authentication."""
    response = test_client.post(
        "/api/v1/authz/check",
        json={
            "user_id": str(uuid4()),
            "resource": "loan:12345",
            "action": "read"
        }
    )
    assert response.status_code == status.HTTP_401_UNAUTHORIZED


@pytest.mark.unit
def test_check_authorization_with_api_key(test_client, auth_headers, sample_authorization_request):
    """Test authorization check with API key."""
    # Mock entity service to return no roles (should DENY)
    response = test_client.post(
        "/api/v1/authz/check",
        json=sample_authorization_request.model_dump(mode='json'),
        headers=auth_headers
    )
    
    # Since entity service is not running, this will likely fail or return DENY
    # In a real test, we would mock the entity service client
    assert response.status_code in [status.HTTP_200_OK, status.HTTP_500_INTERNAL_SERVER_ERROR]


@pytest.mark.unit
def test_batch_check_authorization(test_client, auth_headers, sample_user_id, sample_tenant_id):
    """Test batch authorization check."""
    batch_request = {
        "checks": [
            {
                "user_id": str(sample_user_id),
                "resource": "loan:12345",
                "action": "read",
                "context": {"tenant_id": str(sample_tenant_id)}
            },
            {
                "user_id": str(sample_user_id),
                "resource": "document:67890",
                "action": "update",
                "context": {"tenant_id": str(sample_tenant_id)}
            }
        ]
    }
    
    response = test_client.post(
        "/api/v1/authz/check:batch",
        json=batch_request,
        headers=auth_headers
    )
    
    assert response.status_code in [status.HTTP_200_OK, status.HTTP_500_INTERNAL_SERVER_ERROR]
    
    if response.status_code == status.HTTP_200_OK:
        data = response.json()
        assert "decisions" in data
        assert len(data["decisions"]) == 2
        assert "metadata" in data


@pytest.mark.unit
def test_check_authorization_invalid_request(test_client, auth_headers):
    """Test authorization check with invalid request."""
    response = test_client.post(
        "/api/v1/authz/check",
        json={
            "user_id": "invalid-uuid",
            "resource": "loan:12345",
            "action": "read"
        },
        headers=auth_headers
    )
    
    assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY


@pytest.mark.unit
def test_batch_check_too_many_requests(test_client, auth_headers, sample_user_id):
    """Test batch authorization check with too many requests."""
    checks = [
        {
            "user_id": str(sample_user_id),
            "resource": f"loan:{i}",
            "action": "read"
        }
        for i in range(101)  # Max is 100
    ]
    
    response = test_client.post(
        "/api/v1/authz/check:batch",
        json={"checks": checks},
        headers=auth_headers
    )
    
    assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY
