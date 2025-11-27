"""Global Data Catalog API endpoints.

These endpoints provide access to the shared semantic definitions (Entities and Attributes).
Access is global (not tenant-scoped).
"""

from typing import List

from fastapi import APIRouter, Depends, HTTPException, status

from dq_catalog.models import CatalogEntity
from dq_catalog.repository import CatalogRepository
from dq_api.dependencies import get_catalog_repository

router = APIRouter(prefix="/catalog", tags=["Global Catalog"])


@router.get("/entities", response_model=List[CatalogEntity])
def list_entities(
    repo: CatalogRepository = Depends(get_catalog_repository),
) -> List[CatalogEntity]:
    """List all entities in the global catalog."""
    return repo.list_entities()


@router.get("/entities/{entity_id}", response_model=CatalogEntity)
def get_entity(
    entity_id: str,
    repo: CatalogRepository = Depends(get_catalog_repository),
) -> CatalogEntity:
    """Get a specific catalog entity by its immutable ID."""
    entity = repo.get_entity(entity_id)
    if not entity:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Catalog entity '{entity_id}' not found",
        )
    return entity


@router.post("/entities", status_code=status.HTTP_201_CREATED)
def create_or_update_entity(
    entity: CatalogEntity,
    repo: CatalogRepository = Depends(get_catalog_repository),
) -> CatalogEntity:
    """Create or update a catalog entity (Idempotent).

    Note: In a real deployment, this should be restricted to Admins/Stewards.
    """
    repo.put_entity(entity)
    return entity
