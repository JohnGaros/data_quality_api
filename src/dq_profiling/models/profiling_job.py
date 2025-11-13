from __future__ import annotations

from datetime import datetime
from enum import Enum
from typing import Any, Dict, List, Optional

from pydantic import BaseModel, Field

from .profiling_snapshot import ProfilingSnapshot


class ProfilingJobStatus(str, Enum):
    """Lifecycle states for profiling jobs."""

    PLANNED = "planned"
    RUNNING = "running"
    SUCCEEDED = "succeeded"
    FAILED = "failed"
    CANCELLED = "cancelled"


class ProfilingJob(BaseModel):
    """Request envelope for profiling a dataset before validation."""

    job_id: str
    tenant_id: str
    dataset_type: str
    source_dataset_uri: Optional[str] = Field(
        default=None,
        description="Pointer to the dataset that should be profiled (raw or cleansed).",
    )
    requested_at: datetime = Field(default_factory=datetime.utcnow)
    overrides: Dict[str, Any] = Field(
        default_factory=dict,
        description="Per-field overrides (e.g., tighter thresholds) supplied by callers.",
    )
    priority: int = Field(default=0, ge=0)
    metadata: Dict[str, Any] = Field(default_factory=dict)


class ProfilingJobResult(BaseModel):
    """Result emitted by the profiling engine."""

    job_id: str
    status: ProfilingJobStatus
    profiling_context_id: str
    profiled_at: datetime = Field(default_factory=datetime.utcnow)
    snapshot: ProfilingSnapshot
    warnings: List[str] = Field(default_factory=list)

    def summary(self) -> Dict[str, Any]:
        """Compact structure for API responses and metadata events."""
        return {
            "job_id": self.job_id,
            "status": self.status.value,
            "profiling_context_id": self.profiling_context_id,
            "profiled_at": self.profiled_at.isoformat(),
            "warnings": self.warnings,
            "snapshot": self.snapshot.dict(),
        }
