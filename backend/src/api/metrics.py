"""
Metrics and observability endpoints.

Provides health checks, cache statistics, and system metrics.
"""

from typing import Dict, Any
import logging
import time
from datetime import datetime

from fastapi import APIRouter
from fastapi.responses import JSONResponse

from ..core.cache import get_release_cache
from ..services.temporal_client import get_temporal_client

logger = logging.getLogger(__name__)
router = APIRouter()

# Track API startup time
_startup_time = time.time()


@router.get("/metrics/health")
async def detailed_health() -> JSONResponse:
    """
    Detailed health check with component status.

    Returns health status of all system components.
    """
    health_status = {
        "status": "healthy",
        "timestamp": datetime.utcnow().isoformat(),
        "uptime_seconds": int(time.time() - _startup_time),
        "components": {},
    }

    # Check Temporal connection
    try:
        temporal_client = await get_temporal_client()
        temporal_healthy = await temporal_client.health_check()
        health_status["components"]["temporal"] = {
            "status": "healthy" if temporal_healthy else "unhealthy",
            "message": "Connected" if temporal_healthy else "Connection failed",
        }
    except Exception as e:
        logger.error(f"Temporal health check failed: {e}")
        health_status["components"]["temporal"] = {
            "status": "unhealthy",
            "message": str(e),
        }
        health_status["status"] = "degraded"

    # Cache stats
    try:
        cache = get_release_cache()
        cache_stats = cache.stats()
        health_status["components"]["cache"] = {
            "status": "healthy",
            "stats": cache_stats,
        }
    except Exception as e:
        logger.error(f"Cache stats failed: {e}")
        health_status["components"]["cache"] = {
            "status": "unknown",
            "message": str(e),
        }

    status_code = 200 if health_status["status"] == "healthy" else 503
    return JSONResponse(status_code=status_code, content=health_status)


@router.get("/metrics/cache")
async def cache_metrics() -> Dict[str, Any]:
    """
    Get cache statistics.

    Returns cache hit rate, size, and other metrics.
    """
    cache = get_release_cache()
    stats = cache.stats()

    return {
        "cache_name": "release_cache",
        "default_ttl_seconds": 10,
        **stats,
    }


@router.post("/metrics/cache/clear")
async def clear_cache() -> Dict[str, str]:
    """
    Clear all cache entries.

    Useful for troubleshooting or forcing fresh data fetch.
    """
    cache = get_release_cache()
    cache.clear()

    logger.info("Cache cleared via API request")

    return {
        "status": "success",
        "message": "Cache cleared successfully",
    }


@router.get("/metrics/system")
async def system_metrics() -> Dict[str, Any]:
    """
    Get system-level metrics.

    Returns uptime, version, and other system info.
    """
    return {
        "service": "Temporal Release Management BFF",
        "version": "1.0.0",
        "uptime_seconds": int(time.time() - _startup_time),
        "started_at": datetime.fromtimestamp(_startup_time).isoformat(),
        "python_version": "3.11+",
        "environment": "development",  # Could read from env
    }
