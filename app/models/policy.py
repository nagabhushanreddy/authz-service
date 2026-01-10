"""
Policy models for authorization service.
"""

from typing import Optional, List, Dict, Any
from datetime import datetime
from pydantic import BaseModel, Field, UUID4
from enum import Enum


class PolicyType(str, Enum):
    """Policy types."""
    RBAC = "rbac"
    ABAC = "abac"
    OWNERSHIP = "ownership"


class RuleEffect(str, Enum):
    """Rule effects."""
    ALLOW = "allow"
    DENY = "deny"


class Rule(BaseModel):
    """Policy rule model."""
    effect: RuleEffect = Field(..., description="Rule effect (allow or deny)")
    conditions: Dict[str, Any] = Field(..., description="Rule evaluation conditions")
    priority: int = Field(..., ge=0, le=1000, description="Rule priority (0-1000)")

    class Config:
        json_schema_extra = {
            "example": {
                "effect": "allow",
                "conditions": {
                    "resource_type": "loan",
                    "action": "read",
                    "role": "loan_officer"
                },
                "priority": 100
            }
        }


class PolicyBase(BaseModel):
    """Base policy model."""
    name: str = Field(..., min_length=3, max_length=100, description="Policy name")
    description: Optional[str] = Field(None, max_length=1000, description="Policy description")
    tenant_id: UUID4 = Field(..., description="Tenant ID")
    policy_type: PolicyType = Field(..., description="Policy type")
    rules: List[Rule] = Field(..., min_length=1, description="Policy rules")
    active: bool = Field(True, description="Whether policy is active")
    version: str = Field(..., description="Policy version (semantic versioning)")


class PolicyCreate(PolicyBase):
    """Policy creation model."""

    class Config:
        json_schema_extra = {
            "example": {
                "name": "loan_officer_policy",
                "description": "Policy for loan officers",
                "tenant_id": "123e4567-e89b-12d3-a456-426614174000",
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
        }


class PolicyUpdate(BaseModel):
    """Policy update model."""
    name: Optional[str] = Field(None, min_length=3, max_length=100, description="Policy name")
    description: Optional[str] = Field(None, max_length=1000, description="Policy description")
    rules: Optional[List[Rule]] = Field(None, min_length=1, description="Policy rules")
    active: Optional[bool] = Field(None, description="Whether policy is active")

    class Config:
        json_schema_extra = {
            "example": {
                "description": "Updated policy for senior loan officers",
                "rules": [
                    {
                        "effect": "allow",
                        "conditions": {
                            "resource_type": "loan",
                            "action": "read"
                        },
                        "priority": 100
                    },
                    {
                        "effect": "allow",
                        "conditions": {
                            "resource_type": "loan",
                            "action": "update"
                        },
                        "priority": 90
                    }
                ],
                "active": True
            }
        }


class PolicyResponse(PolicyBase):
    """Policy response model."""
    policy_id: UUID4 = Field(..., description="Policy ID")
    created_at: datetime = Field(..., description="Creation timestamp")
    updated_at: datetime = Field(..., description="Last update timestamp")

    class Config:
        json_schema_extra = {
            "example": {
                "policy_id": "123e4567-e89b-12d3-a456-426614174000",
                "name": "loan_officer_policy",
                "description": "Policy for loan officers",
                "tenant_id": "123e4567-e89b-12d3-a456-426614174000",
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
        }


class PaginationMetadata(BaseModel):
    """Pagination metadata."""
    total: int = Field(..., description="Total number of items")
    page: int = Field(..., description="Current page number")
    page_size: int = Field(..., description="Items per page")
    total_pages: int = Field(..., description="Total number of pages")


class PolicyListResponse(BaseModel):
    """Policy list response model."""
    policies: List[PolicyResponse] = Field(..., description="List of policies")
    pagination: PaginationMetadata = Field(..., description="Pagination metadata")

    class Config:
        json_schema_extra = {
            "example": {
                "policies": [
                    {
                        "policy_id": "123e4567-e89b-12d3-a456-426614174000",
                        "name": "loan_officer_policy",
                        "description": "Policy for loan officers",
                        "tenant_id": "123e4567-e89b-12d3-a456-426614174000",
                        "policy_type": "rbac",
                        "rules": [],
                        "active": True,
                        "version": "1.0.0",
                        "created_at": "2026-01-10T10:30:00Z",
                        "updated_at": "2026-01-10T10:30:00Z"
                    }
                ],
                "pagination": {
                    "total": 1,
                    "page": 1,
                    "page_size": 50,
                    "total_pages": 1
                }
            }
        }
