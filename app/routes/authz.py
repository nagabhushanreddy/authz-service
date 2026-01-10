"""
Authorization decision endpoints.
"""

import logging
from typing import List
from fastapi import APIRouter, HTTPException, status
from datetime import datetime

from app.models.request import AuthorizationRequest, BatchAuthorizationRequest
from app.models.response import (
    AuthorizationResponse, 
    BatchAuthorizationResponse, 
    DecisionResponse,
    ResponseMetadata
)
from app.services.decision_service import get_decision_service
from app.middleware import get_correlation_id

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api/v1/authz", tags=["authorization"])


@router.post("/check", response_model=AuthorizationResponse, status_code=status.HTTP_200_OK)
async def check_authorization(request: AuthorizationRequest):
    """
    Check authorization for a single request.
    
    Evaluates RBAC, ABAC, and ownership rules to determine if user has permission.
    """
    try:
        decision_service = get_decision_service()
        response = await decision_service.check_authorization(request)
        return response
    except Exception as e:
        logger.error(f"Authorization check failed: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Authorization check failed"
        )


@router.post("/check:batch", response_model=BatchAuthorizationResponse, status_code=status.HTTP_200_OK)
async def batch_check_authorization(request: BatchAuthorizationRequest):
    """
    Check authorization for multiple requests in batch.
    
    Processes up to 100 authorization checks in a single request.
    """
    try:
        decision_service = get_decision_service()
        decisions: List[DecisionResponse] = []
        
        # Process each check
        for index, check in enumerate(request.checks):
            try:
                response = await decision_service.check_authorization(check)
                decisions.append(DecisionResponse(
                    decision=response.decision,
                    reason_codes=response.reason_codes,
                    policy_version=response.policy_version,
                    request_index=index
                ))
            except Exception as e:
                logger.error(f"Batch check failed for index {index}: {e}")
                # Continue processing other checks
                decisions.append(DecisionResponse(
                    decision="DENY",
                    reason_codes=["EVALUATION_ERROR"],
                    policy_version="1.0.0",
                    request_index=index
                ))
        
        return BatchAuthorizationResponse(
            decisions=decisions,
            metadata=ResponseMetadata(
                timestamp=datetime.utcnow(),
                correlation_id=get_correlation_id() or None
            )
        )
    except Exception as e:
        logger.error(f"Batch authorization check failed: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Batch authorization check failed"
        )
