"""
Assignment models for authorization service.
"""

from typing import Optional
from datetime import datetime
from pydantic import BaseModel, Field, UUID4, ConfigDict


class UserRoleAssignmentCreate(BaseModel):
    """User role assignment creation model."""
    role_id: UUID4 = Field(..., description="Role ID")
    tenant_id: UUID4 = Field(..., description="Tenant ID")
    valid_from: Optional[datetime] = Field(None, description="Valid from timestamp")
    valid_until: Optional[datetime] = Field(None, description="Valid until timestamp")

    model_config = ConfigDict(
        json_schema_extra={

            "example": {
                "role_id": "123e4567-e89b-12d3-a456-426614174000",
                "tenant_id": "123e4567-e89b-12d3-a456-426614174000",
                "valid_from": "2026-01-10T00:00:00Z",
                "valid_until": "2027-01-10T00:00:00Z"
            }
        })


class UserRoleAssignmentResponse(BaseModel):
    """User role assignment response model."""
    assignment_id: UUID4 = Field(..., description="Assignment ID")
    user_id: UUID4 = Field(..., description="User ID")
    role_id: UUID4 = Field(..., description="Role ID")
    tenant_id: UUID4 = Field(..., description="Tenant ID")
    valid_from: Optional[datetime] = Field(None, description="Valid from timestamp")
    valid_until: Optional[datetime] = Field(None, description="Valid until timestamp")
    created_at: datetime = Field(..., description="Creation timestamp")

    model_config = ConfigDict(
        json_schema_extra={

            "example": {
                "assignment_id": "123e4567-e89b-12d3-a456-426614174000",
                "user_id": "123e4567-e89b-12d3-a456-426614174001",
                "role_id": "123e4567-e89b-12d3-a456-426614174002",
                "tenant_id": "123e4567-e89b-12d3-a456-426614174000",
                "valid_from": "2026-01-10T00:00:00Z",
                "valid_until": "2027-01-10T00:00:00Z",
                "created_at": "2026-01-10T10:30:00Z"
            }
        })


class RolePermissionAssignmentCreate(BaseModel):
    """Role permission assignment creation model."""
    permission_id: UUID4 = Field(..., description="Permission ID")

    model_config = ConfigDict(
        json_schema_extra={

            "example": {
                "permission_id": "123e4567-e89b-12d3-a456-426614174000"
            }
        })


class RolePermissionAssignmentResponse(BaseModel):
    """Role permission assignment response model."""
    assignment_id: UUID4 = Field(..., description="Assignment ID")
    role_id: UUID4 = Field(..., description="Role ID")
    permission_id: UUID4 = Field(..., description="Permission ID")
    created_at: datetime = Field(..., description="Creation timestamp")

    model_config = ConfigDict(
        json_schema_extra={

            "example": {
                "assignment_id": "123e4567-e89b-12d3-a456-426614174000",
                "role_id": "123e4567-e89b-12d3-a456-426614174001",
                "permission_id": "123e4567-e89b-12d3-a456-426614174002",
                "created_at": "2026-01-10T10:30:00Z"
            }
        })
