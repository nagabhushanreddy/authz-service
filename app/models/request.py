"""
Request models for authorization checks.
"""

from typing import Optional, Dict, Any, List
from datetime import datetime
from pydantic import BaseModel, Field, UUID4
from enum import Enum


class ActionType(str, Enum):
    """Supported action types."""
    CREATE = "create"
    READ = "read"
    UPDATE = "update"
    DELETE = "delete"
    EXECUTE = "execute"


class AuthorizationContext(BaseModel):
    """Context for authorization decisions."""
    tenant_id: Optional[UUID4] = Field(None, description="Tenant ID for multi-tenant isolation")
    resource_owner_id: Optional[UUID4] = Field(None, description="Resource owner ID for ownership checks")
    ip_address: Optional[str] = Field(None, description="IP address for IP-based rules")
    time: Optional[datetime] = Field(None, description="Time for time-based rules")
    attributes: Optional[Dict[str, Any]] = Field(default_factory=dict, description="Custom context attributes")

    class Config:
        json_schema_extra = {
            "example": {
                "tenant_id": "123e4567-e89b-12d3-a456-426614174000",
                "resource_owner_id": "123e4567-e89b-12d3-a456-426614174001",
                "ip_address": "192.168.1.1",
                "time": "2026-01-10T10:30:00Z",
                "attributes": {"department": "finance", "risk_level": "low"}
            }
        }


class AuthorizationRequest(BaseModel):
    """Request model for authorization check."""
    user_id: UUID4 = Field(..., description="User ID requesting authorization")
    resource: str = Field(..., min_length=1, max_length=200, description="Resource identifier")
    action: ActionType = Field(..., description="Action to perform")
    context: Optional[AuthorizationContext] = Field(default_factory=AuthorizationContext, description="Additional context")

    class Config:
        json_schema_extra = {
            "example": {
                "user_id": "123e4567-e89b-12d3-a456-426614174000",
                "resource": "loan:12345",
                "action": "read",
                "context": {
                    "tenant_id": "123e4567-e89b-12d3-a456-426614174000",
                    "resource_owner_id": "123e4567-e89b-12d3-a456-426614174001"
                }
            }
        }


class BatchAuthorizationRequest(BaseModel):
    """Request model for batch authorization checks."""
    checks: List[AuthorizationRequest] = Field(..., min_length=1, max_length=100, description="List of authorization checks")

    class Config:
        json_schema_extra = {
            "example": {
                "checks": [
                    {
                        "user_id": "123e4567-e89b-12d3-a456-426614174000",
                        "resource": "loan:12345",
                        "action": "read",
                        "context": {"tenant_id": "123e4567-e89b-12d3-a456-426614174000"}
                    },
                    {
                        "user_id": "123e4567-e89b-12d3-a456-426614174000",
                        "resource": "document:67890",
                        "action": "update",
                        "context": {"tenant_id": "123e4567-e89b-12d3-a456-426614174000"}
                    }
                ]
            }
        }
