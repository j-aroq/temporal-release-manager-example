"""
Release API endpoints.

Provides endpoints for listing releases and getting release details.
"""

from typing import Annotated, List, Dict, Any
import logging

from fastapi import APIRouter, Depends, HTTPException, status, Query
from pydantic import BaseModel, Field

from ..models.auth import User
from ..models.entities import Release, ReleaseHierarchy
from ..services.entity_service import get_entity_service, EntityService, EntityNotFoundError
from ..core.validation import validate_entity_id_format, validate_pagination_params
from ..core.errors import get_user_friendly_error
from .auth import get_current_user

logger = logging.getLogger(__name__)

# Create router
router = APIRouter()


class PaginatedReleases(BaseModel):
    """Paginated list of releases."""

    items: List[Release] = Field(..., description="List of releases")
    total: int = Field(..., description="Total number of releases")
    page: int = Field(..., description="Current page number")
    page_size: int = Field(..., description="Page size")


@router.get("/releases", response_model=PaginatedReleases)
async def list_releases(
    current_user: Annotated[User, Depends(get_current_user)],
    entity_service: Annotated[EntityService, Depends(get_entity_service)],
    page: int = Query(1, ge=1, description="Page number (1-indexed)"),
    page_size: int = Query(20, ge=1, le=100, description="Number of releases per page"),
) -> PaginatedReleases:
    """
    List all releases with pagination.

    Requires authentication.

    Args:
        current_user: Authenticated user (injected by dependency)
        entity_service: Entity service instance (injected by dependency)
        page: Page number (1-indexed, default: 1)
        page_size: Number of releases per page (default: 20, max: 100)

    Returns:
        Paginated list of releases

    Raises:
        HTTPException: If service is unavailable (503)
    """
    try:
        # Validate pagination parameters
        validate_pagination_params(page, page_size)

        logger.info(f"User {current_user.email} listing releases (page {page}, size {page_size})")

        result = await entity_service.list_releases(page=page, page_size=page_size)

        return PaginatedReleases(
            items=result["items"],
            total=result["total"],
            page=result["page"],
            page_size=result["page_size"],
        )

    except Exception as e:
        logger.error(f"Error listing releases: {e}")
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Unable to retrieve releases. Temporal service may be unavailable.",
        )


@router.get("/releases/{release_id}", response_model=Release)
async def get_release(
    release_id: str,
    current_user: Annotated[User, Depends(get_current_user)],
    entity_service: Annotated[EntityService, Depends(get_entity_service)],
) -> Release:
    """
    Get single release by ID.

    Requires authentication.

    Args:
        release_id: Release ID (format: release:id)
        current_user: Authenticated user (injected by dependency)
        entity_service: Entity service instance (injected by dependency)

    Returns:
        Release details

    Raises:
        HTTPException: If release not found (404) or service unavailable (503)
    """
    try:
        # Validate ID format
        validate_entity_id_format(release_id, "release")

        logger.info(f"User {current_user.email} getting release: {release_id}")

        release = await entity_service.get_release(release_id)
        return release

    except EntityNotFoundError as e:
        logger.warning(f"Release not found: {release_id}")
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=get_user_friendly_error("EntityNotFoundError"),
        )

    except HTTPException:
        # Re-raise HTTP exceptions
        raise

    except Exception as e:
        logger.error(f"Error getting release {release_id}: {e}")
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Unable to retrieve release. Temporal service may be unavailable.",
        )


@router.get("/releases/{release_id}/hierarchy", response_model=ReleaseHierarchy)
async def get_release_hierarchy(
    release_id: str,
    current_user: Annotated[User, Depends(get_current_user)],
    entity_service: Annotated[EntityService, Depends(get_entity_service)],
) -> ReleaseHierarchy:
    """
    Get complete release hierarchy with all child entities.

    Retrieves the full tree: Release → Waves → Clusters → Bundles → Apps
    Uses parallel queries for optimal performance.

    Requires authentication.

    Args:
        release_id: Release ID (format: release:id)
        current_user: Authenticated user (injected by dependency)
        entity_service: Entity service instance (injected by dependency)

    Returns:
        Complete release hierarchy with nested structure

    Raises:
        HTTPException: If release not found (404) or service unavailable (503)
    """
    try:
        # Validate ID format
        validate_entity_id_format(release_id, "release")

        logger.info(f"User {current_user.email} getting hierarchy for release: {release_id}")

        hierarchy = await entity_service.get_release_hierarchy(release_id)
        return hierarchy

    except EntityNotFoundError as e:
        logger.warning(f"Release not found for hierarchy: {release_id}")
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=get_user_friendly_error("EntityNotFoundError"),
        )

    except HTTPException:
        # Re-raise HTTP exceptions
        raise

    except Exception as e:
        logger.error(f"Error getting release hierarchy {release_id}: {e}")
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Unable to retrieve release hierarchy. Temporal service may be unavailable.",
        )
