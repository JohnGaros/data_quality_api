"""Unit tests for Store interfaces and adapters."""

import sys
from pathlib import Path
from unittest.mock import MagicMock

import pytest

sys.path.append(str(Path(__file__).resolve().parents[2] / "src"))

from dq_metadata.models import ValidationJobMetadata
from dq_metadata.repository import IMetadataRepository
from dq_stores.base import ContractStore
from dq_stores.postgres import PostgresContractStore, PostgresJobRunStore


class DummyContractStore(ContractStore[dict]):
    """Minimal concrete implementation to satisfy abstract methods."""

    def __init__(self) -> None:
        self._store: dict[str, dict] = {}

    def get(self, key: str) -> dict | None:
        return self._store.get(key)

    def put(self, key: str, value: dict) -> None:
        self._store[key] = value

    def list(self, **filters):
        return self._store.values()

    def delete(self, key: str) -> None:
        self._store.pop(key, None)

    def get_latest_for_dataset(self, tenant: str, environment: str, dataset_type: str):
        return self._store.get(f"{tenant}:{environment}:{dataset_type}")


def test_contract_store_interface_can_be_subclassed() -> None:
    """Ensure ContractStore can be concretely implemented."""

    store = DummyContractStore()
    store.put("t1:dev:billing", {"contract_id": "c1"})

    assert store.get_latest_for_dataset("t1", "dev", "billing")["contract_id"] == "c1"


def test_postgres_contract_store_not_implemented() -> None:
    """PostgresContractStore is a placeholder until repository exists."""

    store = PostgresContractStore()
    with pytest.raises(NotImplementedError):
        store.get("any")


def test_postgres_job_run_store_delegates_to_repository() -> None:
    """JobRunStore should call the underlying metadata repository."""

    repo = MagicMock(spec=IMetadataRepository)
    job = ValidationJobMetadata(
        job_id="job-1",
        tenant_id="tenant-a",
        submission_source="api",
        status="succeeded",
        ingestion_mode=None,
        config_version=None,
        input_assets=[],
    )
    repo.list_jobs.return_value = [job]

    store = PostgresJobRunStore(repository=repo)
    store.put("job-1", job)

    repo.save_job.assert_called_once_with(job)
    assert store.get("job-1") == job
    assert list(store.list()) == [job]

    filtered = list(store.list_by_tenant("tenant-a", environment=None))
    assert filtered == [job]

    with pytest.raises(NotImplementedError):
        store.delete("job-1")
