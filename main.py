"""
Authorization Service - Main Application Entry Point
"""

import logging
import logging.config
import yaml
from contextlib import asynccontextmanager
from pathlib import Path
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.config import get_config
from app.middleware import (
    RequestContextMiddleware,
    AuthenticationMiddleware,
    LoggingMiddleware
)
from app.routes import (
    authz_router,
    roles_router,
    permissions_router,
    policies_router,
    assignments_router
)
from app.clients import get_entity_client


# Initialize logging
def setup_logging():
    """Setup logging configuration."""
    logging_config_path = Path("config/logging.yaml")
    
    if logging_config_path.exists():
        with open(logging_config_path, 'r') as f:
            config = yaml.safe_load(f)
            logging.config.dictConfig(config)
    else:
        # Basic logging setup if config file not found
        logging.basicConfig(
            level=logging.INFO,
            format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
        )


setup_logging()
logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan manager."""
    # Startup
    logger.info("Starting Authorization Service...")
    config = get_config()
    logger.info(f"Service: {config.service.name} v{config.service.version}")
    logger.info(f"Environment: {config.service.environment}")
    logger.info(f"Entity Service URL: {config.entity_service.base_url}")
    
    yield
    
    # Shutdown
    logger.info("Shutting down Authorization Service...")
    
    # Close entity service client
    try:
        entity_client = get_entity_client()
        await entity_client.close()
        logger.info("Closed entity service client")
    except Exception as e:
        logger.error(f"Error closing entity service client: {e}")


# Load configuration
config = get_config()

# Create FastAPI application
app = FastAPI(
    title="Authorization Service API",
    description="Central Policy Decision Point (PDP) for access control with RBAC, ABAC, and ownership-based policies",
    version="1.0.0",
    lifespan=lifespan,
    docs_url="/docs",
    redoc_url="/redoc",
    openapi_url="/openapi.json"
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=config.cors.allow_origins,
    allow_credentials=config.cors.allow_credentials,
    allow_methods=config.cors.allow_methods,
    allow_headers=config.cors.allow_headers,
)

# Add custom middleware (order matters!)
app.add_middleware(RequestContextMiddleware)
app.add_middleware(LoggingMiddleware)
app.add_middleware(
    AuthenticationMiddleware,
    jwt_secret=config.jwt.secret,
    jwt_algorithm=config.jwt.algorithm,
    api_key=config.api.key
)

# Register routers
app.include_router(authz_router)
app.include_router(roles_router)
app.include_router(permissions_router)
app.include_router(policies_router)
app.include_router(assignments_router)


# Health check endpoints
@app.get("/health", tags=["health"])
async def health_check():
    """Health check endpoint."""
    return {
        "status": "healthy",
        "service": config.service.name,
        "version": config.service.version
    }


@app.get("/healthz", tags=["health"])
async def health_probe():
    """Kubernetes health probe endpoint."""
    return {"status": "ok"}


@app.get("/", tags=["root"])
async def root():
    """Root endpoint."""
    return {
        "service": "Authorization Service",
        "version": "1.0.0",
        "description": "Central Policy Decision Point (PDP) for access control",
        "docs": "/docs",
        "health": "/health"
    }


if __name__ == "__main__":
    import uvicorn
    
    uvicorn.run(
        "main:app",
        host=config.service.host,
        port=config.service.port,
        reload=config.service.environment == "development",
        log_level="info"
    )
