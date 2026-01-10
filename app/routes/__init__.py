"""
Routes package initialization.
"""

from .authz import router as authz_router
from .roles import router as roles_router
from .permissions import router as permissions_router
from .policies import router as policies_router
from .assignments import router as assignments_router

__all__ = [
    "authz_router",
    "roles_router",
    "permissions_router",
    "policies_router",
    "assignments_router",
]
