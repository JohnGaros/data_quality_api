"""Postgres-backed store adapters.

These adapters allow registries to depend on Store abstractions while the
underlying persistence can evolve (Postgres today, Blob/filesystem later).
"""

from __future__ import annotations

from typing import Any, Iterable, Optional

from dq_metadata.repository import IMetadataRepository, FileMetadataRepository
from dq_metadata.models import ValidationJobMetadata

from .base import ActionProfileStore, ContractStore, JobDefinitionStore, JobRunStore


class PostgresContractStore(ContractStore[Any]):
    """Placeholder for a Postgres-backed ContractStore.

    TODO: Implement using `dq_contracts.repository` once available. See
    docs/CONTRACT_DRIVEN_ARCHITECTURE.md.
    """

    def __init__(self, db_writer: Optional[Any] = None) -> None:
        self._db_writer = db_writer

    def get(self, key: str) -> Optional[Any]:
        raise NotImplementedError("Contract retrieval not implemented (docs/CONTRACT_DRIVEN_ARCHITECTURE.md).")

    def put(self, key: str, value: Any) -> None:
        raise NotImplementedError("Contract persistence not implemented (docs/CONTRACT_DRIVEN_ARCHITECTURE.md).")

    def list(self, **filters: Any) -> Iterable[Any]:
        raise NotImplementedError("Contract listing not implemented (docs/CONTRACT_DRIVEN_ARCHITECTURE.md).")

    def delete(self, key: str) -> None:
        raise NotImplementedError("Contract deletion not implemented (docs/CONTRACT_DRIVEN_ARCHITECTURE.md).")

    def get_latest_for_dataset(self, tenant: str, environment: str, dataset_type: str) -> Optional[Any]:
        raise NotImplementedError("Contract lookup not implemented (docs/CONTRACT_DRIVEN_ARCHITECTURE.md).")


class PostgresJobDefinitionStore(JobDefinitionStore[Any]):
    """Placeholder for Postgres-backed JobDefinition storage.

    TODO: Wire to dq_jobs registry once implemented. See
    docs/ACTIONS_AND_JOB_DEFINITIONS.md.
    """

    def __init__(self, db_writer: Optional[Any] = None) -> None:
        self._db_writer = db_writer

    def get(self, key: str) -> Optional[Any]:
        raise NotImplementedError("JobDefinition retrieval not implemented (docs/ACTIONS_AND_JOB_DEFINITIONS.md).")

    def put(self, key: str, value: Any) -> None:
        raise NotImplementedError("JobDefinition persistence not implemented (docs/ACTIONS_AND_JOB_DEFINITIONS.md).")

    def list(self, **filters: Any) -> Iterable[Any]:
        raise NotImplementedError("JobDefinition listing not implemented (docs/ACTIONS_AND_JOB_DEFINITIONS.md).")

    def delete(self, key: str) -> None:
        raise NotImplementedError("JobDefinition deletion not implemented (docs/ACTIONS_AND_JOB_DEFINITIONS.md).")

    def list_by_tags(self, tenant: str, environment: str, tags: Optional[list[str]] = None) -> Iterable[Any]:
        raise NotImplementedError("JobDefinition tag filtering not implemented (docs/ACTIONS_AND_JOB_DEFINITIONS.md).")


class PostgresActionProfileStore(ActionProfileStore[Any]):
    """Placeholder for Postgres-backed ActionProfile storage.

    TODO: Wire to dq_actions registry once implemented. See
    docs/ACTIONS_AND_JOB_DEFINITIONS.md.
    """

    def __init__(self, db_writer: Optional[Any] = None) -> None:
        self._db_writer = db_writer

    def get(self, key: str) -> Optional[Any]:
        raise NotImplementedError("ActionProfile retrieval not implemented (docs/ACTIONS_AND_JOB_DEFINITIONS.md).")

    def put(self, key: str, value: Any) -> None:
        raise NotImplementedError("ActionProfile persistence not implemented (docs/ACTIONS_AND_JOB_DEFINITIONS.md).")

    def list(self, **filters: Any) -> Iterable[Any]:
        raise NotImplementedError("ActionProfile listing not implemented (docs/ACTIONS_AND_JOB_DEFINITIONS.md).")

    def delete(self, key: str) -> None:
        raise NotImplementedError("ActionProfile deletion not implemented (docs/ACTIONS_AND_JOB_DEFINITIONS.md).")

    def list_by_type(self, tenant: str, environment: str, action_type: Optional[str] = None) -> Iterable[Any]:
        raise NotImplementedError("ActionProfile type filtering not implemented (docs/ACTIONS_AND_JOB_DEFINITIONS.md).")


class PostgresJobRunStore(JobRunStore[ValidationJobMetadata]):
    """Store adapter that uses an `IMetadataRepository` for job run metadata.

    Defaults to the file-backed repository for local dev; swap in a
    Postgres-backed implementation once available.
    """

    def __init__(self, repository: Optional[IMetadataRepository] = None) -> None:
        self.repository = repository or FileMetadataRepository()

    def get(self, key: str) -> Optional[ValidationJobMetadata]:
        for job in self.repository.list_jobs():
            if str(job.job_id) == key:
                return job
        return None

    def put(self, key: str, value: ValidationJobMetadata) -> None:
        self.repository.save_job(value)

    def list(self, **filters: Any) -> Iterable[ValidationJobMetadata]:
        return list(self.repository.list_jobs())

    def delete(self, key: str) -> None:
        # TODO: Add delete support to metadata repository. See docs/reference/METADATA_PILLARS.md.
        raise NotImplementedError("Deletion not supported by metadata repository.")

    def list_by_tenant(self, tenant: str, environment: Optional[str] = None) -> Iterable[ValidationJobMetadata]:
        jobs = self.repository.list_jobs()
        return [
            job
            for job in jobs
            if getattr(job, "tenant_id", None) == tenant
            and (environment is None or getattr(job, "environment", None) == environment)
        ]
