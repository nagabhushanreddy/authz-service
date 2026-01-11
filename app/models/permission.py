"""
Permission models for authorization service.
"""

from typing import Optional, List, Dict, Any
from datetime import datetime
from pydantic import BaseModel, Field, UUID4, ConfigDict


class PermissionBase(BaseModel):
    """Base permission model."""
    name: str = Field(..., min_length=3, max_length=100, description="Permission name")
    description: Optional[str] = Field(None, max_length=500, description="Permission description")
    resource_type: str = Field(..., min_length=1, max_length=50, description="Resource type (e.g., loan, profile)")
    action: str = Field(..., min_length=1, max_length=50, description="Action (e.g., create, read, update, delete)")
    conditions: Optional[Dict[str, Any]] = Field(default_factory=dict, description="ABAC conditions")


class PermissionCreate(PermissionBase):
    """Permission creation model."""

    model_config = ConfigDict(
        json_schema_extra={

            "example": {
                "name": "loan:read",
                "description": "Read loan information",
                "resource_type": "loan",
                "action": "read",
                "conditions": {
                    "tenant_match": True,
                    "max_amount": 1000000
                }
            }
        })


class PermissionUpdate(BaseModel):
    """Permission update model."""
    name: Optional[str] = Field(None, min_length=3, max_length=100, description="Permission name")
    description: Optional[str] = Field(None, max_length=500, description="Permission description")
    conditions: Optional[Dict[str, Any]] = Field(None, description="ABAC conditions")

    model_config = ConfigDict(
        json_schema_extra={

            "example": {
                "description": "Read and export loan information",
                "conditions": {
                    "tenant_match": True,
                    "max_amount": 2000000
                }
            }
        })


class PermissionResponse(PermissionBase):
    """Permission response model."""
    permission_id: UUID4 = Field(..., description="Permission ID")
    created_at: datetime = Field(..., description="Creation timestamp")
    updated_at: datetime = Field(..., description="Last update timestamp")

    model_config = ConfigDict(
        json_schema_extra={

            "example": {
                "permission_id": "123e4567-e89b-12d3-a456-426614174000",
                "name": "loan:read",
                "description": "Read loan information",
                "resource_type": "loan",
                "action": "read",
                "conditions": {"tenant_match": True},
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


class PermissionListResponse(BaseModel):
    """Permission list response model."""
    permissions: List[PermissionResponse] = Field(..., description="List of permissions")
    pagination: PaginationMetadata = Field(..., description="Pagination metadata")

    model_config = ConfigDict(
        json_schema_extra={

            "example": {
                "permissions": [
                    {
                        "permission_id": "123e4567-e89b-12d3-a456-426614174000",
                        "name": "loan:read",
                        "description": "Read loan information",
                        "resource_type": "loan",
                        "action": "read",
                        "conditions": {},
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
