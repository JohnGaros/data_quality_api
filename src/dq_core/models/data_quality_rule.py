"""Canonical representations of rule templates across validation, profiling, and cleansing."""
from __future__ import annotations

from datetime import date
from typing import Any, List, Optional

from pydantic import BaseModel, Field, field_validator


class RuleBase(BaseModel):
    """Shared fields used by all rule templates."""

    rule_id: str = Field(..., description="Logical identifier for the rule.")
    name: str = Field(..., description="Human-friendly rule name.")
    dataset_type: str = Field(..., description="Dataset category the rule applies to (billing, payments, etc.).")
    description: Optional[str] = Field(None, description="Explains the business intent of the rule.")
    active_from: Optional[date] = Field(None, description="Optional activation date.")
    active_to: Optional[date] = Field(None, description="Optional retirement date.")
    tags: List[str] = Field(default_factory=list, description="Searchable labels.")

    @field_validator("rule_id", "name", "dataset_type", mode="before")
    def _require_non_empty(cls, value: Any) -> str:
        """Guard against missing identifiers."""
        if value is None:
            raise ValueError("value cannot be null")
        if isinstance(value, str):
            cleaned = value.strip()
            if not cleaned:
                raise ValueError("value cannot be empty")
            return cleaned
        return str(value)

    @field_validator("tags", mode="before")
    def _normalise_tags(cls, value: Any) -> List[str]:
        """Normalise tag values to a clean list of strings."""
        if value is None:
            return []
        if isinstance(value, str):
            return [value.strip()] if value.strip() else []
        return [str(tag).strip() for tag in value if str(tag).strip()]

    @field_validator("description", mode="before")
    def _strip_description(cls, value: Any) -> Optional[str]:
        """Trim whitespace from description fields."""
        if value is None:
            return None
        cleaned = str(value).strip()
        return cleaned or None


class ValidationRuleTemplate(RuleBase):
    """Validation rules expressed as boolean expressions."""

    expression: str = Field(..., description="Boolean expression evaluated by the validation engine.")
    severity: str = Field(
        ...,
        description="Determines whether failures block (hard) or warn (soft).",
    )

    @field_validator("expression")
    def _require_expression(cls, value: str) -> str:
        """Ensure expressions are populated."""
        if not value or not value.strip():
            raise ValueError("expression cannot be empty")
        return value.strip()

    @field_validator("severity")
    def _validate_severity(cls, value: str) -> str:
        """Normalise severity into accepted values."""
        normalised = value.strip().lower()
        if normalised not in {"hard", "soft"}:
            raise ValueError("severity must be either 'hard' or 'soft'")
        return normalised


class ProfilingRuleTemplate(RuleBase):
    """Profiling expectations derived from profiling metrics."""

    field: Optional[str] = Field(None, description="Optional field/column the metric applies to.")
    profile_metric: str = Field(..., description="Metric code (null_ratio, stddev, max, distinct_count, etc.).")
    comparison: str = Field(
        "<=",
        description="Comparator used to evaluate the threshold (<=, <, >=, >, ==).",
    )
    threshold: float = Field(..., description="Expected threshold for the metric.")
    tolerance: Optional[float] = Field(
        None,
        description="Optional tolerance band applied to the threshold.",
    )

    @field_validator("profile_metric")
    def _require_metric(cls, value: str) -> str:
        """Ensure metrics are provided."""
        if not value or not value.strip():
            raise ValueError("profile_metric cannot be empty")
        return value.strip()

    @field_validator("comparison")
    def _validate_comparison(cls, value: str) -> str:
        """Ensure comparison operators are supported."""
        allowed = {"<", "<=", ">", ">=", "=="}
        normalised = value.strip()
        if normalised not in allowed:
            raise ValueError(f"comparison must be one of {sorted(allowed)}")
        return normalised

    @field_validator("threshold")
    def _require_threshold(cls, value: float) -> float:
        """Guard against missing thresholds."""
        if value is None:
            raise ValueError("threshold must be provided")
        return float(value)
