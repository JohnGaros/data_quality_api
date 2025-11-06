from __future__ import annotations

from typing import Any, Dict, List, Tuple

from ..models.cleansing_job import (
    CleansingJob,
    CleansingJobResult,
    CleansingJobStatus,
)
from ..models.cleansing_rule import CleansingRule
from .transformer import TransformationOutcome, apply_transformation
from .validators import validate_rule

Dataset = List[Dict[str, Any]]


class CleansingEngine:
    """Executes cleansing transformations in order and captures metrics."""

    def __init__(self) -> None:
        self._validator = validate_rule

    def run(
        self,
        job: CleansingJob,
        rule: CleansingRule,
        dataset: Dataset,
    ) -> Tuple[CleansingJobResult, Dataset, List[str]]:
        """Execute a cleansing job, returning the result, cleansed dataset, and warnings."""
        warnings = self._validator(rule)
        current_dataset = list(dataset)
        aggregated_metrics: Dict[str, Any] = {}
        aggregated_rejected: List[Dict[str, Any]] = []

        for step in rule.transformations:
            outcome: TransformationOutcome = apply_transformation(current_dataset, step)
            current_dataset = outcome.dataset
            aggregated_metrics[step.type] = outcome.metrics
            aggregated_rejected.extend(outcome.rejected)

        before_counts = {"rows": len(dataset)}
        after_counts = {
            "rows": len(current_dataset),
            "rejected": len(aggregated_rejected),
        }

        result = CleansingJobResult(
            job_id=job.job_id,
            status=CleansingJobStatus.SUCCEEDED,
            before_counts=before_counts,
            after_counts=after_counts,
            rejected_sample=aggregated_rejected[0] if aggregated_rejected else {},
            metrics=aggregated_metrics,
        )
        return result, current_dataset, warnings
