from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Callable, Dict, List, Tuple

from ..models.cleansing_rule import TransformationStep

Dataset = List[Dict[str, Any]]
Metrics = Dict[str, Any]
Rejected = List[Dict[str, Any]]


class TransformationError(RuntimeError):
    """Raised when a cleansing step cannot be executed."""


@dataclass
class TransformationOutcome:
    dataset: Dataset
    metrics: Metrics
    rejected: Rejected


def _standardize(dataset: Dataset, step: TransformationStep) -> TransformationOutcome:
    format_hint = step.parameters.get("format", "").lower()
    updated: Dataset = []
    for row in dataset:
        new_row = dict(row)
        for field in step.target_fields:
            if field not in new_row or new_row[field] is None:
                continue
            value = new_row[field]
            if isinstance(value, str):
                if format_hint in {"iso-4217", "upper"}:
                    new_row[field] = value.upper()
                elif format_hint in {"lower"}:
                    new_row[field] = value.lower()
        updated.append(new_row)
    return TransformationOutcome(updated, {"standardized_fields": step.target_fields}, [])


def _fill_missing(dataset: Dataset, step: TransformationStep) -> TransformationOutcome:
    default_value = step.parameters.get("default")
    rejected: Rejected = []
    updated: Dataset = []
    severity = step.severity

    for row in dataset:
        new_row = dict(row)
        failure = False
        for field in step.target_fields:
            value = new_row.get(field)
            if value in (None, ""):
                if default_value is not None:
                    new_row[field] = default_value
                else:
                    failure = True
        if failure and severity == "hard":
            rejected.append({"row": row, "reason": f"{step.type} failed for {step.target_fields}"})
            continue
        updated.append(new_row)

    metrics = {"filled_fields": step.target_fields, "rejected": len(rejected)}
    return TransformationOutcome(updated, metrics, rejected)


def _deduplicate(dataset: Dataset, step: TransformationStep) -> TransformationOutcome:
    keys = step.parameters.get("keys") or step.target_fields
    if not keys:
        raise TransformationError("deduplicate step requires keys or target_fields")

    seen = set()
    deduped: Dataset = []
    rejected: Rejected = []

    for row in dataset:
        key = tuple(row.get(field) for field in keys)
        if key in seen:
            rejected.append({"row": row, "reason": f"duplicate on {keys}"})
            if step.severity == "soft":
                continue
            # Hard duplicates are removed entirely.
        else:
            seen.add(key)
            deduped.append(row)

    metrics = {
        "keys": keys,
        "deduplicated": len(dataset) - len(deduped),
        "retained": len(deduped),
    }
    return TransformationOutcome(deduped, metrics, rejected)


TRANSFORMATION_HANDLERS: Dict[str, Callable[[Dataset, TransformationStep], TransformationOutcome]] = {
    "standardize": _standardize,
    "standardise": _standardize,
    "fill_missing": _fill_missing,
    "deduplicate": _deduplicate,
}


def apply_transformation(dataset: Dataset, step: TransformationStep) -> TransformationOutcome:
    """Apply a single transformation step to a dataset."""
    handler = TRANSFORMATION_HANDLERS.get(step.type)
    if not handler:
        raise TransformationError(f"unsupported transformation type: {step.type}")
    return handler(dataset, step)
