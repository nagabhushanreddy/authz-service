"""
Role models for authorization service.
"""

from typing import Optional, List
from datetime import datetime
from pydantic import BaseModel, Field, UUID4, ConfigDict


class PermissionSummary(BaseModel):
    """Summary of permission in role response."""
    permission_id: UUID4 = Field(..., description="Permission ID")
    name: str = Field(..., description="Permission name")
    resource_type: str = Field(..., description="Resource type")
    action: str = Field(..., description="Action")


class RoleBase(BaseModel):
    """Base role model."""
    name: str = Field(..., min_length=3, max_length=50, description="Role name")
    description: Optional[str] = Field(None, max_length=500, description="Role description")
    tenant_id: UUID4 = Field(..., description="Tenant ID")


class RoleCreate(RoleBase):
    """Role creation model."""
    permissions: Optional[List[UUID4]] = Field(default_factory=list, description="List of permission IDs")

    model_config = ConfigDict(
        json_schema_extra={

            "example": {
                "name": "loan_officer",
                "description": "Can manage loans",
                "tenant_id": "123e4567-e89b-12d3-a456-426614174000",
                "permissions": ["123e4567-e89b-12d3-a456-426614174001"]
            }
        })


class RoleUpdate(BaseModel):
    """Role update model."""
    name: Optional[str] = Field(None, min_length=3, max_length=50, description="Role name")
    description: Optional[str] = Field(None, max_length=500, description="Role description")
    permissions: Optional[List[UUID4]] = Field(None, description="List of permission IDs (replaces all)")

    model_config = ConfigDict(
        json_schema_extra={

            "example": {
                "name": "senior_loan_officer",
                "description": "Can manage and approve loans",
                "permissions": ["123e4567-e89b-12d3-a456-426614174001", "123e4567-e89b-12d3-a456-426614174002"]
            }
        })


class RoleResponse(RoleBase):
    """Role response model."""
    role_id: UUID4 = Field(..., description="Role ID")
    permissions: List[PermissionSummary] = Field(default_factory=list, description="List of permissions")
    created_at: datetime = Field(..., description="Creation timestamp")
    updated_at: datetime = Field(..., description="Last update timestamp")

    model_config = ConfigDict(
        json_schema_extra={

            "example": {
                "role_id": "123e4567-e89b-12d3-a456-426614174000",
                "name": "loan_officer",
                "description": "Can manage loans",
                "tenant_id": "123e4567-e89b-12d3-a456-426614174000",
                "permissions": [
                    {
                        "permission_id": "123e4567-e89b-12d3-a456-426614174001",
                        "name": "loan:read",
                        "resource_type": "loan",
                        "action": "read"
                    }
                ],
                "created_at": "2026-01-10T10:30:00Z",
                "updated_at": "2026-01-10T10:30:00Z"
            }
        })


class PaginationMetadata(BaseModel):
    """Pagination metadata."""
    total: int = Field(..., description="Total number of items")
    page: int = Field(..., description="Current page number")
    page_size: int = Field(..., description="Items per page")
    total_pages: int = Field(..., description="Total number of pages")


class RoleListResponse(BaseModel):
    """Role list response model."""
    roles: List[RoleResponse] = Field(..., description="List of roles")
    pagination: PaginationMetadata = Field(..., description="Pagination metadata")

    model_config = ConfigDict(
        json_schema_extra={

            "example": {
                "roles": [
                    {
                        "role_id": "123e4567-e89b-12d3-a456-426614174000",
                        "name": "loan_officer",
                        "description": "Can manage loans",
                        "tenant_id": "123e4567-e89b-12d3-a456-426614174000",
                        "permissions": [],
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
        })
