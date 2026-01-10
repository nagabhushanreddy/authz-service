"""
Assignment management endpoints.
"""

import logging
from typing import Optional, List
from uuid import UUID
from fastapi import APIRouter, HTTPException, status, Query

from app.models.assignment import (
    UserRoleAssignmentCreate,
    UserRoleAssignmentResponse,
    RolePermissionAssignmentCreate,
    RolePermissionAssignmentResponse
)
from app.models.role import RoleResponse
from app.models.permission import PermissionResponse
from app.services.assignment_service import get_assignment_service

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api/v1/authz/assignments", tags=["assignments"])


# User-Role assignment endpoints
@router.post("/users/{user_id}/roles", 
            response_model=UserRoleAssignmentResponse, 
            status_code=status.HTTP_201_CREATED)
async def assign_role_to_user(user_id: UUID, assignment_data: UserRoleAssignmentCreate):
    """Assign a role to a user."""
    try:
        assignment_service = get_assignment_service()
        return await assignment_service.assign_role_to_user(user_id, assignment_data)
    except Exception as e:
        logger.error(f"Failed to assign role to user: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to assign role to user"
        )


@router.get("/users/{user_id}/roles", 
           response_model=List[RoleResponse], 
           status_code=status.HTTP_200_OK)
async def get_user_roles(
    user_id: UUID,
    tenant_id: Optional[UUID] = Query(None, description="Filter by tenant ID"),
    active_only: bool = Query(True, description="Only return active assignments")
):
    """Get all roles assigned to a user."""
    try:
        assignment_service = get_assignment_service()
        return await assignment_service.get_user_roles(user_id, tenant_id, active_only)
    except Exception as e:
        logger.error(f"Failed to get user roles: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to get user roles"
        )


@router.delete("/users/{user_id}/roles/{role_id}", 
              status_code=status.HTTP_204_NO_CONTENT)
async def revoke_role_from_user(user_id: UUID, role_id: UUID):
    """Revoke a role from a user."""
    try:
        assignment_service = get_assignment_service()
        success = await assignment_service.revoke_role_from_user(user_id, role_id)
        if not success:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Assignment not found"
            )
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to revoke role from user: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to revoke role from user"
        )


# Role-Permission assignment endpoints
@router.post("/roles/{role_id}/permissions", 
            response_model=RolePermissionAssignmentResponse, 
            status_code=status.HTTP_201_CREATED)
async def assign_permission_to_role(role_id: UUID, assignment_data: RolePermissionAssignmentCreate):
    """Assign a permission to a role."""
    try:
        assignment_service = get_assignment_service()
        return await assignment_service.assign_permission_to_role(role_id, assignment_data)
    except Exception as e:
        logger.error(f"Failed to assign permission to role: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to assign permission to role"
        )


@router.get("/roles/{role_id}/permissions", 
           response_model=List[PermissionResponse], 
           status_code=status.HTTP_200_OK)
async def get_role_permissions(role_id: UUID):
    """Get all permissions assigned to a role."""
    try:
        assignment_service = get_assignment_service()
        return await assignment_service.get_role_permissions(role_id)
    except Exception as e:
        logger.error(f"Failed to get role permissions: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to get role permissions"
        )


@router.delete("/roles/{role_id}/permissions/{permission_id}", 
              status_code=status.HTTP_204_NO_CONTENT)
async def revoke_permission_from_role(role_id: UUID, permission_id: UUID):
    """Revoke a permission from a role."""
    try:
        assignment_service = get_assignment_service()
        success = await assignment_service.revoke_permission_from_role(role_id, permission_id)
        if not success:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Assignment not found"
            )
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to revoke permission from role: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to revoke permission from role"
        )
