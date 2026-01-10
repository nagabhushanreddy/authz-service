"""
Middleware for authorization service.
"""

import logging
import uuid
from contextvars import ContextVar
from typing import Optional, Dict, Any
from datetime import datetime
from fastapi import Request, Response
from starlette.middleware.base import BaseHTTPMiddleware
from jose import jwt, JWTError

# Context variables for request tracking
correlation_id_var: ContextVar[str] = ContextVar("correlation_id", default="")
user_id_var: ContextVar[Optional[str]] = ContextVar("user_id", default=None)
tenant_id_var: ContextVar[Optional[str]] = ContextVar("tenant_id", default=None)

logger = logging.getLogger(__name__)


class CorrelationIdFilter(logging.Filter):
    """Logging filter to inject correlation ID."""
    
    def filter(self, record):
        record.correlation_id = correlation_id_var.get("")
        return True


class RequestContextMiddleware(BaseHTTPMiddleware):
    """Middleware to manage request context."""
    
    async def dispatch(self, request: Request, call_next):
        """Process request and inject context."""
        # Generate or extract correlation ID
        correlation_id = request.headers.get("X-Correlation-ID", str(uuid.uuid4()))
        correlation_id_var.set(correlation_id)
        
        # Process request
        response = await call_next(request)
        
        # Add correlation ID to response headers
        response.headers["X-Correlation-ID"] = correlation_id
        
        return response


class AuthenticationMiddleware(BaseHTTPMiddleware):
    """Middleware for JWT authentication."""
    
    def __init__(self, app, jwt_secret: str, jwt_algorithm: str = "HS256", 
                 api_key: Optional[str] = None):
        """Initialize authentication middleware.
        
        Args:
            app: FastAPI application
            jwt_secret: JWT secret key
            jwt_algorithm: JWT algorithm
            api_key: API key for service-to-service authentication
        """
        super().__init__(app)
        self.jwt_secret = jwt_secret
        self.jwt_algorithm = jwt_algorithm
        self.api_key = api_key
        
        # Public paths that don't require authentication
        self.public_paths = [
            "/health",
            "/healthz",
            "/docs",
            "/redoc",
            "/openapi.json"
        ]
    
    async def dispatch(self, request: Request, call_next):
        """Process request with authentication."""
        # Skip authentication for public paths
        if any(request.url.path.startswith(path) for path in self.public_paths):
            return await call_next(request)
        
        # Check API key authentication
        api_key = request.headers.get("X-API-Key")
        if api_key and api_key == self.api_key:
            # API key authentication successful
            return await call_next(request)
        
        # Check JWT authentication
        auth_header = request.headers.get("Authorization")
        if not auth_header or not auth_header.startswith("Bearer "):
            return Response(
                content='{"error": "Missing or invalid authorization header"}',
                status_code=401,
                media_type="application/json"
            )
        
        token = auth_header[7:]  # Remove "Bearer " prefix
        
        try:
            # Decode and validate JWT
            payload = jwt.decode(token, self.jwt_secret, algorithms=[self.jwt_algorithm])
            
            # Extract user context
            user_id = payload.get("user_id") or payload.get("sub")
            tenant_id = payload.get("tenant_id")
            
            if not user_id:
                return Response(
                    content='{"error": "Invalid token: missing user_id"}',
                    status_code=401,
                    media_type="application/json"
                )
            
            # Set context variables
            user_id_var.set(user_id)
            if tenant_id:
                tenant_id_var.set(tenant_id)
            
            # Add user info to request state
            request.state.user_id = user_id
            request.state.tenant_id = tenant_id
            request.state.token_payload = payload
            
            return await call_next(request)
            
        except JWTError as e:
            logger.warning(f"JWT validation failed: {e}")
            return Response(
                content=f'{{"error": "Invalid token: {str(e)}"}}',
                status_code=401,
                media_type="application/json"
            )


class LoggingMiddleware(BaseHTTPMiddleware):
    """Middleware for request/response logging."""
    
    async def dispatch(self, request: Request, call_next):
        """Process request with logging."""
        start_time = datetime.utcnow()
        
        # Log request
        logger.info(f"Request: {request.method} {request.url.path}")
        
        # Process request
        response = await call_next(request)
        
        # Calculate duration
        duration = (datetime.utcnow() - start_time).total_seconds()
        
        # Log response
        logger.info(
            f"Response: {request.method} {request.url.path} "
            f"status={response.status_code} duration={duration:.3f}s"
        )
        
        # Add timing header
        response.headers["X-Response-Time"] = f"{duration:.3f}s"
        
        return response


def get_current_user_id() -> Optional[str]:
    """Get current user ID from context."""
    return user_id_var.get()


def get_current_tenant_id() -> Optional[str]:
    """Get current tenant ID from context."""
    return tenant_id_var.get()


def get_correlation_id() -> str:
    """Get current correlation ID from context."""
    return correlation_id_var.get("")
