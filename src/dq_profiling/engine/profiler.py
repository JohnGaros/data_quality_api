from __future__ import annotations

from typing import Any, Dict, Iterable, List, MutableMapping, Set

from ..models.profiling_job import ProfilingJob, ProfilingJobResult, ProfilingJobStatus
from ..models.profiling_snapshot import ProfilingFieldStats, ProfilingSnapshot

DatasetRow = Dict[str, Any]
Dataset = Iterable[DatasetRow]


class ProfilingEngine:
    """Produces profiling snapshots that feed validation contexts."""

    def __init__(self, sample_size: int = 5) -> None:
        self._sample_size = sample_size

    def profile(self, job: ProfilingJob, dataset: Dataset) -> ProfilingJobResult:
        """Profile the dataset and return a structured result."""
        record_count = 0
        aggregates: Dict[str, MutableMapping[str, Any]] = {}

        for row in dataset:
            record_count += 1
            for field_name, value in row.items():
                accumulator = aggregates.setdefault(
                    field_name,
                    {
                        "non_null": 0,
                        "nulls": 0,
                        "distinct_values": set(),
                        "sample_values": [],
                    },
                )
                if value in (None, ""):
                    accumulator["nulls"] += 1
                else:
                    accumulator["non_null"] += 1
                    distinct_values: Set[Any] = accumulator["distinct_values"]
                    distinct_values.add(value)
                    sample_values: List[Any] = accumulator["sample_values"]
                    if len(sample_values) < self._sample_size:
                        sample_values.append(value)

        field_stats = {
            field_name: ProfilingFieldStats(
                field_name=field_name,
                non_null=accumulator["non_null"],
                nulls=accumulator["nulls"],
                distinct=len(accumulator["distinct_values"]),
                sample_values=list(accumulator["sample_values"]),
            )
            for field_name, accumulator in aggregates.items()
        }

        snapshot = ProfilingSnapshot(
            snapshot_id=f"profile-{job.job_id}",
            tenant_id=job.tenant_id,
            dataset_type=job.dataset_type,
            record_count=record_count,
            generated_from="cleansed" if job.metadata.get("input") == "cleansed" else "raw",
            field_stats=field_stats,
        )

        return ProfilingJobResult(
            job_id=job.job_id,
            status=ProfilingJobStatus.SUCCEEDED,
            profiling_context_id=snapshot.snapshot_id,
            snapshot=snapshot,
            warnings=self._build_warnings(snapshot),
        )

    def _build_warnings(self, snapshot: ProfilingSnapshot) -> List[str]:
        """Emit basic warnings to help operators inspect anomalies."""
        warnings: List[str] = []
        if snapshot.record_count == 0:
            warnings.append("Dataset contained zero rows; downstream validation will skip.")
        for field_name, stats in snapshot.field_stats.items():
            if stats.nulls and stats.non_null == 0:
                warnings.append(f"Field '{field_name}' is entirely null values.")
        return warnings
