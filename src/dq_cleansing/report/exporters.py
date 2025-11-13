"""Export helpers for cleansing reports."""

from __future__ import annotations

from typing import Any, Dict

from .cleansing_report import CleansingReport


def to_json(report: CleansingReport) -> Dict[str, Any]:
    """Return a serialisable representation for API responses."""

    return report.to_dict()
