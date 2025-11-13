"""Service responsible for persisting and querying metadata entities.

In addition to CRUD helpers, the registry exposes catalog-style discovery
features (search, faceting, lineage management) that future API endpoints
such as `/catalog/assets`, `/catalog/assets/{asset_id}`, `/catalog/search`,
and `/catalog/facets` can leverage.
"""

from __future__ import annotations

from collections import defaultdict
from typing import Dict, Iterable, List, Optional
from uuid import UUID

from .models import (
    AuditEventMetadata,
    ComplianceTag,
    DataAssetMetadata,
    FieldMetadata,
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
        self._store: Dict[str, list] = {
            "assets": [],
            "jobs": [],
            "rules": [],
            "audit_events": [],
            "tags": [],
        }

    # --- Data asset operations ---

    def register_asset(self, asset: DataAssetMetadata) -> None:
        """Persist or update a data asset entry."""

        for index, existing in enumerate(self._store["assets"]):
            if existing.asset_id == asset.asset_id:
                self._store["assets"][index] = asset
                break
        else:
            self._store["assets"].append(asset)

    def get_asset(self, asset_id: UUID) -> Optional[DataAssetMetadata]:
        """Retrieve a data asset by identifier."""
        return next((asset for asset in self._store["assets"] if asset.asset_id == asset_id), None)

    # --- Catalog discovery helpers ---

    def link_assets(self, parent_asset_id: UUID, child_asset_id: UUID) -> None:
        """Register a parent/child relationship between two assets."""

        parent = self.get_asset(parent_asset_id)
        child = self.get_asset(child_asset_id)
        if not parent or not child:
            return

        updated_parent = parent.copy(update={"child_asset_ids": list({*parent.child_asset_ids, child_asset_id})})
        updated_child = child.copy(update={"parent_asset_ids": list({*child.parent_asset_ids, parent_asset_id})})
        self.register_asset(updated_parent)
        self.register_asset(updated_child)

    def relate_assets(self, source_asset_id: UUID, target_asset_id: UUID) -> None:
        """Record a cross-asset lineage link (e.g., joins/views)."""

        source = self.get_asset(source_asset_id)
        target = self.get_asset(target_asset_id)
        if not source or not target:
            return

        updated_source = source.copy(update={"related_asset_ids": list({*source.related_asset_ids, target_asset_id})})
        updated_target = target.copy(update={"related_asset_ids": list({*target.related_asset_ids, source_asset_id})})
        self.register_asset(updated_source)
        self.register_asset(updated_target)

    def find_assets(
        self,
        *,
        name: Optional[str] = None,
        owner: Optional[str] = None,
        tag: Optional[str] = None,
        field_name: Optional[str] = None,
    ) -> List[DataAssetMetadata]:
        """Search assets using catalog-style filters (name, owner, tag, field)."""

        assets = list(self._store["assets"])
        if name:
            needle = name.lower()
            assets = [asset for asset in assets if (asset.name or asset.dataset_type).lower().find(needle) != -1]
        if owner:
            assets = [asset for asset in assets if asset.owner and asset.owner.lower() == owner.lower()]
        if field_name:
            field_lower = field_name.lower()
            assets = [
                asset
                for asset in assets
                if any(field.name.lower() == field_lower for field in asset.fields)
            ]
        if tag:
            tagged_asset_ids = {
                tag_entry.resource_id
                for tag_entry in self._store["tags"]
                if tag_entry.tag_value.lower() == tag.lower() or tag_entry.tag_key.lower() == tag.lower()
            }
            assets = [asset for asset in assets if str(asset.asset_id) in tagged_asset_ids]
        return assets

    def facet_assets(self, fields: Optional[List[str]] = None) -> Dict[str, Dict[str, int]]:
        """Return facet counts (classification, owner, etc.) for catalog browsing."""

        fields = fields or ["dataset_type", "classification", "owner", "data_source"]
        facets: Dict[str, Dict[str, int]] = defaultdict(lambda: defaultdict(int))
        for asset in self._store["assets"]:
            for field in fields:
                value = getattr(asset, field, None)
                key = value or "(unset)"
                facets[field][key] += 1
        # Convert defaultdicts to vanilla dicts for serialization friendliness.
        return {facet: dict(counts) for facet, counts in facets.items()}

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
