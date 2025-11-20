"""Pydantic models describing first-class data contracts."""

from __future__ import annotations

from datetime import datetime
from enum import Enum
from typing import Any, Dict, List, Optional, Union

from pydantic import BaseModel, Field, model_validator

ParameterValue = Union[str, int, float, bool, List[str], Dict[str, Any]]


class Environment(str, Enum):
    """Supported deployment environments for a contract."""

    DEV = "dev"
    TEST = "test"
    PROD = "prod"


class RuleType(str, Enum):
    """Categories of rule templates supported by the engines."""

    VALIDATION = "validation"
    CLEANSING = "cleansing"
    PROFILING = "profiling"


class RuleBindingTargetScope(str, Enum):
    """Scope for a rule binding."""

    DATASET = "dataset"
    COLUMN = "column"


class RuleParameter(BaseModel):
    """Key/value parameter used by rule templates and bindings."""

    name: str = Field(..., description="Parameter key as expected by the rule implementation.")
    value: ParameterValue = Field(..., description="Parameter value.")
    value_type: Optional[str] = Field(
        None,
        description="Optional hint describing the expected type (string, number, percent, etc.).",
    )
    description: Optional[str] = Field(None, description="Human readable explanation of the parameter.")


class RuleTemplate(BaseModel):
    """Registry entry for a reusable rule template."""

    rule_template_id: str = Field(..., description="Unique identifier for the template.")
    name: str = Field(..., description="Friendly rule name.")
    rule_type: RuleType = Field(..., description="Indicates validation, cleansing, or profiling.")
    dataset_type: Optional[str] = Field(None, description="Canonical dataset type the template targets.")
    version: str = Field(..., description="Template version.")
    severity: Optional[str] = Field(None, description="Severity used by downstream reporting (hard/soft/etc.).")
    source_module: str = Field(..., description="Owning module (dq_core, dq_cleansing, dq_profiling).")
    description: Optional[str] = Field(None, description="What the template enforces.")
    default_parameters: List[RuleParameter] = Field(
        default_factory=list,
        description="Parameters applied when bindings do not override values.",
    )
    parameter_schema: Dict[str, Any] = Field(
        default_factory=dict,
        description="JSON schema describing parameter structure for validation.",
    )
    tags: List[str] = Field(default_factory=list, description="Searchable labels/categories.")
    deprecated: bool = Field(False, description="Whether the template is retired.")
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)


class ActivationWindow(BaseModel):
    """Timeboxed activation for a rule binding."""

    start_at: Optional[datetime] = Field(None, description="Optional start timestamp.")
    end_at: Optional[datetime] = Field(None, description="Optional end timestamp.")

    @model_validator(mode="after")
    def validate_window(self) -> "ActivationWindow":
        """Basic guard to ensure the activation window is valid."""

        if self.start_at and self.end_at and self.end_at <= self.start_at:
            raise ValueError("activation window end_at must be after start_at")
        return self


class RuleBinding(BaseModel):
    """Connects a rule template to a dataset or column scope."""

    binding_id: str = Field(..., description="Unique identifier for the binding.")
    tenant_id: str = Field(..., description="Tenant that owns this binding.")
    environment: Environment = Field(..., description="Environment where the binding is active.")
    rule_template_id: str = Field(..., description="Reference to the rule template.")
    rule_type: RuleType = Field(..., description="Denormalized template type for quick filtering.")
    target_scope: RuleBindingTargetScope = Field(..., description="Dataset or column scope.")
    target_id: str = Field(
        ...,
        description="Dataset contract ID or column contract ID depending on the scope.",
    )
    parameters: List[RuleParameter] = Field(
        default_factory=list,
        description="Overrides applied to the template when executing this binding.",
    )
    priority: int = Field(
        0,
        description="Execution order hint when multiple bindings apply to the same scope.",
    )
    enabled: bool = Field(True, description="Soft-toggle without deleting the binding.")
    activation_window: Optional[ActivationWindow] = Field(
        None,
        description="Optional window constraining when the binding is active.",
    )
    notes: Optional[str] = Field(None, description="Change rationale or reviewer notes.")
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)


class ColumnConstraint(BaseModel):
    """Schema-level constraints applied to a column."""

    required: bool = Field(False, description="Whether the column must exist and be non-null.")
    unique: bool = Field(False, description="Whether the column values must be unique per dataset.")
    min_value: Optional[float] = Field(None, description="Minimum numeric threshold.")
    max_value: Optional[float] = Field(None, description="Maximum numeric threshold.")
    regex: Optional[str] = Field(None, description="Regular expression format enforcement.")
    allowed_values: List[str] = Field(default_factory=list, description="Enumerated set of acceptable values.")
    min_length: Optional[int] = Field(None, description="Minimum string length.")
    max_length: Optional[int] = Field(None, description="Maximum string length.")
    disallow_nulls: bool = Field(False, description="Convenience flag for nullability expectations.")


class ProfilingExpectation(BaseModel):
    """Desired profiling thresholds for a column."""

    metric: str = Field(..., description="Metric name (null_ratio, min, max, stddev, etc.).")
    min_threshold: Optional[float] = Field(None, description="Acceptable lower bound.")
    max_threshold: Optional[float] = Field(None, description="Acceptable upper bound.")
    change_tolerance_pct: Optional[float] = Field(
        None,
        description="Allowed delta compared to previous run (percentage).",
    )


class SchemaRegistryRef(BaseModel):
    """Links a dataset contract to an external schema registry."""

    subject: str = Field(..., description="Schema registry subject or identifier.")
    version: str = Field(..., description="Registered version.")
    registry_type: str = Field(..., description="e.g., confluent, azure_schema_registry.")
    uri: Optional[str] = Field(None, description="HTTPS endpoint for the schema registry.")


class ColumnContract(BaseModel):
    """Describes a single column within a dataset contract."""

    column_id: str = Field(..., description="Unique identifier within the contract.")
    logical_field_key: str = Field(..., description="Reference to dq_core logical field catalog.")
    display_name: Optional[str] = Field(None, description="External-friendly column name.")
    aliases: List[str] = Field(default_factory=list, description="Tenant-specific column names.")
    data_type: str = Field(..., description="Declared data type (string, decimal, date, etc.).")
    description: Optional[str] = Field(None, description="Purpose of the column.")
    required: bool = Field(True, description="Whether the column must be delivered by producers.")
    default_value: Optional[ParameterValue] = Field(None, description="Optional default value for missing data.")
    format: Optional[str] = Field(None, description="Format hint (ISO-8601, currency, etc.).")
    constraints: ColumnConstraint = Field(default_factory=ColumnConstraint)
    profiling_expectations: List[ProfilingExpectation] = Field(
        default_factory=list,
        description="Profiling thresholds tied to this column.",
    )
    sensitivity_tags: List[str] = Field(default_factory=list, description="Compliance tags applied to this column.")
    metadata: Dict[str, Any] = Field(default_factory=dict, description="Custom column attributes.")


class IndexDefinition(BaseModel):
    """Declarative index for the dataset."""

    name: str = Field(..., description="Index identifier.")
    fields: List[str] = Field(..., description="Column IDs participating in the index.")
    unique: bool = Field(False, description="Whether the index enforces uniqueness.")


class QualitySLO(BaseModel):
    """Service-level objective associated with a dataset."""

    metric: str = Field(..., description="Metric code, e.g., hard_failure_rate.")
    target: float = Field(..., description="Target threshold or percentage.")
    period_days: int = Field(30, description="SLO evaluation window.")


class DatasetContract(BaseModel):
    """Dataset-level schema and governance definition."""

    dataset_contract_id: str = Field(..., description="Unique identifier for the dataset contract.")
    dataset_type: str = Field(..., description="Canonical dataset category (billing, payments, etc.).")
    tenant_id: str = Field(..., description="Tenant owning the dataset.")
    environment: Environment = Field(..., description="Environment where the dataset contract is active.")
    version: str = Field(..., description="Dataset contract version.")
    description: Optional[str] = Field(None, description="Purpose of the dataset.")
    owner: Optional[str] = Field(None, description="Business owner or steward.")
    columns: List[ColumnContract] = Field(default_factory=list, description="Ordered column definitions.")
    primary_keys: List[str] = Field(default_factory=list, description="Column IDs that compose the primary key.")
    indexes: List[IndexDefinition] = Field(default_factory=list, description="Optional secondary indexes.")
    classification: Optional[str] = Field(None, description="Compliance classification.")
    retention_policy_id: Optional[str] = Field(None, description="Policy controlling retention/deletion.")
    schema_hash: Optional[str] = Field(None, description="Hash to detect schema drift.")
    depends_on_dataset_contract_ids: List[str] = Field(
        default_factory=list,
        description="References to upstream dataset contracts.",
    )
    schema_registry_ref: Optional[SchemaRegistryRef] = Field(
        None,
        description="Optional schema registry linkage for streaming integrations.",
    )
    quality_slos: List[QualitySLO] = Field(default_factory=list, description="SLO definitions for the dataset.")
    metadata: Dict[str, Any] = Field(default_factory=dict, description="Arbitrary dataset-level metadata.")
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)


class LifecycleEvent(BaseModel):
    """Individual lifecycle entry (draft, approval, retirement)."""

    status: str = Field(..., description="Lifecycle status label.")
    actor: Optional[str] = Field(None, description="Who performed the action.")
    notes: Optional[str] = Field(None, description="Reasoning or ticket reference.")
    occurred_at: datetime = Field(default_factory=datetime.utcnow)


class PromotionRecord(BaseModel):
    """Captures environment promotion metadata."""

    from_environment: Environment = Field(..., description="Source environment (dev/test).")
    to_environment: Environment = Field(..., description="Target environment (test/prod).")
    promoted_by: str = Field(..., description="Actor approving/pushing the promotion.")
    promoted_at: datetime = Field(default_factory=datetime.utcnow)
    notes: Optional[str] = Field(None, description="Change ticket / rollout note.")


class ContractStatus(str, Enum):
    """High-level lifecycle states for contracts."""

    DRAFT = "draft"
    PENDING_APPROVAL = "pending_approval"
    APPROVED = "approved"
    RETIRED = "retired"


class ContractLifecycle(BaseModel):
    """Lifecycle metadata for a contract."""

    status: ContractStatus = Field(ContractStatus.DRAFT, description="Current lifecycle state.")
    created_by: Optional[str] = Field(None, description="Author of the draft.")
    approved_by: Optional[str] = Field(None, description="Approver once status=approved.")
    approval_notes: Optional[str] = Field(None, description="Optional approval justification.")
    events: List[LifecycleEvent] = Field(default_factory=list, description="History of lifecycle changes.")
    promotion_history: List[PromotionRecord] = Field(
        default_factory=list,
        description="Environment promotion audit trail.",
    )
    supersedes_contract_id: Optional[str] = Field(None, description="Previous contract replaced by this one.")


class DataContract(BaseModel):
    """Top-level data contract definition for a tenant."""

    contract_id: str = Field(..., description="Unique identifier for the contract.")
    tenant_id: str = Field(..., description="Tenant that owns the contract.")
    environment: Environment = Field(..., description="Environment for this contract revision.")
    version: str = Field(..., description="Contract semantic version.")
    name: str = Field(..., description="Friendly contract name.")
    description: Optional[str] = Field(None, description="Purpose / summary of the contract.")
    datasets: List[DatasetContract] = Field(default_factory=list, description="Dataset contracts covered.")
    rule_templates: List[RuleTemplate] = Field(
        default_factory=list,
        description="Embedded rule templates (optional for global catalog references).",
    )
    rule_bindings: List[RuleBinding] = Field(
        default_factory=list,
        description="Bindings linking rule templates to dataset/column scopes.",
    )
    metadata: Dict[str, Any] = Field(
        default_factory=dict,
        description="Arbitrary metadata (lineage pointers, approval ticket, etc.).",
    )
    lifecycle: ContractLifecycle = Field(default_factory=ContractLifecycle)
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)

    def dataset_contract_by_type(self, dataset_type: str) -> Optional[DatasetContract]:
        """Helper to locate a dataset contract by canonical dataset type."""

        dataset_type_lower = dataset_type.lower()
        for dataset in self.datasets:
            if dataset.dataset_type.lower() == dataset_type_lower:
                return dataset
        return None
