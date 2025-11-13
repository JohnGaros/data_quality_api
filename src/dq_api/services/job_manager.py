"""Validation job orchestration utilities."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Dict, List, Optional

from dq_cleansing import CleansingJob

from .cleansing_job_manager import CleansingJobManager


@dataclass
class ValidationJobRequest:
    """Envelope describing the work needed to run a validation job."""

    job_id: str
    tenant_id: str
    dataset_type: str
    dataset: List[Dict[str, Any]]
    chain_cleansing: bool = False
    cleansing_rule_id: Optional[str] = None
    cleansing_rule_version: Optional[str] = None


class JobManager:
    """Lightweight job manager that can chain cleansing before validation."""

    def __init__(self, cleansing_manager: Optional[CleansingJobManager] = None) -> None:
        """Initialize the manager with an optional cleansing manager dependency."""

        self.cleansing_manager = cleansing_manager

    def execute(self, request: ValidationJobRequest) -> Dict[str, Any]:
        """Run a validation job, optionally chaining a cleansing job beforehand."""

        dataset = list(request.dataset)
        cleansing_summary: Optional[Dict[str, Any]] = None

        if request.chain_cleansing:
            if not self.cleansing_manager:
                raise ValueError("Cleansing manager is required when chain_cleansing is True")
            cleansing_job_id = f"cln-{request.job_id}"
            cleansing_job = CleansingJob(
                job_id=cleansing_job_id,
                tenant_id=request.tenant_id,
                dataset_type=request.dataset_type,
                rule_id=request.cleansing_rule_id or "default",
                rule_version=request.cleansing_rule_version,
                chain_validation=True,
            )
            result, cleansed_dataset, _warnings = self.cleansing_manager.submit_job(
                cleansing_job,
                dataset,
            )
            self.cleansing_manager.link_validation_job(cleansing_job_id, request.job_id)
            cleansing_summary = result.to_report_dict()
            dataset = cleansed_dataset

        validation_summary = self._run_validation(dataset)
        return {
            "validation": validation_summary,
            "cleansing": cleansing_summary,
        }

    @staticmethod
    def _run_validation(dataset: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Placeholder validation execution that reports simple metrics."""

        record_count = len(dataset)
        return {
            "status": "succeeded",
            "records_processed": record_count,
        }
