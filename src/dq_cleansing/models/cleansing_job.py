from __future__ import annotations

from enum import Enum
from typing import Any, Dict, Optional

from pydantic import BaseModel, Field


class CleansingJobStatus(str, Enum):
    """Lifecycle states for cleansing jobs."""

    PLANNED = "planned"
    RUNNING = "running"
    SUCCEEDED = "succeeded"
    FAILED = "failed"
    SKIPPED = "skipped"


class CleansingJob(BaseModel):
    """Request payload representing a cleansing execution."""

    job_id: str
    tenant_id: str
    dataset_type: str
    rule_id: str
    rule_version: Optional[str] = None
    source_job_id: Optional[str] = Field(
        default=None,
        description="Upload job that produced the raw dataset.",
    )
    chain_validation: bool = Field(
        default=False,
        description="Automatically trigger validation with cleansed output.",
    )
    status: CleansingJobStatus = Field(default=CleansingJobStatus.PLANNED)
    options: Dict[str, Any] = Field(default_factory=dict)


class CleansingJobResult(BaseModel):
    """Result envelope returned by the cleansing engine."""

    job_id: str
    status: CleansingJobStatus
    before_counts: Dict[str, int]
    after_counts: Dict[str, int]
    rejected_sample: Dict[str, Any] = Field(default_factory=dict)
    output_dataset: Optional[str] = None
    linked_validation_job_id: Optional[str] = None
    metrics: Dict[str, Any] = Field(default_factory=dict)

    def to_report_dict(self) -> Dict[str, Any]:
        """Flatten for API responses."""
        return {
            "job_id": self.job_id,
            "status": self.status.value,
            "before_counts": self.before_counts,
            "after_counts": self.after_counts,
            "rejected_sample": self.rejected_sample,
            "output_dataset": self.output_dataset,
            "linked_validation_job_id": self.linked_validation_job_id,
            "metrics": self.metrics,
        }
