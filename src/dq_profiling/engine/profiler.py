from __future__ import annotations

from collections import Counter
from typing import Any, Dict, Iterable, List, MutableMapping

from ..models.profiling_job import ProfilingJob, ProfilingJobResult, ProfilingJobStatus
from ..models.profiling_snapshot import (
    DistributionBucket,
    DistributionSummary,
    ProfilingFieldStats,
    ProfilingSnapshot,
    ValueFrequency,
)
try:
    from dq_engine.base import ExecutionEngine
    from dq_engine.pandas_engine import PandasExecutionEngine
except Exception:  # pragma: no cover - optional dependency
    ExecutionEngine = None  # type: ignore
    PandasExecutionEngine = None  # type: ignore

DatasetRow = Dict[str, Any]
Dataset = Iterable[DatasetRow]


class ProfilingEngine:
    """Produces profiling snapshots that feed validation contexts."""

    def __init__(
        self,
        sample_size: int = 5,
        top_frequencies: int = 5,
        histogram_buckets: int = 5,
        execution_engine: "ExecutionEngine | None" = None,
    ) -> None:
        self._sample_size = sample_size
        self._top_frequencies = top_frequencies
        self._histogram_buckets = histogram_buckets
        # TODO: delegate profiling to execution engine when dataset handles are
        # available. Keep in-memory iterable-based implementation for now.
        self.execution_engine = execution_engine or (PandasExecutionEngine() if PandasExecutionEngine else None)

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
                        "sample_values": [],
                        "value_counts": Counter(),
                        "numeric_values": [],
                        "numeric_sum": 0.0,
                        "numeric_sum_sq": 0.0,
                        "numeric_min": None,
                        "numeric_max": None,
                    },
                )
                if self._is_null(value):
                    accumulator["nulls"] += 1
                    continue

                accumulator["non_null"] += 1
                accumulator["value_counts"][value] += 1

                if len(accumulator["sample_values"]) < self._sample_size:
                    accumulator["sample_values"].append(value)

                if self._is_numeric(value):
                    numeric_value = float(value)
                    accumulator["numeric_values"].append(numeric_value)
                    accumulator["numeric_sum"] += numeric_value
                    accumulator["numeric_sum_sq"] += numeric_value ** 2
                    accumulator["numeric_min"] = self._update_min(
                        accumulator["numeric_min"],
                        numeric_value,
                    )
                    accumulator["numeric_max"] = self._update_max(
                        accumulator["numeric_max"],
                        numeric_value,
                    )

        field_stats = {
            field_name: self._build_field_stats(
                field_name=field_name,
                accumulator=accumulator,
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

    def _build_field_stats(
        self,
        *,
        field_name: str,
        accumulator: MutableMapping[str, Any],
    ) -> ProfilingFieldStats:
        non_null = accumulator["non_null"]
        nulls = accumulator["nulls"]
        total_rows = non_null + nulls
        distinct = len(accumulator["value_counts"])

        frequent_values = self._build_value_frequencies(
            accumulator["value_counts"],
            total_rows,
            limit=self._top_frequencies,
        )
        distribution = self._build_distribution(
            accumulator["value_counts"],
            accumulator["numeric_values"],
            total_rows,
        )

        mean = None
        stddev = None
        if accumulator["numeric_values"] and non_null:
            mean = accumulator["numeric_sum"] / non_null
            variance = (accumulator["numeric_sum_sq"] / non_null) - (mean ** 2)
            stddev = (variance if variance > 0 else 0) ** 0.5

        return ProfilingFieldStats(
            field_name=field_name,
            non_null=non_null,
            nulls=nulls,
            distinct=distinct,
            sample_values=list(accumulator["sample_values"]),
            min_value=accumulator["numeric_min"],
            max_value=accumulator["numeric_max"],
            mean=mean,
            stddev=stddev,
            frequent_values=frequent_values,
            distribution=distribution,
        )

    def _build_value_frequencies(
        self,
        counts: Counter,
        total_rows: int,
        *,
        limit: int | None = None,
    ) -> List[ValueFrequency]:
        most_common = counts.most_common(limit)
        return [
            ValueFrequency(
                value=value,
                count=count,
                percentage=self._percentage(count, total_rows),
            )
            for value, count in most_common
        ]

    def _build_distribution(
        self,
        counts: Counter,
        numeric_values: List[float],
        total_rows: int,
    ) -> DistributionSummary | None:
        if numeric_values:
            buckets = self._build_numeric_buckets(numeric_values, total_rows)
            return DistributionSummary(kind="numeric", buckets=buckets)
        if counts:
            values = self._build_value_frequencies(counts, total_rows, limit=None)
            return DistributionSummary(kind="categorical", values=values)
        return None

    def _build_numeric_buckets(
        self,
        values: List[float],
        total_rows: int,
    ) -> List[DistributionBucket]:
        if not values:
            return []

        min_value = min(values)
        max_value = max(values)
        if min_value == max_value:
            return [
                DistributionBucket(
                    start=min_value,
                    end=max_value,
                    count=len(values),
                    percentage=self._percentage(len(values), total_rows),
                )
            ]

        bucket_count = min(self._histogram_buckets, max(1, len(values)))
        width = (max_value - min_value) / bucket_count or 1

        bucket_ranges = [
            {
                "start": min_value + index * width,
                "end": max_value if index == bucket_count - 1 else min_value + (index + 1) * width,
                "count": 0,
            }
            for index in range(bucket_count)
        ]

        for value in values:
            if value == max_value:
                bucket_index = bucket_count - 1
            else:
                bucket_index = int((value - min_value) / width)
            bucket_ranges[bucket_index]["count"] += 1

        return [
            DistributionBucket(
                start=round(bucket["start"], 6),
                end=round(bucket["end"], 6),
                count=bucket["count"],
                percentage=self._percentage(bucket["count"], total_rows),
            )
            for bucket in bucket_ranges
            if bucket["count"] > 0
        ]

    def _percentage(self, count: int, total: int) -> float:
        if total == 0:
            return 0.0
        return round((count / total) * 100, 4)

    def _is_null(self, value: Any) -> bool:
        return value is None or value == ""

    def _is_numeric(self, value: Any) -> bool:
        return isinstance(value, (int, float)) and not isinstance(value, bool)

    def _update_min(self, current: float | None, value: float) -> float:
        if current is None or value < current:
            return value
        return current

    def _update_max(self, current: float | None, value: float) -> float:
        if current is None or value > current:
            return value
        return current

    def _build_warnings(self, snapshot: ProfilingSnapshot) -> List[str]:
        """Emit basic warnings to help operators inspect anomalies."""
        warnings: List[str] = []
        if snapshot.record_count == 0:
            warnings.append("Dataset contained zero rows; downstream validation will skip.")
        for field_name, stats in snapshot.field_stats.items():
            if stats.nulls and stats.non_null == 0:
                warnings.append(f"Field '{field_name}' is entirely null values.")
        return warnings
