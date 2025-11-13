from __future__ import annotations

from typing import Any, Dict, Optional

from pydantic import BaseModel, Field

from ..models.profiling_job import ProfilingJob
from ..models.profiling_snapshot import ProfilingSnapshot


class ProfilingContext(BaseModel):
    """Normalized view of profiling metrics consumed by the rule engine."""

    profiling_context_id: str
    tenant_id: str
    dataset_type: str
    record_count: int
    field_thresholds: Dict[str, Dict[str, Any]] = Field(default_factory=dict)
    metadata: Dict[str, Any] = Field(default_factory=dict)


class ProfilingContextBuilder:
    """Generates rule-engine-friendly contexts from profiling snapshots."""

    def build(
        self,
        snapshot: ProfilingSnapshot,
        job: Optional[ProfilingJob] = None,
    ) -> ProfilingContext:
        """Create a context by combining snapshot stats with job overrides."""
        overrides = job.overrides if job else None
        effective_snapshot = snapshot.merge_overrides(overrides)

        thresholds = {
            field_name: stats.thresholds
            for field_name, stats in effective_snapshot.field_stats.items()
        }

        metadata = {
            "generated_from": effective_snapshot.generated_from,
            "overrides": effective_snapshot.overrides_applied,
        }
        if job:
            metadata["profiling_job_id"] = job.job_id
            metadata["source_dataset_uri"] = job.source_dataset_uri

        return ProfilingContext(
            profiling_context_id=effective_snapshot.snapshot_id,
            tenant_id=effective_snapshot.tenant_id,
            dataset_type=effective_snapshot.dataset_type,
            record_count=effective_snapshot.record_count,
            field_thresholds=thresholds,
            metadata=metadata,
        )
