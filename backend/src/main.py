"""
FastAPI application for Temporal Release Management BFF.

Main application entry point with lifecycle management and middleware configuration.
"""

from contextlib import asynccontextmanager
from typing import AsyncGenerator

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

from .core.config import get_settings
from .core.logging import setup_logging, get_logger
from .core.env_validation import validate_settings
from .services.temporal_client import get_temporal_client, close_temporal_client

# Configure logging
setup_logging()
logger = get_logger(__name__)

# Load and validate settings (loads .env file via Pydantic)
try:
    settings = get_settings()
    validate_settings(settings)
except Exception as e:
    logger.error(f"Configuration loading failed: {e}")
    raise


@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncGenerator[None, None]:
    """
    Application lifespan manager for startup and shutdown events.

    Handles:
    - Temporal client initialization
    - Resource cleanup
    """
    settings = get_settings()
    logger.info("Starting Temporal Release Management BFF")
    logger.info(f"Temporal host: {settings.temporal_host}")
    logger.info(f"Temporal namespace: {settings.temporal_namespace}")

    # Startup: Initialize Temporal client
    try:
        temporal_client = await get_temporal_client()
        health = await temporal_client.health_check()
        if health:
            logger.info("Temporal client connected and healthy")
        else:
            logger.warning("Temporal client connection unhealthy")
    except Exception as e:
        logger.error(f"Failed to initialize Temporal client: {e}")
        # Don't fail startup - allow API to start even if Temporal is down
        logger.warning("API starting without Temporal connection")

    yield

    # Shutdown: Close Temporal client
    logger.info("Shutting down Temporal Release Management BFF")
    try:
        await close_temporal_client()
        logger.info("Temporal client closed successfully")
    except Exception as e:
        logger.error(f"Error closing Temporal client: {e}")


# Create FastAPI application
# settings already loaded above

app = FastAPI(
    title="Temporal Release Management API",
    description=(
        "BFF API for querying Temporal workflow state to display deployment release hierarchies.\n\n"
        "## Entity Hierarchy\n\n"
        "Release → Wave → Cluster → Bundle → App\n\n"
        "## Authentication\n\n"
        "All endpoints (except /auth/*) require JWT authentication via Bearer token."
    ),
    version="1.0.0",
    docs_url="/docs" if settings.enable_docs else None,
    redoc_url="/redoc" if settings.enable_docs else None,
    openapi_url="/openapi.json" if settings.enable_docs else None,
    lifespan=lifespan,
)

# Configure middleware
# Order matters: Security headers → Rate limiting → CORS

# Add security headers middleware
from .middleware import SecurityHeadersMiddleware, RateLimitMiddleware

app.add_middleware(SecurityHeadersMiddleware)

# Add rate limiting middleware
app.add_middleware(
    RateLimitMiddleware,
    requests_per_minute=60,  # 60 requests per minute for general endpoints
    burst_size=10,  # Allow burst of 10 requests
)

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.api_cors_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/health", tags=["Health"])
async def health_check() -> JSONResponse:
    """
    Health check endpoint.

    Returns API status and Temporal connection health.
    """
    try:
        temporal_client = await get_temporal_client()
        temporal_healthy = await temporal_client.health_check()
    except Exception as e:
        logger.error(f"Health check error: {e}")
        temporal_healthy = False

    return JSONResponse(
        status_code=200 if temporal_healthy else 503,
        content={
            "status": "healthy" if temporal_healthy else "degraded",
            "temporal": "connected" if temporal_healthy else "disconnected",
            "api": "running",
        },
    )


@app.get("/", tags=["Root"])
async def root() -> JSONResponse:
    """Root endpoint with API information."""
    return JSONResponse(
        content={
            "name": "Temporal Release Management API",
            "version": "1.0.0",
            "docs": "/docs" if settings.enable_docs else "disabled",
            "health": "/health",
        }
    )


# Import and include routers
from .api import auth, releases, entities, metrics

app.include_router(auth.router, prefix=settings.api_prefix, tags=["Authentication"])
app.include_router(releases.router, prefix=settings.api_prefix, tags=["Releases"])
app.include_router(entities.router, prefix=settings.api_prefix, tags=["Entities"])
app.include_router(metrics.router, prefix=settings.api_prefix, tags=["Metrics & Observability"])
