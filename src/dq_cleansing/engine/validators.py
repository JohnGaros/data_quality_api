"""Validation helpers for cleansing rules."""

from __future__ import annotations

from typing import List

from ..models.cleansing_rule import CleansingRule, TransformationStep


def validate_rule(rule: CleansingRule) -> List[str]:
    """Return list of validation warnings for a rule definition."""

    warnings: List[str] = []
    for index, step in enumerate(rule.transformations):
        _validate_step(step, index, warnings)
    return warnings


def _validate_step(step: TransformationStep, index: int, warnings: List[str]) -> None:
    """Inspect a single transformation for common issues."""

    if step.type in {"standardize", "standardise", "fill_missing"} and not step.target_fields:
        warnings.append(f"step {index} requires target_fields for {step.type}")
    if step.type == "deduplicate" and not (step.parameters.get("keys") or step.target_fields):
        warnings.append(f"step {index} must define keys for deduplicate")
