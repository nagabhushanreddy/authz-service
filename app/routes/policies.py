"""
Policy management endpoints.
"""

import logging
from typing import Optional
from uuid import UUID
from fastapi import APIRouter, HTTPException, status, Query

from app.models.policy import PolicyCreate, PolicyUpdate, PolicyResponse, PolicyListResponse
from app.services.policy_service import get_policy_service

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api/v1/authz/policies", tags=["policies"])


@router.post("", response_model=PolicyResponse, status_code=status.HTTP_201_CREATED)
async def create_policy(policy_data: PolicyCreate):
    """Create a new policy."""
    try:
        policy_service = get_policy_service()
        return await policy_service.create_policy(policy_data)
    except Exception as e:
        logger.error(f"Failed to create policy: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to create policy"
        )


@router.get("", response_model=PolicyListResponse, status_code=status.HTTP_200_OK)
async def list_policies(
    tenant_id: Optional[UUID] = Query(None, description="Filter by tenant ID"),
    policy_type: Optional[str] = Query(None, description="Filter by policy type"),
    active: Optional[bool] = Query(None, description="Filter by active status"),
    page: int = Query(1, ge=1, description="Page number"),
    page_size: int = Query(50, ge=1, le=100, description="Items per page")
):
    """List policies with pagination."""
    try:
        policy_service = get_policy_service()
        return await policy_service.list_policies(tenant_id, policy_type, active, page, page_size)
    except Exception as e:
        logger.error(f"Failed to list policies: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to list policies"
        )


@router.get("/{policy_id}", response_model=PolicyResponse, status_code=status.HTTP_200_OK)
async def get_policy(policy_id: UUID):
    """Get policy by ID."""
    try:
        policy_service = get_policy_service()
        policy = await policy_service.get_policy(policy_id)
        if not policy:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Policy not found"
            )
        return policy
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to get policy: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to get policy"
        )


@router.patch("/{policy_id}", response_model=PolicyResponse, status_code=status.HTTP_200_OK)
async def update_policy(policy_id: UUID, policy_data: PolicyUpdate):
    """Update policy."""
    try:
        policy_service = get_policy_service()
        return await policy_service.update_policy(policy_id, policy_data)
    except Exception as e:
        logger.error(f"Failed to update policy: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to update policy"
        )


@router.delete("/{policy_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_policy(policy_id: UUID):
    """Delete policy."""
    try:
        policy_service = get_policy_service()
        success = await policy_service.delete_policy(policy_id)
        if not success:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Policy not found"
            )
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to delete policy: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to delete policy"
        )
