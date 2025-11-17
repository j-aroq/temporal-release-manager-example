"""
Entity API endpoints for individual entity queries.

Provides endpoints for querying individual entities (Wave, Cluster, Bundle, App)
by their IDs without needing to traverse the full release hierarchy.
"""

from typing import Annotated
import logging

from fastapi import APIRouter, Depends, HTTPException, status

from ..models.auth import User
from ..models.entities import Wave, Cluster, Bundle, App
from ..services.entity_service import get_entity_service, EntityService, EntityNotFoundError
from ..core.validation import validate_entity_id_format
from .auth import get_current_user

logger = logging.getLogger(__name__)

# Create router
router = APIRouter()


@router.get("/entities/waves/{wave_id}", response_model=Wave)
async def get_wave(
    wave_id: str,
    current_user: Annotated[User, Depends(get_current_user)],
    entity_service: Annotated[EntityService, Depends(get_entity_service)],
) -> Wave:
    """
    Get single wave by ID.

    Requires authentication.

    Args:
        wave_id: Wave ID (format: wave:id)
        current_user: Authenticated user (injected by dependency)
        entity_service: Entity service instance (injected by dependency)

    Returns:
        Wave details with cluster IDs

    Raises:
        HTTPException: If wave not found (404) or service unavailable (503)
    """
    try:
        validate_entity_id_format(wave_id, "wave")

        logger.info(f"User {current_user.email} getting wave: {wave_id}")
        wave = await entity_service.get_wave(wave_id)
        return wave

    except EntityNotFoundError:
        logger.warning(f"Wave not found: {wave_id}")
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Wave not found: {wave_id}. It may have been completed or removed.",
        )

    except HTTPException:
        raise

    except Exception as e:
        logger.error(f"Error getting wave {wave_id}: {e}")
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Unable to retrieve wave. Temporal service may be unavailable.",
        )


@router.get("/entities/clusters/{cluster_id}", response_model=Cluster)
async def get_cluster(
    cluster_id: str,
    current_user: Annotated[User, Depends(get_current_user)],
    entity_service: Annotated[EntityService, Depends(get_entity_service)],
) -> Cluster:
    """
    Get single cluster by ID.

    Requires authentication.

    Args:
        cluster_id: Cluster ID (format: cluster:id)
        current_user: Authenticated user (injected by dependency)
        entity_service: Entity service instance (injected by dependency)

    Returns:
        Cluster details with bundle ID

    Raises:
        HTTPException: If cluster not found (404) or service unavailable (503)
    """
    try:
        validate_entity_id_format(cluster_id, "cluster")

        logger.info(f"User {current_user.email} getting cluster: {cluster_id}")
        cluster = await entity_service.get_cluster(cluster_id)
        return cluster

    except EntityNotFoundError:
        logger.warning(f"Cluster not found: {cluster_id}")
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Cluster not found: {cluster_id}. It may have been completed or removed.",
        )

    except HTTPException:
        raise

    except Exception as e:
        logger.error(f"Error getting cluster {cluster_id}: {e}")
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Unable to retrieve cluster. Temporal service may be unavailable.",
        )


@router.get("/entities/bundles/{bundle_id}", response_model=Bundle)
async def get_bundle(
    bundle_id: str,
    current_user: Annotated[User, Depends(get_current_user)],
    entity_service: Annotated[EntityService, Depends(get_entity_service)],
) -> Bundle:
    """
    Get single bundle by ID.

    Requires authentication.

    Args:
        bundle_id: Bundle ID (format: bundle:id)
        current_user: Authenticated user (injected by dependency)
        entity_service: Entity service instance (injected by dependency)

    Returns:
        Bundle details with app IDs

    Raises:
        HTTPException: If bundle not found (404) or service unavailable (503)
    """
    try:
        validate_entity_id_format(bundle_id, "bundle")

        logger.info(f"User {current_user.email} getting bundle: {bundle_id}")
        bundle = await entity_service.get_bundle(bundle_id)
        return bundle

    except EntityNotFoundError:
        logger.warning(f"Bundle not found: {bundle_id}")
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Bundle not found: {bundle_id}. It may have been completed or removed.",
        )

    except HTTPException:
        raise

    except Exception as e:
        logger.error(f"Error getting bundle {bundle_id}: {e}")
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Unable to retrieve bundle. Temporal service may be unavailable.",
        )


@router.get("/entities/apps/{app_id}", response_model=App)
async def get_app(
    app_id: str,
    current_user: Annotated[User, Depends(get_current_user)],
    entity_service: Annotated[EntityService, Depends(get_entity_service)],
) -> App:
    """
    Get single app by ID.

    Requires authentication.

    Args:
        app_id: App ID (format: app:id)
        current_user: Authenticated user (injected by dependency)
        entity_service: Entity service instance (injected by dependency)

    Returns:
        App details

    Raises:
        HTTPException: If app not found (404) or service unavailable (503)
    """
    try:
        validate_entity_id_format(app_id, "app")

        logger.info(f"User {current_user.email} getting app: {app_id}")
        app = await entity_service.get_app(app_id)
        return app

    except EntityNotFoundError:
        logger.warning(f"App not found: {app_id}")
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"App not found: {app_id}. It may have been completed or removed.",
        )

    except HTTPException:
        raise

    except Exception as e:
        logger.error(f"Error getting app {app_id}: {e}")
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Unable to retrieve app. Temporal service may be unavailable.",
        )
