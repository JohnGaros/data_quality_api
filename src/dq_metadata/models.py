"""Pydantic models representing metadata entities captured for governance."""

from datetime import datetime
from typing import Any, Dict, List, Optional
from uuid import UUID

from pydantic import BaseModel, Field


class FieldMetadata(BaseModel):
    """Describes a single field/column within a registered data asset."""

    name: str = Field(..., description="Field name as presented to consumers.")
    data_type: str = Field(..., description="Logical or physical data type (e.g., string, decimal).")
    description: Optional[str] = Field(None, description="Human friendly description of the field.")


class UsageStats(BaseModel):
    """Tracks access statistics that power catalog popularity metrics."""

    access_count: int = Field(0, description="Number of times this asset was accessed.")
    last_accessed: Optional[datetime] = Field(None, description="Timestamp when the asset was last accessed.")


class DataAssetMetadata(BaseModel):
    """Describes a dataset registered with the platform."""

    asset_id: UUID = Field(..., description="Unique identifier for the data asset.")
    tenant_id: str = Field(..., description="Tenant that owns the data asset.")
    name: Optional[str] = Field(None, description="Friendly name for the dataset as displayed in the catalog.")
    dataset_type: str = Field(..., description="Canonical dataset category (billing, payments, etc.).")
    schema_signature: str = Field(..., description="Hash of logical field definitions for lineage.")
    classification: Optional[str] = Field(None, description="Compliance classifier (e.g., PII, confidential).")
    retention_policy_id: Optional[str] = Field(None, description="Reference to retention policy applied.")
    owner: Optional[str] = Field(None, description="Business owner or steward of the data asset.")
    fields: List[FieldMetadata] = Field(default_factory=list, description="Field-level metadata for discovery.")
    data_source: Optional[str] = Field(None, description="System of origin (e.g., Dynamics, SAP, custom feed).")
    usage_stats: UsageStats = Field(default_factory=UsageStats, description="Usage/popularity metrics.")
    custom_attributes: Dict[str, Any] = Field(default_factory=dict, description="Arbitrary catalog-ready attributes.")
    parent_asset_ids: List[UUID] = Field(
        default_factory=list,
        description="Asset IDs that this asset derives from (parent datasets).",
    )
    child_asset_ids: List[UUID] = Field(
        default_factory=list,
        description="Asset IDs derived from this asset (child datasets).",
    )
    related_asset_ids: List[UUID] = Field(
        default_factory=list,
        description="Cross-asset lineage links (e.g., joins, references).",
    )
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)


class ValidationJobMetadata(BaseModel):
    """Tracks lineage information for validation jobs."""

    job_id: str = Field(..., description="Validation job identifier.")
    tenant_id: str = Field(..., description="Tenant associated with this job.")
    submission_source: str = Field(..., description="Entry point (API, UI, automation).")
    ingestion_mode: Optional[str] = Field(None, description="How the job was ingested (direct_upload, external_reference, automation, etc.).")
    config_version: Optional[str] = Field(None, description="Configuration version applied.")
    status: str = Field(..., description="Current job status (pending, running, etc.).")
    input_assets: List[UUID] = Field(default_factory=list, description="Assets that fed into the job.")
    output_report_uri: Optional[str] = Field(None, description="Storage location for generated reports.")
    checksum: Optional[str] = Field(None, description="Checksum of uploaded bundle for idempotency.")
    submitted_by: Optional[str] = Field(None, description="User or service that submitted the job.")
    submitted_at: datetime = Field(default_factory=datetime.utcnow)
    started_at: Optional[datetime] = None
    completed_at: Optional[datetime] = None
    metadata: Dict[str, str] = Field(default_factory=dict, description="Additional context key/value pairs.")


class RuleVersionMetadata(BaseModel):
    """Records version history for rules and mappings."""

    rule_version_id: UUID = Field(..., description="Unique identifier for the rule version.")
    rule_id: str = Field(..., description="Logical rule identifier.")
    expression_hash: str = Field(..., description="Hash of the rule expression for tamper checking.")
    severity: str = Field(..., description="Rule severity (hard, soft).")
    change_type: str = Field(..., description="Lifecycle event (create, update, retire).")
    changed_by: str = Field(..., description="User who performed the change.")
    approved_by: Optional[str] = Field(None, description="Approver of the change.")
    approved_at: Optional[datetime] = None
    effective_from: datetime = Field(default_factory=datetime.utcnow)
    effective_to: Optional[datetime] = None
    notes: Optional[str] = Field(None, description="Justification or release notes for the change.")


class AuditEventMetadata(BaseModel):
    """Captures audited actions across the platform."""

    event_id: UUID = Field(..., description="Unique audit event identifier.")
    actor_id: str = Field(..., description="User or service principal performing the action.")
    actor_role: str = Field(..., description="Role of actor (Admin, Configurator, etc.).")
    action_type: str = Field(..., description="What happened (tenant_created, token_issued, etc.).")
    resource_type: str = Field(..., description="Type of resource touched (tenant, rule, job).")
    resource_id: str = Field(..., description="Identifier of the resource.")
    context: Dict[str, str] = Field(default_factory=dict, description="Additional context details.")
    ip_address: Optional[str] = Field(None, description="Originating IP address if available.")
    initiated_at: datetime = Field(default_factory=datetime.utcnow)
    is_privileged: bool = Field(default=False, description="Whether the action required elevated permissions.")


class ComplianceTag(BaseModel):
    """Label applied to resources for compliance classification."""

    tag_id: UUID = Field(..., description="Unique identifier for the tag.")
    resource_type: str = Field(..., description="Type of resource tagged (asset, job, report).")
    resource_id: str = Field(..., description="Identifier of the tagged resource.")
    tag_key: str = Field(..., description="Classification key (e.g., PII, RETENTION_TIER).")
    tag_value: str = Field(..., description="Classification value.")
    source: str = Field(..., description="How the tag was assigned (manual, detection_rule).")
    assigned_by: Optional[str] = Field(None, description="Actor or service assigning the tag.")
    assigned_at: datetime = Field(default_factory=datetime.utcnow)
