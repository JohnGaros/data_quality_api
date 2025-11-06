from __future__ import annotations

from typing import Any, Dict, List, Optional

from pydantic import BaseModel, Field, validator


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

    @validator("type")
    def _normalise_type(cls, value: str) -> str:
        value = value.strip().lower()
        if not value:
            raise ValueError("transformation type cannot be empty")
        return value

    @validator("severity")
    def _validate_severity(cls, value: str) -> str:
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
    transformations: List[TransformationStep]
    metadata: Dict[str, Any] = Field(default_factory=dict)

    @validator("rule_id", "name", "dataset_type", "version")
    def _require_non_empty(cls, value: str) -> str:
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
