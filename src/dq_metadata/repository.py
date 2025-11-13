"""Repository abstractions for metadata persistence.

Implements a repository interface (`IMetadataRepository`) so the
`MetadataRegistry` can interact with different backends (file-based,
database, cloud, etc.). The provided `FileMetadataRepository` is intended
for local development and testing; it stores JSON on disk using atomic
writes with a simple file-lock mechanism to ensure safe concurrent access.
"""

from __future__ import annotations

import json
import os
import tempfile
import time
from abc import ABC, abstractmethod
from pathlib import Path
from typing import Dict, Iterable, List, Optional, Type, TypeVar
from uuid import UUID

from .models import (
    AuditEventMetadata,
    ComplianceTag,
    DataAssetMetadata,
    RuleVersionMetadata,
    ValidationJobMetadata,
)

T = TypeVar("T")


DEFAULT_STORE_STRUCTURE = {
    "assets": [],
    "jobs": [],
    "rules": [],
    "audit_events": [],
    "tags": [],
}


def _json_default(value):
    """Fallback encoder for JSON serialization."""

    if hasattr(value, "isoformat"):
        return value.isoformat()  # datetime
    if isinstance(value, UUID):
        return str(value)
    raise TypeError(f"Object of type {type(value)!r} is not JSON serializable")


class IMetadataRepository(ABC):
    """Repository interface declaring metadata persistence operations."""

    # --- Assets ---
    @abstractmethod
    def save_asset(self, asset: DataAssetMetadata) -> None:
        """Create or update a data asset entry."""

    @abstractmethod
    def list_assets(self) -> List[DataAssetMetadata]:
        """Return all registered assets."""

    @abstractmethod
    def get_asset(self, asset_id: UUID) -> Optional[DataAssetMetadata]:
        """Fetch an asset by identifier."""

    # --- Validation jobs ---
    @abstractmethod
    def save_job(self, job: ValidationJobMetadata) -> None:
        """Persist a validation job metadata entry."""

    @abstractmethod
    def list_jobs(self) -> List[ValidationJobMetadata]:
        """Return recorded validation jobs."""

    # --- Rule versions ---
    @abstractmethod
    def save_rule_version(self, rule_version: RuleVersionMetadata) -> None:
        """Persist metadata describing a rule version."""

    @abstractmethod
    def list_rule_versions(self) -> List[RuleVersionMetadata]:
        """Return recorded rule versions."""

    # --- Audit events ---
    @abstractmethod
    def save_audit_event(self, event: AuditEventMetadata) -> None:
        """Persist an audit event."""

    @abstractmethod
    def list_audit_events(self) -> List[AuditEventMetadata]:
        """Return recorded audit events."""

    # --- Compliance tags ---
    @abstractmethod
    def save_tag(self, tag: ComplianceTag) -> None:
        """Persist a compliance tag."""

    @abstractmethod
    def delete_tag(self, tag_id: UUID) -> None:
        """Remove a compliance tag by identifier."""

    @abstractmethod
    def list_tags(self) -> List[ComplianceTag]:
        """Return compliance tags."""


class FileLock:
    """Simple file-based lock using lock files for cross-process safety."""

    def __init__(self, lock_path: Path, retry_delay: float = 0.1) -> None:
        self._lock_path = lock_path
        self._retry_delay = retry_delay
        self._fd: Optional[int] = None

    def __enter__(self) -> "FileLock":
        while True:
            try:
                self._fd = os.open(self._lock_path, os.O_CREAT | os.O_EXCL | os.O_RDWR)
                break
            except FileExistsError:
                time.sleep(self._retry_delay)
        return self

    def __exit__(self, exc_type, exc, tb) -> None:
        if self._fd is not None:
            os.close(self._fd)
        try:
            os.remove(self._lock_path)
        except FileNotFoundError:
            pass


class FileMetadataRepository(IMetadataRepository):
    """JSON-backed metadata repository for local development/testing."""

    def __init__(self, file_path: Optional[Path] = None) -> None:
        self._file_path = Path(file_path or Path.cwd() / "metadata_store.json")
        self._lock_path = self._file_path.with_suffix(".lock")
        self._ensure_store()

    # -- IMetadataRepository implementation ---------------------------------
    def save_asset(self, asset: DataAssetMetadata) -> None:
        data = self._read_store()
        data["assets"] = self._upsert_entry(data["assets"], asset, key="asset_id")
        self._write_store(data)

    def list_assets(self) -> List[DataAssetMetadata]:
        return self._deserialize_list(self._read_store()["assets"], DataAssetMetadata)

    def get_asset(self, asset_id: UUID) -> Optional[DataAssetMetadata]:
        for asset in self._read_store()["assets"]:
            if asset.get("asset_id") == str(asset_id):
                return DataAssetMetadata.parse_obj(asset)
        return None

    def save_job(self, job: ValidationJobMetadata) -> None:
        data = self._read_store()
        data["jobs"] = self._upsert_entry(data["jobs"], job, key="job_id")
        self._write_store(data)

    def list_jobs(self) -> List[ValidationJobMetadata]:
        return self._deserialize_list(self._read_store()["jobs"], ValidationJobMetadata)

    def save_rule_version(self, rule_version: RuleVersionMetadata) -> None:
        data = self._read_store()
        data["rules"] = self._upsert_entry(data["rules"], rule_version, key="rule_version_id")
        self._write_store(data)

    def list_rule_versions(self) -> List[RuleVersionMetadata]:
        return self._deserialize_list(self._read_store()["rules"], RuleVersionMetadata)

    def save_audit_event(self, event: AuditEventMetadata) -> None:
        data = self._read_store()
        data["audit_events"].append(json.loads(event.json()))
        self._write_store(data)

    def list_audit_events(self) -> List[AuditEventMetadata]:
        return self._deserialize_list(self._read_store()["audit_events"], AuditEventMetadata)

    def save_tag(self, tag: ComplianceTag) -> None:
        data = self._read_store()
        data["tags"] = self._upsert_entry(data["tags"], tag, key="tag_id")
        self._write_store(data)

    def delete_tag(self, tag_id: UUID) -> None:
        data = self._read_store()
        data["tags"] = [tag for tag in data["tags"] if tag.get("tag_id") != str(tag_id)]
        self._write_store(data)

    def list_tags(self) -> List[ComplianceTag]:
        return self._deserialize_list(self._read_store()["tags"], ComplianceTag)

    # -- Internal helpers ----------------------------------------------------
    def _ensure_store(self) -> None:
        if not self._file_path.exists():
            self._file_path.parent.mkdir(parents=True, exist_ok=True)
            self._write_store(DEFAULT_STORE_STRUCTURE)

    def _read_store(self) -> Dict[str, list]:
        with FileLock(self._lock_path):
            try:
                with self._file_path.open("r", encoding="utf-8") as handle:
                    return json.load(handle)
            except json.JSONDecodeError as exc:  # pragma: no cover - defensive logging
                raise RuntimeError(f"Corrupted metadata store: {exc}") from exc
            except OSError as exc:
                raise RuntimeError(f"Failed to read metadata store: {exc}") from exc

    def _write_store(self, data: Dict[str, list]) -> None:
        with FileLock(self._lock_path):
            temp_fd, temp_path = tempfile.mkstemp(dir=str(self._file_path.parent))
            try:
                with os.fdopen(temp_fd, "w", encoding="utf-8") as handle:
                    json.dump(data, handle, default=_json_default, indent=2)
                os.replace(temp_path, self._file_path)
            except OSError as exc:
                raise RuntimeError(f"Failed to write metadata store: {exc}") from exc
            finally:
                if os.path.exists(temp_path):
                    os.remove(temp_path)

    def _deserialize_list(self, records: Iterable[dict], model_cls: Type[T]) -> List[T]:
        return [model_cls.parse_obj(record) for record in records]

    def _upsert_entry(self, entries: List[dict], model_obj, *, key: str) -> List[dict]:
        payload = json.loads(model_obj.json())
        identifier = str(payload[key])
        updated = []
        replaced = False
        for entry in entries:
            if entry.get(key) == identifier:
                updated.append(payload)
                replaced = True
            else:
                updated.append(entry)
        if not replaced:
            updated.append(payload)
        return updated

