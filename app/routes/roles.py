"""
Role management endpoints.
"""

import logging
from typing import Optional
from uuid import UUID
from fastapi import APIRouter, HTTPException, status, Query

from app.models.role import RoleCreate, RoleUpdate, RoleResponse, RoleListResponse
from app.services.role_service import get_role_service

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api/v1/authz/roles", tags=["roles"])


@router.post("", response_model=RoleResponse, status_code=status.HTTP_201_CREATED)
async def create_role(role_data: RoleCreate):
    """Create a new role."""
    try:
        role_service = get_role_service()
        return await role_service.create_role(role_data)
    except Exception as e:
        logger.error(f"Failed to create role: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to create role"
        )


@router.get("", response_model=RoleListResponse, status_code=status.HTTP_200_OK)
async def list_roles(
    tenant_id: Optional[UUID] = Query(None, description="Filter by tenant ID"),
    page: int = Query(1, ge=1, description="Page number"),
    page_size: int = Query(50, ge=1, le=100, description="Items per page")
):
    """List roles with pagination."""
    try:
        role_service = get_role_service()
        return await role_service.list_roles(tenant_id, page, page_size)
    except Exception as e:
        logger.error(f"Failed to list roles: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to list roles"
        )


@router.get("/{role_id}", response_model=RoleResponse, status_code=status.HTTP_200_OK)
async def get_role(role_id: UUID):
    """Get role by ID."""
    try:
        role_service = get_role_service()
        role = await role_service.get_role(role_id)
        if not role:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Role not found"
            )
        return role
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to get role: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to get role"
        )


@router.patch("/{role_id}", response_model=RoleResponse, status_code=status.HTTP_200_OK)
async def update_role(role_id: UUID, role_data: RoleUpdate):
    """Update role."""
    try:
        role_service = get_role_service()
        return await role_service.update_role(role_id, role_data)
    except Exception as e:
        logger.error(f"Failed to update role: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to update role"
        )


@router.delete("/{role_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_role(role_id: UUID):
    """Delete role."""
    try:
        role_service = get_role_service()
        success = await role_service.delete_role(role_id)
        if not success:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Role not found"
            )
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to delete role: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to delete role"
        )
