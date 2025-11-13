"""In-memory orchestration layer for cleansing jobs."""

from __future__ import annotations

from typing import Any, Dict, Iterable, List, Optional, Tuple

from dq_cleansing import (
    CleansingEngine,
    CleansingJob,
    CleansingJobResult,
    CleansingJobStatus,
    CleansingRule,
    CleansingRuleLibrary,
)


class CleansingJobManager:
    """Coordinates cleansing job execution and in-memory persistence."""

    def __init__(
        self,
        rule_library: Optional[CleansingRuleLibrary] = None,
        engine: Optional[CleansingEngine] = None,
    ) -> None:
        self.rule_library = rule_library or CleansingRuleLibrary()
        self.engine = engine or CleansingEngine()
        self._jobs: Dict[str, CleansingJob] = {}
        self._results: Dict[str, CleansingJobResult] = {}
        self._outputs: Dict[str, List[Dict[str, Any]]] = {}

    # Rule operations -----------------------------------------------------------------

    def upsert_rule(self, rule: CleansingRule) -> None:
        """Insert or update a cleansing rule in the backing library."""

        self.rule_library.upsert(rule)

    def list_rules(self, dataset_type: Optional[str] = None) -> Iterable[CleansingRule]:
        """Return all rules, optionally filtered by dataset type."""

        return self.rule_library.list(dataset_type=dataset_type)

    def reset(self) -> None:
        """Clear in-memory state. Intended for tests and local development."""
        self.rule_library.clear()
        self._jobs.clear()
        self._results.clear()
        self._outputs.clear()

    # Job execution -------------------------------------------------------------------

    def submit_job(
        self,
        job: CleansingJob,
        dataset: List[Dict[str, Any]],
    ) -> Tuple[CleansingJobResult, List[Dict[str, Any]], List[str]]:
        """Run a cleansing job immediately (synchronous stub for the blueprint)."""
        rule = self.rule_library.get(job.rule_id, job.rule_version)
        if not rule:
            raise ValueError(f"cleansing rule {job.rule_id} not found")

        running_job = job.copy(update={"status": CleansingJobStatus.RUNNING})
        result, cleansed_dataset, warnings = self.engine.run(running_job, rule, dataset)
        if warnings:
            result.metrics["warnings"] = warnings

        completed_job = running_job.copy(update={"status": result.status})
        self._jobs[job.job_id] = completed_job
        self._results[job.job_id] = result
        self._outputs[job.job_id] = cleansed_dataset

        return result, cleansed_dataset, warnings

    # Retrieval -----------------------------------------------------------------------

    def get_job(self, job_id: str) -> Optional[CleansingJob]:
        """Return a previously submitted job, if available."""

        return self._jobs.get(job_id)

    def get_result(self, job_id: str) -> Optional[CleansingJobResult]:
        """Return the result for a completed job."""

        return self._results.get(job_id)

    def list_job_results(self) -> Iterable[CleansingJobResult]:
        """Iterate over all stored results."""

        return self._results.values()

    def get_output_dataset(self, job_id: str) -> Optional[List[Dict[str, Any]]]:
        """Return the cleansed dataset for a job."""

        return self._outputs.get(job_id)

    def link_validation_job(self, job_id: str, validation_job_id: str) -> Optional[CleansingJobResult]:
        """Persist the validation job id that consumed the cleansing output."""

        result = self._results.get(job_id)
        if not result:
            return None
        updated = result.copy(update={"linked_validation_job_id": validation_job_id})
        self._results[job_id] = updated
        return updated
