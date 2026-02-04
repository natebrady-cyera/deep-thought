"""Health check endpoints"""
from fastapi import APIRouter, status
from app.core.database import check_db_connection
from app.core.config import settings

router = APIRouter()


@router.get("/health")
async def health_check():
    """
    Health check endpoint.
    Returns system health status including database connection.
    """
    db_healthy = check_db_connection()

    health_status = {
        "service": "deep-thought",
        "version": settings.app_version,
        "status": "healthy" if db_healthy else "degraded",
        "database": {
            "status": "connected" if db_healthy else "disconnected",
            "type": "sqlite" if "sqlite" in settings.database_url else "postgres",
        },
    }

    status_code = status.HTTP_200_OK if db_healthy else status.HTTP_503_SERVICE_UNAVAILABLE

    return health_status
