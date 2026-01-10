"""
Health check endpoints.
"""

from fastapi import APIRouter, status
from datetime import datetime

from app.config import settings

router = APIRouter(tags=["health"])


@router.get("/health", status_code=status.HTTP_200_OK)
@router.get("/healthz", status_code=status.HTTP_200_OK)
async def health_check():
    """
    Health check endpoint.
    
    Returns service health status and basic information.
    """
    return {
        "status": "healthy",
        "service": settings.SERVICE_NAME,
        "version": settings.SERVICE_VERSION,
        "environment": settings.ENVIRONMENT,
        "timestamp": datetime.utcnow().isoformat()
    }
