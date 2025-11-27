"""FastAPI dependency declarations (services, settings, etc.)."""

from functools import lru_cache

from dq_catalog.models import CatalogEntity
from dq_catalog.repository import CatalogRepository
from dq_stores.memory import InMemoryStore


@lru_cache()
def get_catalog_store() -> InMemoryStore[str, CatalogEntity]:
    """Return a singleton in-memory store for catalog entities."""
    return InMemoryStore[str, CatalogEntity]()


def get_catalog_repository() -> CatalogRepository:
    """Return the catalog repository using the configured store."""
    store = get_catalog_store()
    return CatalogRepository(store)
