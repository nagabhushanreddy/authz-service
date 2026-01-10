"""
Permission management endpoints.
"""

import logging
from typing import Optional
from uuid import UUID
from fastapi import APIRouter, HTTPException, status, Query

from app.models.permission import PermissionCreate, PermissionUpdate, PermissionResponse, PermissionListResponse
from app.services.permission_service import get_permission_service

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api/v1/authz/permissions", tags=["permissions"])


@router.post("", response_model=PermissionResponse, status_code=status.HTTP_201_CREATED)
async def create_permission(permission_data: PermissionCreate):
    """Create a new permission."""
    try:
        permission_service = get_permission_service()
        return await permission_service.create_permission(permission_data)
    except Exception as e:
        logger.error(f"Failed to create permission: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to create permission"
        )


@router.get("", response_model=PermissionListResponse, status_code=status.HTTP_200_OK)
async def list_permissions(
    resource_type: Optional[str] = Query(None, description="Filter by resource type"),
    action: Optional[str] = Query(None, description="Filter by action"),
    page: int = Query(1, ge=1, description="Page number"),
    page_size: int = Query(50, ge=1, le=100, description="Items per page")
):
    """List permissions with pagination."""
    try:
        permission_service = get_permission_service()
        return await permission_service.list_permissions(resource_type, action, page, page_size)
    except Exception as e:
        logger.error(f"Failed to list permissions: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to list permissions"
        )


@router.get("/{permission_id}", response_model=PermissionResponse, status_code=status.HTTP_200_OK)
async def get_permission(permission_id: UUID):
    """Get permission by ID."""
    try:
        permission_service = get_permission_service()
        permission = await permission_service.get_permission(permission_id)
        if not permission:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Permission not found"
            )
        return permission
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to get permission: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to get permission"
        )


@router.patch("/{permission_id}", response_model=PermissionResponse, status_code=status.HTTP_200_OK)
async def update_permission(permission_id: UUID, permission_data: PermissionUpdate):
    """Update permission."""
    try:
        permission_service = get_permission_service()
        return await permission_service.update_permission(permission_id, permission_data)
    except Exception as e:
        logger.error(f"Failed to update permission: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to update permission"
        )


@router.delete("/{permission_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_permission(permission_id: UUID):
    """Delete permission."""
    try:
        permission_service = get_permission_service()
        success = await permission_service.delete_permission(permission_id)
        if not success:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Permission not found"
            )
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to delete permission: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to delete permission"
        )
