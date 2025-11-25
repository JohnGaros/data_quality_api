"""View models for Data Docs.

These models present human-readable summaries of contracts, job definitions,
and runs. They do not store configuration; they render existing ground truth
from contracts, libraries, catalog, jobs, and metadata.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime
from typing import Any, Dict, List, Optional


@dataclass
class RuleDoc:
    """Human-readable rule description."""

    rule_id: str
    name: Optional[str] = None
    description: Optional[str] = None
    severity: Optional[str] = None
    scope: Optional[str] = None  # dataset/column
    parameters: Dict[str, Any] = field(default_factory=dict)


@dataclass
class ColumnDoc:
    """Column schema documentation."""

    name: str
    data_type: str
    required: bool = False
    description: Optional[str] = None
    constraints: Dict[str, Any] = field(default_factory=dict)
    catalog_attribute: Optional[str] = None
    tags: List[str] = field(default_factory=list)


@dataclass
class DatasetDoc:
    """Dataset-level documentation within a contract."""

    dataset_type: str
    description: Optional[str] = None
    columns: List[ColumnDoc] = field(default_factory=list)
    rules: List[RuleDoc] = field(default_factory=list)
    governance: Dict[str, Any] = field(default_factory=dict)


@dataclass
class ContractDoc:
    """DataContract documentation view."""

    contract_id: str
    name: Optional[str]
    version: Optional[str]
    tenant: str
    environment: str
    status: Optional[str] = None
    datasets: List[DatasetDoc] = field(default_factory=list)
    rule_templates: List[RuleDoc] = field(default_factory=list)
    governance: Dict[str, Any] = field(default_factory=dict)
    metadata: Dict[str, Any] = field(default_factory=dict)


@dataclass
class ActionProfileDoc:
    """Action profile summary attached to jobs/runs."""

    action_profile_id: str
    name: Optional[str] = None
    action_type: Optional[str] = None
    status: Optional[str] = None
    metadata: Dict[str, Any] = field(default_factory=dict)


@dataclass
class JobDefinitionDoc:
    """JobDefinition/Checkpoint documentation view."""

    job_definition_id: str
    name: Optional[str]
    tenant: str
    environment: str
    description: Optional[str] = None
    dataset_type: Optional[str] = None
    contract_id: Optional[str] = None
    contract_version: Optional[str] = None
    trigger: Optional[str] = None
    tags: List[str] = field(default_factory=list)
    action_profiles: List[ActionProfileDoc] = field(default_factory=list)
    metadata: Dict[str, Any] = field(default_factory=dict)


@dataclass
class ProfilingSummaryDoc:
    """Profiling summary for a run."""

    record_count: int
    field_summaries: Dict[str, Dict[str, Any]] = field(default_factory=dict)


@dataclass
class ValidationSummaryDoc:
    """Validation summary for a run."""

    status: str
    rule_results: List[Dict[str, Any]] = field(default_factory=list)
    failure_rate: Optional[float] = None


@dataclass
class CleansingSummaryDoc:
    """Cleansing summary for a run."""

    applied: bool
    rule_set: Optional[str] = None
    before_counts: Dict[str, Any] = field(default_factory=dict)
    after_counts: Dict[str, Any] = field(default_factory=dict)
    rejected_count: Optional[int] = None


@dataclass
class RunDoc:
    """Run-level documentation view."""

    run_id: str
    job_definition_id: Optional[str]
    contract_id: Optional[str]
    contract_version: Optional[str]
    tenant: str
    environment: str
    started_at: Optional[datetime] = None
    completed_at: Optional[datetime] = None
    ingestion: Dict[str, Any] = field(default_factory=dict)
    cleansing: Optional[CleansingSummaryDoc] = None
    profiling: Optional[ProfilingSummaryDoc] = None
    validation: Optional[ValidationSummaryDoc] = None
    actions: List[ActionProfileDoc] = field(default_factory=list)
    metadata: Dict[str, Any] = field(default_factory=dict)


@dataclass
class ContractDiffDoc:
    """Stub for contract diff documentation between versions."""

    contract_id: str
    from_version: str
    to_version: str
    changes: Dict[str, Any] = field(default_factory=dict)


@dataclass
class RuleUsageDoc:
    """Stub for rule-centric documentation."""

    rule_template_id: str
    name: Optional[str] = None
    severity: Optional[str] = None
    description: Optional[str] = None
    used_in_contracts: List[str] = field(default_factory=list)
    used_in_datasets: List[str] = field(default_factory=list)
