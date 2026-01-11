import os
from pathlib import Path
from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.config import settings
from app.middleware import AuthenticationMiddleware, RequestContextMiddleware, LoggingMiddleware
from app.routes import health_router, authz_router, roles_router, permissions_router, policies_router, assignments_router
from utils import init_utils, logger


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Lifespan context manager for startup and shutdown events"""
    logger.info(f"Starting {settings.SERVICE_NAME} v{settings.SERVICE_VERSION}")
    logger.info(f"Environment: {settings.ENVIRONMENT}")
    logger.info(f"Server: {settings.HOST}:{settings.PORT}")

    yield

    # Shutdown
    logger.info(f"Shutting down {settings.SERVICE_NAME}")


# Create FastAPI app
app = FastAPI(
    title="Authorization Service API",
    description="Authorization and RBAC/ABAC decision service",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc",
    openapi_url="/openapi.json",
    lifespan=lifespan,
)

# Add middleware
app.add_middleware(LoggingMiddleware)
app.add_middleware(
    AuthenticationMiddleware,
    jwt_secret=settings.JWT_SECRET_KEY,
    jwt_algorithm=settings.JWT_ALGORITHM,
    api_key=settings.API_KEY
)
app.add_middleware(RequestContextMiddleware)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routes
app.include_router(health_router)
app.include_router(authz_router)
app.include_router(roles_router)
app.include_router(permissions_router)
app.include_router(policies_router)
app.include_router(assignments_router)


@app.get("/")
async def root():
    """Root endpoint"""
    return {
        "service": settings.SERVICE_NAME,
        "version": settings.SERVICE_VERSION,
        "environment": settings.ENVIRONMENT,
        "docs": "/docs",
    }


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(
        "main:app",
        host=settings.HOST,
        port=settings.PORT,
        workers=settings.WORKERS,
        reload=settings.ENVIRONMENT == "development",
    )
