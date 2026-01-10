"""
Pydantic models for the Authorization Service.
"""

from .request import (
    AuthorizationRequest,
    BatchAuthorizationRequest,
    AuthorizationContext,
)
from .response import (
    AuthorizationResponse,
    BatchAuthorizationResponse,
    DecisionResponse,
    StandardResponse,
    ErrorResponse,
    ErrorDetail,
    ResponseMetadata,
)
from .role import (
    RoleBase,
    RoleCreate,
    RoleUpdate,
    RoleResponse,
    RoleListResponse,
)
from .permission import (
    PermissionBase,
    PermissionCreate,
    PermissionUpdate,
    PermissionResponse,
    PermissionListResponse,
)
from .policy import (
    PolicyBase,
    PolicyCreate,
    PolicyUpdate,
    PolicyResponse,
    PolicyListResponse,
    Rule,
    PolicyType,
    RuleEffect,
)
from .assignment import (
    UserRoleAssignmentCreate,
    UserRoleAssignmentResponse,
    RolePermissionAssignmentCreate,
    RolePermissionAssignmentResponse,
)

__all__ = [
    # Request models
    "AuthorizationRequest",
    "BatchAuthorizationRequest",
    "AuthorizationContext",
    # Response models
    "AuthorizationResponse",
    "BatchAuthorizationResponse",
    "DecisionResponse",
    "StandardResponse",
    "ErrorResponse",
    "ErrorDetail",
    "ResponseMetadata",
    # Role models
    "RoleBase",
    "RoleCreate",
    "RoleUpdate",
    "RoleResponse",
    "RoleListResponse",
    # Permission models
    "PermissionBase",
    "PermissionCreate",
    "PermissionUpdate",
    "PermissionResponse",
    "PermissionListResponse",
    # Policy models
    "PolicyBase",
    "PolicyCreate",
    "PolicyUpdate",
    "PolicyResponse",
    "PolicyListResponse",
    "Rule",
    "PolicyType",
    "RuleEffect",
    # Assignment models
    "UserRoleAssignmentCreate",
    "UserRoleAssignmentResponse",
    "RolePermissionAssignmentCreate",
    "RolePermissionAssignmentResponse",
]
