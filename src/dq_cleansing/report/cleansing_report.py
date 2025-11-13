from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Dict

from ..models.cleansing_job import CleansingJobResult


@dataclass
class CleansingReport:
    """Human-readable summary of a cleansing job."""

    job_id: str
    status: str
    before_rows: int
    after_rows: int
    rejected_rows: int
    metrics: Dict[str, Any]

    @classmethod
    def from_result(cls, result: CleansingJobResult) -> "CleansingReport":
        """Build a report from a `CleansingJobResult` instance."""

        return cls(
            job_id=result.job_id,
            status=result.status.value,
            before_rows=result.before_counts.get("rows", 0),
            after_rows=result.after_counts.get("rows", 0),
            rejected_rows=result.after_counts.get("rejected", 0),
            metrics=result.metrics,
        )

    def to_dict(self) -> Dict[str, Any]:
        """Return a serialisable representation for API responses."""

        return {
            "job_id": self.job_id,
            "status": self.status,
            "before_rows": self.before_rows,
            "after_rows": self.after_rows,
            "rejected_rows": self.rejected_rows,
            "metrics": self.metrics,
        }
