"""Execution engine base interfaces.

Execution engines decouple *what* cleansing/profiling/validation need from
*how/where* datasets are processed (Pandas now; Spark/SQL later). Backend
choice must ultimately come from contracts/infra profiles; this module does
not introduce new configuration.
"""

from __future__ import annotations

from abc import ABC, abstractmethod
from typing import Any, Iterable, Mapping, Protocol


class DatasetHandle(Protocol):
    """Opaque reference to a dataset inside an execution backend."""

    ...


class ExecutionEngine(ABC):
    """Abstract execution engine for cleansing, profiling, and validation."""

    @abstractmethod
    def load_dataset(self, source_ref: Mapping[str, Any]) -> DatasetHandle:
        """Load a dataset from a source reference (blob URI, table name, etc.)."""

    @abstractmethod
    def persist_dataset(self, handle: DatasetHandle, target_ref: Mapping[str, Any]) -> Mapping[str, Any]:
        """Persist a dataset and return a lineage-friendly reference."""

    @abstractmethod
    def apply_transformations(self, handle: DatasetHandle, transformations: Iterable[Any]) -> DatasetHandle:
        """Apply logical cleansing transformations (dedup, normalize, enrich)."""

    @abstractmethod
    def compute_profile(self, handle: DatasetHandle, spec: Mapping[str, Any]) -> Mapping[str, Any]:
        """Compute profiling stats per column according to a provided spec."""

    @abstractmethod
    def evaluate_rules(self, handle: DatasetHandle, rules_bundle: Mapping[str, Any]) -> Mapping[str, Any]:
        """Evaluate validation rules and return structured results."""
