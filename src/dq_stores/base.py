"""Base Store interfaces for pluggable persistence of canonical JSON artifacts.

Stores abstract how artifacts are persisted (Postgres, filesystem, Blob, etc.)
without changing where configuration truth originates (contracts + libraries +
catalog). All methods are multi-tenant/environment aware.
"""

from __future__ import annotations

from abc import ABC, abstractmethod
from typing import Generic, Iterable, Optional, Protocol, TypeVar

T = TypeVar("T")
Key = TypeVar("Key")


class Store(ABC, Generic[Key, T]):
    """Generic Store interface for persisting canonical artifacts."""

    @abstractmethod
    def get(self, key: Key) -> Optional[T]:
        """Fetch an artifact by key."""

    @abstractmethod
    def put(self, key: Key, value: T) -> None:
        """Persist or replace an artifact."""

    @abstractmethod
    def list(self, **filters) -> Iterable[T]:
        """Iterate artifacts, optionally filtered."""

    @abstractmethod
    def delete(self, key: Key) -> None:
        """Delete an artifact by key."""


class ContractStore(Store[str, T], ABC):
    """Specialised store for contracts and dataset contracts.

    Keys and filters must include tenant/environment scoping.
    """

    @abstractmethod
    def get_latest_for_dataset(self, tenant: str, environment: str, dataset_type: str) -> Optional[T]:
        """Return the latest contract matching a dataset type for a tenant/env."""


class JobDefinitionStore(Store[str, T], ABC):
    """Store for JobDefinitions/Checkpoints."""

    @abstractmethod
    def list_by_tags(self, tenant: str, environment: str, tags: Optional[list[str]] = None) -> Iterable[T]:
        """Filter job definitions by tags for a tenant/env."""


class ActionProfileStore(Store[str, T], ABC):
    """Store for ActionProfiles (post-job behaviours)."""

    @abstractmethod
    def list_by_type(self, tenant: str, environment: str, action_type: Optional[str] = None) -> Iterable[T]:
        """Filter action profiles by type for a tenant/env."""


class JobRunStore(Store[str, T], ABC):
    """Store for validation/cleansing/profiling job run metadata."""

    @abstractmethod
    def list_by_tenant(self, tenant: str, environment: Optional[str] = None) -> Iterable[T]:
        """Return recorded runs for a tenant/env."""
