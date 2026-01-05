"""Health check and monitoring endpoints"""

from fastapi import APIRouter, Response, status
from pydantic import BaseModel
from typing import Dict, Any
from datetime import datetime
import os

from api.core.database import engine
from api.core.config import settings
from rag_system import vector_store

router = APIRouter(tags=["health"])


class HealthStatus(BaseModel):
    """Health check response model"""
    status: str
    timestamp: str
    version: str
    environment: str
    checks: Dict[str, Any]


class ReadinessStatus(BaseModel):
    """Readiness check response model"""
    ready: bool
    timestamp: str
    checks: Dict[str, Any]


@router.get("/health", response_model=HealthStatus)
async def health_check():
    """
    Basic health check endpoint.
    Returns 200 if the service is running.
    Used by monitoring systems to detect if the service is up.
    """
    return HealthStatus(
        status="healthy",
        timestamp=datetime.utcnow().isoformat(),
        version=settings.VERSION,
        environment="production" if not settings.DEBUG else "development",
        checks={
            "api": "up",
            "config": "loaded"
        }
    )


@router.get("/ready", response_model=ReadinessStatus)
async def readiness_check(response: Response):
    """
    Readiness check endpoint.
    Returns 200 if the service is ready to accept requests.
    Used by load balancers and orchestrators (Kubernetes, etc).
    
    Checks:
    - Database connectivity
    - Vector store availability (optional)
    """
    checks = {}
    all_ready = True
    
    # Check database connection
    try:
        async with engine.connect() as conn:
            await conn.execute("SELECT 1")
        checks["database"] = {
            "status": "ready",
            "type": "postgresql" if "postgresql" in settings.DATABASE_URL else "sqlite"
        }
    except Exception as e:
        checks["database"] = {
            "status": "not_ready",
            "error": str(e)
        }
        all_ready = False
    
    # Check vector store (optional, don't fail if disabled)
    require_chroma = os.getenv("REQUIRE_CHROMA", "true").lower() in {"1", "true", "yes"}
    try:
        # Simple check - vector store should be initialized
        if hasattr(vector_store, 'client') and vector_store.client:
            checks["vector_store"] = {
                "status": "ready",
                "required": require_chroma
            }
        else:
            checks["vector_store"] = {
                "status": "not_initialized",
                "required": require_chroma
            }
            if require_chroma:
                all_ready = False
    except Exception as e:
        checks["vector_store"] = {
            "status": "error",
            "error": str(e),
            "required": require_chroma
        }
        if require_chroma:
            all_ready = False
    
    # Check Redis (optional)
    try:
        import redis
        redis_client = redis.from_url(settings.REDIS_URL, decode_responses=True)
        redis_client.ping()
        checks["redis"] = {
            "status": "ready",
            "required": False
        }
    except Exception as e:
        checks["redis"] = {
            "status": "not_ready",
            "error": str(e),
            "required": False  # Redis is optional for core functionality
        }
    
    # Set response status based on readiness
    if not all_ready:
        response.status_code = status.HTTP_503_SERVICE_UNAVAILABLE
    
    return ReadinessStatus(
        ready=all_ready,
        timestamp=datetime.utcnow().isoformat(),
        checks=checks
    )


@router.get("/health/live", response_model=Dict[str, str])
async def liveness_check():
    """
    Kubernetes liveness probe.
    Simple check that returns 200 if the process is alive.
    """
    return {
        "status": "alive",
        "timestamp": datetime.utcnow().isoformat()
    }


@router.get("/health/startup", response_model=Dict[str, Any])
async def startup_check(response: Response):
    """
    Kubernetes startup probe.
    Checks if the application has finished starting up.
    """
    checks = {}
    startup_complete = True
    
    # Check if database is accessible
    try:
        async with engine.connect() as conn:
            await conn.execute("SELECT 1")
        checks["database"] = "initialized"
    except Exception as e:
        checks["database"] = f"error: {str(e)}"
        startup_complete = False
    
    # Check if config is loaded
    try:
        _ = settings.SECRET_KEY
        checks["config"] = "loaded"
    except Exception as e:
        checks["config"] = f"error: {str(e)}"
        startup_complete = False
    
    if not startup_complete:
        response.status_code = status.HTTP_503_SERVICE_UNAVAILABLE
    
    return {
        "startup_complete": startup_complete,
        "timestamp": datetime.utcnow().isoformat(),
        "checks": checks
    }
