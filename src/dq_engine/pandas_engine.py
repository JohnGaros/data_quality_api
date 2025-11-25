"""Pandas-backed execution engine.

This implementation is a minimal adapter to keep Pandas as the default backend
while making it easy to swap to Spark/SQL in future. Integration with
`dq_integration.azure_blob` and contract-driven infra profiles is left as a
TODO; configuration still comes from contracts + libraries + catalog.
"""

from __future__ import annotations

from typing import Any, Iterable, Mapping

import pandas as pd

from .base import DatasetHandle, ExecutionEngine


class PandasDatasetHandle:
    """DatasetHandle wrapper around a pandas DataFrame."""

    def __init__(self, df: pd.DataFrame) -> None:
        self.df = df


class PandasExecutionEngine(ExecutionEngine):
    """Default execution engine using pandas DataFrames."""

    def load_dataset(self, source_ref: Mapping[str, Any]) -> DatasetHandle:
        """
        Load dataset into a pandas DataFrame.

        TODO: integrate with `dq_integration.azure_blob` and infra profile hints
        for storage selection. See docs/ARCHITECTURE.md#2 for ingestion details.
        """

        raise NotImplementedError("Dataset loading for PandasExecutionEngine not wired (docs/ARCHITECTURE.md#2).")

    def persist_dataset(self, handle: DatasetHandle, target_ref: Mapping[str, Any]) -> Mapping[str, Any]:
        """
        Persist DataFrame to a target reference (e.g., blob path).

        TODO: delegate to dq_integration blob adapters once target selection is
        driven by infra profiles. See docs/CONTRACT_DRIVEN_ARCHITECTURE.md.
        """

        raise NotImplementedError("Dataset persistence for PandasExecutionEngine not implemented yet.")

    def apply_transformations(self, handle: DatasetHandle, transformations: Iterable[Any]) -> DatasetHandle:
        """
        Apply cleansing transformations to the DataFrame.

        TODO: map logical transformations from contracts/cleansing rules to
        pandas operations, or delegate to dq_cleansing transformers directly.
        See docs/diagrams/cleansing_job_flow.mmd.
        """

        raise NotImplementedError("Transformation mapping for PandasExecutionEngine not implemented yet.")

    def compute_profile(self, handle: DatasetHandle, spec: Mapping[str, Any]) -> Mapping[str, Any]:
        """
        Compute profiling statistics using pandas-friendly logic.

        TODO: delegate to dq_profiling profiling engine over the underlying
        DataFrame. See docs/ARCHITECTURE.md#2.3 Profiling module structure.
        """

        raise NotImplementedError("Profiling for PandasExecutionEngine not implemented yet.")

    def evaluate_rules(self, handle: DatasetHandle, rules_bundle: Mapping[str, Any]) -> Mapping[str, Any]:
        """
        Evaluate validation rules using pandas-backed execution.

        TODO: integrate with dq_core rule engine once it supports DataFrame
        inputs via the execution engine abstraction. See docs/reference/DQ_RULES.md.
        """

        raise NotImplementedError("Rule evaluation for PandasExecutionEngine not implemented yet.")
