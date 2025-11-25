"""Blob-backed store placeholders for future implementations.

Blob stores will be used for large artifacts (job results, reports) when
offloading from Postgres is desired. Wiring will integrate with
`dq_integration.azure_blob` once infra profiles drive container selection.
"""

from __future__ import annotations

from typing import Any, Iterable, Optional

from .base import JobRunStore


class AzureBlobJobRunStore(JobRunStore[Any]):
    """Placeholder for storing job runs/results in Azure Blob Storage."""

    def __init__(self, *, container: Optional[str] = None) -> None:
        self.container = container

    def get(self, key: str) -> Optional[Any]:
        raise NotImplementedError("Blob retrieval not implemented (docs/ARCHITECTURE.md#Integrations).")

    def put(self, key: str, value: Any) -> None:
        raise NotImplementedError("Blob persistence not implemented (docs/ARCHITECTURE.md#Integrations).")

    def list(self, **filters: Any) -> Iterable[Any]:
        raise NotImplementedError("Blob listing not implemented (docs/ARCHITECTURE.md#Integrations).")

    def delete(self, key: str) -> None:
        raise NotImplementedError("Blob deletion not implemented (docs/ARCHITECTURE.md#Integrations).")

    def list_by_tenant(self, tenant: str, environment: Optional[str] = None) -> Iterable[Any]:
        raise NotImplementedError("Blob filtering not implemented (docs/ARCHITECTURE.md#Integrations).")
