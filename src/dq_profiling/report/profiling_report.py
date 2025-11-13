from __future__ import annotations

import csv
import io
import json
from dataclasses import dataclass
from datetime import datetime
from typing import Any, Dict, Iterable, List, Optional

from ..models.profiling_job import ProfilingJobResult
from ..models.profiling_snapshot import ProfilingFieldStats


def _serialize(value: Any) -> str:
    """Best-effort JSON serialization for CSV output."""
    try:
        return json.dumps(value, default=str)
    except TypeError:
        return str(value)


@dataclass
class FieldSummary:
    """Roll-up of profiling metrics per field."""

    name: str
    non_null: int
    nulls: int
    distinct: int
    sample_values: List[Any]
    min_value: Optional[float]
    max_value: Optional[float]
    mean: Optional[float]
    stddev: Optional[float]
    frequent_values: List[Dict[str, Any]]
    distribution: Optional[Dict[str, Any]]
    thresholds: Dict[str, Any]

    @classmethod
    def from_stats(cls, stats: ProfilingFieldStats) -> "FieldSummary":
        distribution = None
        if stats.distribution:
            distribution = {
                "kind": stats.distribution.kind,
                "buckets": [bucket.dict() for bucket in stats.distribution.buckets],
                "values": [freq.dict() for freq in stats.distribution.values],
            }

        return cls(
            name=stats.field_name,
            non_null=stats.non_null,
            nulls=stats.nulls,
            distinct=stats.distinct,
            sample_values=stats.sample_values,
            min_value=stats.min_value,
            max_value=stats.max_value,
            mean=stats.mean,
            stddev=stats.stddev,
            frequent_values=[freq.dict() for freq in stats.frequent_values],
            distribution=distribution,
            thresholds=stats.thresholds,
        )

    def to_dict(self) -> Dict[str, Any]:
        return {
            "name": self.name,
            "non_null": self.non_null,
            "nulls": self.nulls,
            "distinct": self.distinct,
            "sample_values": self.sample_values,
            "min_value": self.min_value,
            "max_value": self.max_value,
            "mean": self.mean,
            "stddev": self.stddev,
            "frequent_values": self.frequent_values,
            "distribution": self.distribution,
            "thresholds": self.thresholds,
        }


@dataclass
class ProfilingReport:
    """Human-readable summary produced from a profiling job result."""

    job_id: str
    profiling_context_id: str
    status: str
    profiled_at: datetime
    record_count: int
    generated_from: str
    field_summaries: List[FieldSummary]
    warnings: List[str]

    def to_dict(self) -> Dict[str, Any]:
        """Return a JSON-serializable dictionary for API responses."""
        return {
            "job_id": self.job_id,
            "profiling_context_id": self.profiling_context_id,
            "status": self.status,
            "profiled_at": self.profiled_at.isoformat(),
            "record_count": self.record_count,
            "generated_from": self.generated_from,
            "warnings": self.warnings,
            "fields": [field.to_dict() for field in self.field_summaries],
        }

    def to_rows(self) -> Iterable[List[Any]]:
        """Yield row data suitable for CSV/Excel exports."""
        yield [
            "field_name",
            "non_null",
            "nulls",
            "distinct",
            "min",
            "max",
            "mean",
            "stddev",
            "frequent_values",
            "distribution",
            "sample_values",
            "thresholds",
        ]
        for field in self.field_summaries:
            yield [
                field.name,
                field.non_null,
                field.nulls,
                field.distinct,
                field.min_value,
                field.max_value,
                field.mean,
                field.stddev,
                _serialize(field.frequent_values),
                _serialize(field.distribution) if field.distribution else "",
                "|".join(map(str, field.sample_values)),
                field.thresholds,
            ]


def profiling_report_from_result(result: ProfilingJobResult) -> ProfilingReport:
    """Convert a ProfilingJobResult into a ProfilingReport."""

    snapshot = result.snapshot
    field_summaries = [
        FieldSummary.from_stats(stats) for stats in snapshot.iter_fields()
    ]
    return ProfilingReport(
        job_id=result.job_id,
        profiling_context_id=result.profiling_context_id,
        status=result.status.value,
        profiled_at=result.profiled_at,
        record_count=snapshot.record_count,
        generated_from=snapshot.generated_from,
        field_summaries=field_summaries,
        warnings=result.warnings,
    )


def export_report_to_csv(report: ProfilingReport) -> str:
    """Return a CSV string representing the profiling report."""

    buffer = io.StringIO()
    writer = csv.writer(buffer)
    for row in report.to_rows():
        writer.writerow(row)
    return buffer.getvalue()
