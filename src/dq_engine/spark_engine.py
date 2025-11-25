"""Stub for a Spark-backed execution engine."""

from __future__ import annotations

from typing import Any, Iterable, Mapping

from .base import DatasetHandle, ExecutionEngine


class SparkDatasetHandle:
    """Placeholder handle wrapping a Spark DataFrame or view reference."""

    def __init__(self, df: Any) -> None:
        self.df = df


class SparkExecutionEngine(ExecutionEngine):
    """Stub implementation for Spark; wiring will follow infra profile selection."""

    def load_dataset(self, source_ref: Mapping[str, Any]) -> DatasetHandle:
        raise NotImplementedError("Spark loading not implemented (docs/EXECUTION_ENGINES.md).")

    def persist_dataset(self, handle: DatasetHandle, target_ref: Mapping[str, Any]) -> Mapping[str, Any]:
        raise NotImplementedError("Spark persistence not implemented (docs/EXECUTION_ENGINES.md).")

    def apply_transformations(self, handle: DatasetHandle, transformations: Iterable[Any]) -> DatasetHandle:
        raise NotImplementedError("Spark transformations not implemented (docs/EXECUTION_ENGINES.md).")

    def compute_profile(self, handle: DatasetHandle, spec: Mapping[str, Any]) -> Mapping[str, Any]:
        raise NotImplementedError("Spark profiling not implemented (docs/EXECUTION_ENGINES.md).")

    def evaluate_rules(self, handle: DatasetHandle, rules_bundle: Mapping[str, Any]) -> Mapping[str, Any]:
        raise NotImplementedError("Spark rule evaluation not implemented (docs/EXECUTION_ENGINES.md).")
