"""Service responsible for persisting and querying metadata entities."""

from __future__ import annotations

from typing import Iterable, Optional
from uuid import UUID

from .models import (
    AuditEventMetadata,
    ComplianceTag,
    DataAssetMetadata,
    RuleVersionMetadata,
    ValidationJobMetadata,
)


class MetadataRegistry:
    """Thin abstraction layer around the underlying metadata store.

    In early iterations this can wrap direct database calls. Later we can
    swap in message-driven ingestion or external catalog integrations.
    """

    def __init__(self) -> None:
        # Placeholder for database/session handle injection.
        self._store = {
            "assets": [],
            "jobs": [],
            "rules": [],
            "audit_events": [],
            "tags": [],
        }

    # --- Data asset operations ---

    def register_asset(self, asset: DataAssetMetadata) -> None:
        """Persist or update a data asset entry."""
        self._store["assets"].append(asset)

    def get_asset(self, asset_id: UUID) -> Optional[DataAssetMetadata]:
        """Retrieve a data asset by identifier."""
        return next((asset for asset in self._store["assets"] if asset.asset_id == asset_id), None)

    # --- Validation job operations ---

    def record_job(self, job: ValidationJobMetadata) -> None:
        """Store metadata for a validation job."""
        self._store["jobs"].append(job)

    def list_jobs(self) -> Iterable[ValidationJobMetadata]:
        """Iterate over recorded jobs."""
        return list(self._store["jobs"])

    # --- Rule version operations ---

    def record_rule_version(self, rule_version: RuleVersionMetadata) -> None:
        """Add a rule version entry to the registry."""
        self._store["rules"].append(rule_version)

    def list_rule_versions(self, rule_id: Optional[str] = None) -> Iterable[RuleVersionMetadata]:
        """Return rule versions, optionally filtered by rule id."""
        items = self._store["rules"]
        if rule_id:
            items = [rv for rv in items if rv.rule_id == rule_id]
        return list(items)

    # --- Audit events ---

    def record_audit_event(self, event: AuditEventMetadata) -> None:
        """Persist an audit event."""
        self._store["audit_events"].append(event)

    def list_audit_events(self) -> Iterable[AuditEventMetadata]:
        """Fetch recorded audit events."""
        return list(self._store["audit_events"])

    # --- Compliance tags ---

    def assign_tag(self, tag: ComplianceTag) -> None:
        """Assign a compliance tag to a resource."""
        self._store["tags"].append(tag)

    def remove_tag(self, tag_id: UUID) -> None:
        """Remove a compliance tag (soft delete for governance trail)."""
        self._store["tags"] = [tag for tag in self._store["tags"] if tag.tag_id != tag_id]

    def list_tags(self, resource_id: Optional[str] = None) -> Iterable[ComplianceTag]:
        """List tags, optionally filtered by resource identifier."""
        tags = self._store["tags"]
        if resource_id:
            tags = [tag for tag in tags if tag.resource_id == resource_id]
        return list(tags)
