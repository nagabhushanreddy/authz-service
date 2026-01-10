"""
Response models for authorization service.
"""

from typing import Optional, List, Dict, Any, Generic, TypeVar
from datetime import datetime
from pydantic import BaseModel, Field, UUID4
from enum import Enum


class DecisionType(str, Enum):
    """Authorization decision types."""
    ALLOW = "ALLOW"
    DENY = "DENY"


class ResponseMetadata(BaseModel):
    """Metadata for responses."""
    timestamp: datetime = Field(default_factory=datetime.utcnow, description="Response timestamp")
    correlation_id: Optional[UUID4] = Field(None, description="Request correlation ID")

    class Config:
        json_schema_extra = {
            "example": {
                "timestamp": "2026-01-10T10:30:00Z",
                "correlation_id": "123e4567-e89b-12d3-a456-426614174000"
            }
        }


class AuthorizationResponse(BaseModel):
    """Response model for authorization check."""
    decision: DecisionType = Field(..., description="Authorization decision")
    reason_codes: List[str] = Field(default_factory=list, description="Reason codes for decision")
    policy_version: str = Field(..., description="Version of policies evaluated")
    evaluated_policies: List[str] = Field(default_factory=list, description="List of policy IDs evaluated")
    metadata: ResponseMetadata = Field(default_factory=ResponseMetadata, description="Response metadata")

    class Config:
        json_schema_extra = {
            "example": {
                "decision": "ALLOW",
                "reason_codes": ["RBAC_MATCH", "ROLE_ADMIN"],
                "policy_version": "1.0.0",
                "evaluated_policies": ["policy-123", "policy-456"],
                "metadata": {
                    "timestamp": "2026-01-10T10:30:00Z",
                    "correlation_id": "123e4567-e89b-12d3-a456-426614174000"
                }
            }
        }


class DecisionResponse(BaseModel):
    """Individual decision in batch response."""
    decision: DecisionType = Field(..., description="Authorization decision")
    reason_codes: List[str] = Field(default_factory=list, description="Reason codes for decision")
    policy_version: str = Field(..., description="Version of policies evaluated")
    request_index: int = Field(..., description="Index of request in batch")

    class Config:
        json_schema_extra = {
            "example": {
                "decision": "ALLOW",
                "reason_codes": ["RBAC_MATCH"],
                "policy_version": "1.0.0",
                "request_index": 0
            }
        }


class BatchAuthorizationResponse(BaseModel):
    """Response model for batch authorization checks."""
    decisions: List[DecisionResponse] = Field(..., description="List of authorization decisions")
    metadata: ResponseMetadata = Field(default_factory=ResponseMetadata, description="Response metadata")

    class Config:
        json_schema_extra = {
            "example": {
                "decisions": [
                    {
                        "decision": "ALLOW",
                        "reason_codes": ["RBAC_MATCH"],
                        "policy_version": "1.0.0",
                        "request_index": 0
                    },
                    {
                        "decision": "DENY",
                        "reason_codes": ["NO_PERMISSION"],
                        "policy_version": "1.0.0",
                        "request_index": 1
                    }
                ],
                "metadata": {
                    "timestamp": "2026-01-10T10:30:00Z",
                    "correlation_id": "123e4567-e89b-12d3-a456-426614174000"
                }
            }
        }


T = TypeVar('T')


class StandardResponse(BaseModel, Generic[T]):
    """Standard API response wrapper."""
    success: bool = Field(..., description="Indicates if request was successful")
    data: Optional[T] = Field(None, description="Response data")
    error: Optional['ErrorDetail'] = Field(None, description="Error details if unsuccessful")
    metadata: ResponseMetadata = Field(default_factory=ResponseMetadata, description="Response metadata")

    class Config:
        json_schema_extra = {
            "example": {
                "success": True,
                "data": {"id": "123"},
                "error": None,
                "metadata": {
                    "timestamp": "2026-01-10T10:30:00Z",
                    "correlation_id": "123e4567-e89b-12d3-a456-426614174000"
                }
            }
        }


class ErrorDetail(BaseModel):
    """Error detail model."""
    code: str = Field(..., description="Error code")
    message: str = Field(..., description="Human-readable error message")
    details: Optional[Dict[str, Any]] = Field(None, description="Additional error details")

    class Config:
        json_schema_extra = {
            "example": {
                "code": "INVALID_REQUEST",
                "message": "Invalid request format",
                "details": {"field": "user_id", "error": "Invalid UUID format"}
            }
        }


class ErrorResponse(BaseModel):
    """Error response model."""
    success: bool = Field(False, description="Always false for errors")
    data: None = Field(None, description="Always null for errors")
    error: ErrorDetail = Field(..., description="Error details")
    metadata: ResponseMetadata = Field(default_factory=ResponseMetadata, description="Response metadata")

    class Config:
        json_schema_extra = {
            "example": {
                "success": False,
                "data": None,
                "error": {
                    "code": "ROLE_NOT_FOUND",
                    "message": "Role not found",
                    "details": {"role_id": "123e4567-e89b-12d3-a456-426614174000"}
                },
                "metadata": {
                    "timestamp": "2026-01-10T10:30:00Z",
                    "correlation_id": "123e4567-e89b-12d3-a456-426614174000"
                }
            }
        }
