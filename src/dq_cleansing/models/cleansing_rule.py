from __future__ import annotations

from datetime import date
from typing import Any, Dict, List, Optional

from pydantic import BaseModel, Field, field_validator


class TransformationStep(BaseModel):
    """Describes a single cleansing transformation."""

    type: str = Field(..., description="Transformation keyword, e.g. standardize or deduplicate.")
    target_fields: List[str] = Field(
        default_factory=list,
        description="Logical fields impacted by the transformation.",
    )
    parameters: Dict[str, Any] = Field(
        default_factory=dict,
        description="Arbitrary configuration for the transformation.",
    )
    severity: str = Field(
        default="soft",
        description="Determines whether failures reject records (hard) or log warnings (soft).",
    )
    condition: Optional[str] = Field(
        default=None,
        description="Optional expression controlling when to execute the transformation.",
    )

    @field_validator("type", mode="before")
    def _normalise_type(cls, value: str) -> str:
        """Normalise and validate the transformation type."""
        value = value.strip().lower()
        if not value:
            raise ValueError("transformation type cannot be empty")
        return value

    @field_validator("severity", mode="before")
    def _validate_severity(cls, value: str) -> str:
        """Ensure severity values conform to soft/hard semantics."""
        normalised = value.strip().lower()
        if normalised not in {"soft", "hard"}:
            raise ValueError("severity must be either 'soft' or 'hard'")
        return normalised


class CleansingRule(BaseModel):
    """Canonical representation of a cleansing rule definition."""

    rule_id: str
    name: str
    dataset_type: str
    version: str
    description: Optional[str] = Field(
        default=None,
        description="Business-facing explanation of what the cleansing rule does.",
    )
    active_from: Optional[date] = Field(
        default=None,
        description="Optional activation date for the cleansing rule version.",
    )
    transformations: List[TransformationStep]
    metadata: Dict[str, Any] = Field(default_factory=dict)

    @field_validator("rule_id", "name", "dataset_type", "version", mode="before")
    def _require_non_empty(cls, value: str) -> str:
        """Guard against empty strings in critical identifiers."""
        if not value or not value.strip():
            raise ValueError("value cannot be empty")
        return value.strip()

    def describe(self) -> Dict[str, Any]:
        """Return serialisable summary for APIs and reports."""
        return {
            "rule_id": self.rule_id,
            "name": self.name,
            "dataset_type": self.dataset_type,
            "version": self.version,
            "transformation_count": len(self.transformations),
        }
