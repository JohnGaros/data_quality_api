from __future__ import annotations

from typing import Any, Dict, Iterable, List, Optional, Literal

from pydantic import BaseModel, Field


class ValueFrequency(BaseModel):
    """Frequency metadata for a given value."""

    value: Any
    count: int
    percentage: float


class DistributionBucket(BaseModel):
    """Histogram bucket for numeric fields."""

    start: float
    end: float
    count: int
    percentage: float


class DistributionSummary(BaseModel):
    """Generic distribution descriptor."""

    kind: Literal["numeric", "categorical"]
    buckets: List[DistributionBucket] = Field(default_factory=list)
    values: List[ValueFrequency] = Field(default_factory=list)


class ProfilingFieldStats(BaseModel):
    """Basic statistics stored per logical field."""

    field_name: str
    non_null: int = 0
    nulls: int = 0
    distinct: int = 0
    sample_values: List[Any] = Field(default_factory=list)
    min_value: Optional[float] = None
    max_value: Optional[float] = None
    mean: Optional[float] = None
    stddev: Optional[float] = None
    frequent_values: List[ValueFrequency] = Field(default_factory=list)
    distribution: Optional[DistributionSummary] = None
    thresholds: Dict[str, Any] = Field(
        default_factory=dict,
        description="Dynamic thresholds derived from historical profiling runs.",
    )


class ProfilingSnapshot(BaseModel):
    """Collection of profiling metrics used to build validation contexts."""

    snapshot_id: str
    tenant_id: str
    dataset_type: str
    record_count: int
    generated_from: str = Field(
        default="raw",
        description="Whether the snapshot used raw or cleansed data as input.",
    )
    field_stats: Dict[str, ProfilingFieldStats] = Field(default_factory=dict)
    overrides_applied: Dict[str, Any] = Field(default_factory=dict)

    def merge_overrides(self, overrides: Optional[Dict[str, Any]]) -> "ProfilingSnapshot":
        """Return a copy with overrides folded into `overrides_applied`."""
        if not overrides:
            return self

        merged = self.copy(deep=True)
        merged.overrides_applied.update(overrides)

        for field_name, field_override in overrides.items():
            stats = merged.field_stats.setdefault(
                field_name,
                ProfilingFieldStats(field_name=field_name),
            )
            thresholds = field_override.get("thresholds") if isinstance(field_override, dict) else None
            if thresholds:
                stats.thresholds.update(thresholds)
        return merged

    def iter_fields(self) -> Iterable[ProfilingFieldStats]:
        """Convenience iterator for callers that need to scan stats."""
        return self.field_stats.values()
