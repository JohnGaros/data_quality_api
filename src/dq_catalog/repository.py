"""Repository implementation for the Global Data Catalog.

This module implements the repository pattern for CatalogEntity and CatalogAttribute,
abstracting the underlying persistence layer (Store) to support future sync
with external systems (e.g., Collibra, Postgres).
"""

from typing import List, Optional

from dq_catalog.models import CatalogEntity
from dq_stores.base import Store


class CatalogRepository:
    """Repository for managing Global Catalog Entities and Attributes.

    This repository enforces the global scope (no tenant_id) and supports
    idempotent operations for sync readiness.
    """

    def __init__(self, store: Store[str, CatalogEntity]):
        """Initialize with a backing Store.

        Args:
            store: A Store implementation capable of persisting CatalogEntity objects.
                   The key is the catalog_entity_id.
        """
        self._store = store

    def get_entity(self, catalog_entity_id: str) -> Optional[CatalogEntity]:
        """Retrieve a catalog entity by its immutable ID.

        Args:
            catalog_entity_id: The unique identifier for the entity.

        Returns:
            The CatalogEntity if found, else None.
        """
        return self._store.get(catalog_entity_id)

    def put_entity(self, entity: CatalogEntity) -> None:
        """Persist or update a catalog entity.

        This operation is idempotent. If the entity exists, it is replaced.
        This supports the "Append-Only" versioning strategy where new versions
        are just new IDs (new entities), but also allows updating metadata/tags
        for an existing ID without changing its semantic meaning.

        Args:
            entity: The CatalogEntity to persist.
        """
        self._store.put(entity.catalog_entity_id, entity)

    def list_entities(self) -> List[CatalogEntity]:
        """List all catalog entities in the global catalog.

        Returns:
            A list of all CatalogEntity objects.
        """
        return list(self._store.list())

    def get_attribute(self, catalog_attribute_id: str) -> Optional[CatalogEntity]:
        """Retrieve the parent entity that contains the given attribute ID.

        Note: This is a scan operation unless the store supports secondary indexing.
        For MVP, we scan. In production, this should be optimized.

        Args:
            catalog_attribute_id: The unique identifier for the attribute.

        Returns:
            The parent CatalogEntity containing the attribute, or None.
        """
        # TODO: Optimize this with a secondary index or dedicated AttributeStore
        for entity in self.list_entities():
            for attr in entity.attributes:
                if attr.catalog_attribute_id == catalog_attribute_id:
                    return entity
        return None
