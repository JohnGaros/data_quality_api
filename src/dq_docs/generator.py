"""Data Docs generator orchestrating registry/metadata lookups.

This module consumes existing registries (contracts, jobs, metadata) and
produces view models for rendering. It does not introduce configuration; it
reflects canonical JSON and recorded metadata scoped by tenant/environment.
"""

from __future__ import annotations

from typing import Any, Optional

from dq_docs.models import (
    ActionProfileDoc,
    ContractDiffDoc,
    ContractDoc,
    DatasetDoc,
    JobDefinitionDoc,
    RunDoc,
)


class DataDocsGenerator:
    """Builds Data Docs view models from registries/stores."""

    def __init__(
        self,
        *,
        contract_registry: Optional[Any] = None,
        job_registry: Optional[Any] = None,
        metadata_registry: Optional[Any] = None,
        action_registry: Optional[Any] = None,
        tenant: Optional[str] = None,
        environment: Optional[str] = None,
    ) -> None:
        self.contract_registry = contract_registry
        self.job_registry = job_registry
        self.metadata_registry = metadata_registry
        self.action_registry = action_registry
        self.tenant = tenant
        self.environment = environment

    def build_contract_doc(self, contract_id: str, version: Optional[str] = None) -> ContractDoc:
        """Load contract and return a ContractDoc.

        TODO: integrate with `dq_contracts.ContractRegistry`. See
        docs/ARCHITECTURE.md and docs/DATA_DOCS_STRATEGY.md.
        """

        contract = self._load_contract(contract_id, version=version)
        return self._map_contract_to_doc(contract)

    def build_job_definition_doc(self, job_definition_id: str) -> JobDefinitionDoc:
        """Load a JobDefinition/Checkpoint and return a JobDefinitionDoc."""

        job_def = self._load_job_definition(job_definition_id)
        return self._map_job_definition_to_doc(job_def)

    def build_run_doc(self, run_id: str) -> RunDoc:
        """Build a RunDoc from metadata and related entities."""

        run = self._load_run(run_id)
        return self._map_run_to_doc(run)

    def build_contract_diff_doc(self, contract_id: str, from_version: str, to_version: str) -> ContractDiffDoc:
        """Stub for generating contract diffs."""

        raise NotImplementedError("Contract diff docs not implemented (docs/DATA_DOCS_STRATEGY.md).")

    # --- Internal loaders (stubbed for now) ---------------------------------

    def _load_contract(self, contract_id: str, version: Optional[str] = None) -> Any:
        raise NotImplementedError("Contract loading not implemented (docs/CONTRACT_DRIVEN_ARCHITECTURE.md).")

    def _load_job_definition(self, job_definition_id: str) -> Any:
        raise NotImplementedError("JobDefinition loading not implemented (docs/ACTIONS_AND_JOB_DEFINITIONS.md).")

    def _load_run(self, run_id: str) -> Any:
        raise NotImplementedError("Run loading not implemented (docs/reference/METADATA_PILLARS.md).")

    # --- Mapping helpers (minimal placeholders) -----------------------------

    def _map_contract_to_doc(self, contract: Any) -> ContractDoc:
        """Map contract model to ContractDoc."""

        # Basic placeholders; will be replaced once contract model mapping is wired.
        datasets: list[DatasetDoc] = []
        return ContractDoc(
            contract_id=getattr(contract, "contract_id", contract),
            name=getattr(contract, "name", None),
            version=getattr(contract, "version", None),
            tenant=getattr(contract, "tenant_id", self.tenant or ""),
            environment=str(getattr(contract, "environment", self.environment or "")),
            status=str(getattr(getattr(contract, "lifecycle", None), "status", "")) if hasattr(contract, "lifecycle") else None,
            datasets=datasets,
            rule_templates=[],
            governance={},
            metadata=getattr(contract, "metadata", {}) if hasattr(contract, "metadata") else {},
        )

    def _map_job_definition_to_doc(self, job_def: Any) -> JobDefinitionDoc:
        """Map job definition model to JobDefinitionDoc."""

        actions = []
        action_refs = getattr(job_def, "action_profiles", []) if hasattr(job_def, "action_profiles") else []
        for ref in action_refs:
            actions.append(
                ActionProfileDoc(
                    action_profile_id=getattr(ref, "action_profile_id", str(ref)),
                    name=getattr(ref, "name", None),
                    action_type=getattr(ref, "action_type", None),
                    status=None,
                    metadata={},
                )
            )

        return JobDefinitionDoc(
            job_definition_id=getattr(job_def, "job_definition_id", job_def),
            name=getattr(job_def, "name", None),
            tenant=getattr(job_def, "tenant_id", self.tenant or ""),
            environment=str(getattr(job_def, "environment", self.environment or "")),
            description=getattr(job_def, "description", None),
            dataset_type=getattr(job_def, "dataset_type", None),
            contract_id=getattr(job_def, "contract_id", None),
            contract_version=getattr(job_def, "contract_version", None),
            trigger=getattr(job_def, "trigger", None),
            tags=getattr(job_def, "tags", []) or [],
            action_profiles=actions,
            metadata=getattr(job_def, "metadata", {}) if hasattr(job_def, "metadata") else {},
        )

    def _map_run_to_doc(self, run: Any) -> RunDoc:
        """Map run metadata to RunDoc."""

        return RunDoc(
            run_id=getattr(run, "job_id", run),
            job_definition_id=getattr(run, "job_definition_id", None),
            contract_id=getattr(run, "contract_id", None),
            contract_version=getattr(run, "contract_version", None),
            tenant=getattr(run, "tenant_id", self.tenant or ""),
            environment=str(getattr(run, "environment", self.environment or "")),
            started_at=getattr(run, "submitted_at", None),
            completed_at=getattr(run, "completed_at", None),
            ingestion={"ingestion_mode": getattr(run, "ingestion_mode", None), "raw_blob_uri": getattr(run, "raw_blob_uri", None)},
            cleansing=None,
            profiling=None,
            validation=None,
            actions=[],
            metadata=getattr(run, "metadata", {}) if hasattr(run, "metadata") else {},
        )
