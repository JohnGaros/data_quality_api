"""Context facade for running contract-driven data quality jobs.

This module intentionally stays thin: it reads configuration from the existing
contract/library/catalog sources and orchestrates engines. It must not become
another configuration store.
"""

from __future__ import annotations

import uuid
from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional, Sequence

try:  # Engines are optional to keep imports lazy-friendly
    from dq_cleansing.engine.cleansing_engine import CleansingEngine
except Exception:  # pragma: no cover - missing dependency in early iterations
    CleansingEngine = None  # type: ignore

try:
    from dq_profiling.engine.profiler import ProfilingEngine
except Exception:  # pragma: no cover - missing dependency in early iterations
    ProfilingEngine = None  # type: ignore

try:
    from dq_core.engine.rule_engine import RuleEngine
except Exception:  # pragma: no cover - missing dependency in early iterations
    RuleEngine = None  # type: ignore

try:
    from dq_contracts.registry import ContractRegistry
except Exception:  # pragma: no cover - missing dependency in early iterations
    ContractRegistry = None  # type: ignore

try:
    from dq_metadata.registry import MetadataRegistry
except Exception:  # pragma: no cover - missing dependency in early iterations
    MetadataRegistry = None  # type: ignore

try:
    from dq_stores.base import ContractStore, JobDefinitionStore
except Exception:  # pragma: no cover - store module optional during early iterations
    ContractStore = None  # type: ignore
    JobDefinitionStore = None  # type: ignore
try:
    from dq_engine.base import ExecutionEngine
    from dq_engine.pandas_engine import PandasExecutionEngine
except Exception:  # pragma: no cover - execution engine optional
    ExecutionEngine = None  # type: ignore
    PandasExecutionEngine = None  # type: ignore


class DQJobStatus(str):
    """Lightweight job lifecycle states."""

    PENDING = "pending"
    RUNNING = "running"
    SUCCEEDED = "succeeded"
    FAILED = "failed"


@dataclass
class DQJobResult:
    """Minimal job result structure returned by DQContext."""

    job_id: str
    tenant: str
    environment: str
    dataset_type: str
    status: str
    contract_id: Optional[str] = None
    job_definition_id: Optional[str] = None
    details: Dict[str, Any] = field(default_factory=dict)


@dataclass
class DataContractSummary:
    """Summary of a data contract for discovery APIs."""

    contract_id: str
    dataset_types: Sequence[str]
    version: Optional[str] = None
    environment: Optional[str] = None


@dataclass
class JobDefinitionSummary:
    """Summary of a job definition for discovery APIs."""

    job_definition_id: str
    tags: Sequence[str] = field(default_factory=list)
    description: Optional[str] = None


class DQContext:
    """Runtime facade for contract-driven cleansing → profiling → validation flows.

    Configuration is always sourced from `dq_contracts`, `dq_jobs`, and the
    authoring libraries described in the architecture docs. This class is a
    convenience layer for notebooks, scripts, Airflow/ADF operators, and tests.
    It must not store or mutate rule/schema/governance configuration.
    """

    def __init__(
        self,
        tenant: str,
        env: str,
        *,
        contract_registry: Optional[ContractRegistry] = None,
        contract_store: Optional["ContractStore"] = None,
        metadata_registry: Optional[MetadataRegistry] = None,
        cleansing_engine: Optional[CleansingEngine] = None,
        profiling_engine: Optional[ProfilingEngine] = None,
        rule_engine: Optional[RuleEngine] = None,
        job_definition_store: Optional["JobDefinitionStore"] = None,
        execution_engine: Optional["ExecutionEngine"] = None,
    ) -> None:
        self.tenant = tenant
        self.environment = env
        self.contract_registry = contract_registry
        self.contract_store = contract_store
        self.job_definition_store = job_definition_store
        self.metadata_registry = metadata_registry
        self.execution_engine = execution_engine or (PandasExecutionEngine() if PandasExecutionEngine else None)
        self.cleansing_engine = cleansing_engine or (CleansingEngine() if CleansingEngine else None)
        self.profiling_engine = profiling_engine or (ProfilingEngine() if ProfilingEngine else None)
        self.rule_engine = rule_engine or (RuleEngine() if RuleEngine else None)

    def run_validation_on_file(
        self,
        dataset_type: str,
        local_path: str,
        job_definition_id: Optional[str] = None,
        extra_metadata: Optional[Dict[str, Any]] = None,
    ) -> DQJobResult:
        """Run cleansing → profiling → validation on a local file.

        Configuration is derived from `DataContracts` (and optionally a
        JobDefinition) scoped by the provided tenant/environment. Upload and
        storage selection must come from infra profiles defined in contracts
        and infra libraries; this facade will not accept ad-hoc overrides.
        """

        job_id = self._build_job_id(prefix="file")
        contract = self._resolve_contract_for_dataset(dataset_type)
        upload_ref = self._upload_local_file(dataset_type, local_path, contract)
        cleansing_output = self._run_cleansing_pipeline(job_id, dataset_type, upload_ref, contract)
        profiling_output = self._run_profiling_pipeline(job_id, dataset_type, cleansing_output, contract)
        validation_output = self._run_validation_engine(
            job_id,
            dataset_type,
            contract=contract,
            profiling_output=profiling_output,
            job_definition_id=job_definition_id,
        )
        self._record_metadata_event(
            job_id=job_id,
            dataset_type=dataset_type,
            contract=contract,
            upload_ref=upload_ref,
            cleansing_output=cleansing_output,
            profiling_output=profiling_output,
            validation_output=validation_output,
            extra_metadata=extra_metadata,
            job_definition_id=job_definition_id,
        )

        details = {
            "upload": upload_ref,
            "cleansing": cleansing_output,
            "profiling": profiling_output,
            "validation": validation_output,
            "extra_metadata": extra_metadata or {},
        }
        contract_id = getattr(contract, "contract_id", None) or getattr(contract, "contractId", None)
        if not contract_id and isinstance(contract, dict):
            contract_id = contract.get("contract_id") or contract.get("contractId")
        return DQJobResult(
            job_id=job_id,
            tenant=self.tenant,
            environment=self.environment,
            dataset_type=dataset_type,
            status=DQJobStatus.SUCCEEDED,
            contract_id=contract_id,
            job_definition_id=job_definition_id,
            details=details,
        )

    def run_job_definition(
        self,
        job_definition_id: str,
        batch_ref: Dict[str, Any],
        extra_metadata: Optional[Dict[str, Any]] = None,
    ) -> DQJobResult:
        """Execute a JobDefinition/Checkpoint by ID.

        JobDefinitions are expected to live under `dq_jobs` and reference
        contracts and action profiles. This call resolves the job definition,
        validates its tenant/environment, and orchestrates the same cleansing →
        profiling → validation sequence as file-based runs.
        """

        job_id = self._build_job_id(prefix="jobdef")
        job_definition = self._resolve_job_definition(job_definition_id)
        dataset_type = self._extract_dataset_type_from_job(job_definition)
        contract = self._resolve_contract_from_job(job_definition)
        cleansing_output = self._run_cleansing_pipeline(job_id, dataset_type, batch_ref, contract)
        profiling_output = self._run_profiling_pipeline(job_id, dataset_type, cleansing_output, contract)
        validation_output = self._run_validation_engine(
            job_id,
            dataset_type,
            contract=contract,
            profiling_output=profiling_output,
            job_definition_id=job_definition_id,
            batch_ref=batch_ref,
        )
        self._record_metadata_event(
            job_id=job_id,
            dataset_type=dataset_type,
            contract=contract,
            upload_ref=batch_ref,
            cleansing_output=cleansing_output,
            profiling_output=profiling_output,
            validation_output=validation_output,
            extra_metadata=extra_metadata,
            job_definition_id=job_definition_id,
        )

        details = {
            "batch_ref": batch_ref,
            "cleansing": cleansing_output,
            "profiling": profiling_output,
            "validation": validation_output,
            "extra_metadata": extra_metadata or {},
        }
        contract_id = getattr(contract, "contract_id", None) or getattr(contract, "contractId", None)
        if not contract_id and isinstance(contract, dict):
            contract_id = contract.get("contract_id") or contract.get("contractId")
        return DQJobResult(
            job_id=job_id,
            tenant=self.tenant,
            environment=self.environment,
            dataset_type=dataset_type,
            status=DQJobStatus.SUCCEEDED,
            contract_id=contract_id,
            job_definition_id=job_definition_id,
            details=details,
        )

    def list_contracts(self, dataset_type: Optional[str] = None) -> List[DataContractSummary]:
        """List contracts available to this tenant/environment."""

        return self._list_contracts(dataset_type=dataset_type)

    def list_job_definitions(self, tags: Optional[List[str]] = None) -> List[JobDefinitionSummary]:
        """List job definitions available to this tenant/environment."""

        return self._list_job_definitions(tags=tags)

    def dry_run_job(
        self,
        job_definition_id: str,
        batch_ref: Dict[str, Any],
        overrides: Optional[Dict[str, Any]] = None,
    ) -> DQJobResult:
        """Optional dry-run execution path (stubbed until supported)."""

        raise NotImplementedError(
            "Dry-run support is not implemented. See docs/ACTIONS_AND_JOB_DEFINITIONS.md for planned semantics."
        )

    # --- Internal helpers (clear TODOs for missing dependencies) ---

    def _resolve_contract_for_dataset(self, dataset_type: str) -> Any:
        """
        Resolve the active DataContract for a dataset type.

        TODO: Wire this to `dq_contracts.ContractRegistry` when repository/search
        helpers are available. See docs/CONTRACT_DRIVEN_ARCHITECTURE.md.
        """

        if self.contract_store:
            # Prefer store abstraction once concrete implementation exists.
            return self.contract_store.get_latest_for_dataset(
                tenant=self.tenant,
                environment=self.environment,
                dataset_type=dataset_type,
            )
        raise NotImplementedError("Contract resolution not implemented yet (docs/CONTRACT_DRIVEN_ARCHITECTURE.md).")

    def _upload_local_file(self, dataset_type: str, local_path: str, contract: Any) -> Dict[str, Any]:
        """
        Upload a local file to the correct blob container based on infra profiles.

        TODO: Integrate with dq_integration.azure_blob adapters once the infra
        profile resolution exists in contracts/infra libraries.
        """

        raise NotImplementedError("Blob upload adapter not implemented (docs/ARCHITECTURE.md#Integrations).")

    def _run_cleansing_pipeline(
        self,
        job_id: str,
        dataset_type: str,
        input_ref: Any,
        contract: Any,
    ) -> Any:
        """
        Execute the cleansing engine based on contract-scoped rules.

        TODO: Link contract-derived cleansing rule bindings to dq_cleansing once
        the registry wiring is available. See docs/diagrams/cleansing_job_flow.mmd.
        """

        raise NotImplementedError("Cleansing pipeline wiring not implemented (docs/ARCHITECTURE.md#2.2).")

    def _run_profiling_pipeline(
        self,
        job_id: str,
        dataset_type: str,
        cleansing_output: Any,
        contract: Any,
    ) -> Any:
        """
        Execute profiling using cleansed data.

        TODO: Feed the profiling engine with contract metadata once available.
        See docs/diagrams/profiling_context.mmd.
        """

        raise NotImplementedError("Profiling pipeline wiring not implemented (docs/ARCHITECTURE.md#2.3).")

    def _run_validation_engine(
        self,
        job_id: str,
        dataset_type: str,
        *,
        contract: Any,
        profiling_output: Any,
        job_definition_id: Optional[str],
        batch_ref: Optional[Dict[str, Any]] = None,
    ) -> Any:
        """
        Execute validation rules using dq_core rule engine and profiling context.

        TODO: Pull rule bindings from the contract registry and drive dq_core
        once rule evaluation is implemented. See docs/reference/DQ_RULES.md.
        """

        raise NotImplementedError("Validation engine wiring not implemented (docs/reference/DQ_RULES.md).")

    def _record_metadata_event(
        self,
        *,
        job_id: str,
        dataset_type: str,
        contract: Any,
        upload_ref: Any,
        cleansing_output: Any,
        profiling_output: Any,
        validation_output: Any,
        extra_metadata: Optional[Dict[str, Any]],
        job_definition_id: Optional[str],
    ) -> None:
        """
        Record lineage and audit metadata for the run.

        TODO: Integrate with dq_metadata once the repository is available for
        job run persistence. See docs/reference/METADATA_PILLARS.md.
        """

        raise NotImplementedError("Metadata recording not implemented (docs/reference/METADATA_PILLARS.md).")

    def _resolve_job_definition(self, job_definition_id: str) -> Any:
        """
        Fetch a JobDefinition by ID from dq_jobs.

        TODO: Implement JobDefinition registry lookup when dq_jobs is available.
        See docs/ACTIONS_AND_JOB_DEFINITIONS.md.
        """

        if self.job_definition_store:
            return self.job_definition_store.get(job_definition_id)
        raise NotImplementedError("JobDefinition registry not implemented (docs/ACTIONS_AND_JOB_DEFINITIONS.md).")

    def _list_contracts(self, dataset_type: Optional[str] = None) -> List[DataContractSummary]:
        """
        List contracts for the current tenant/environment.

        TODO: Implement using dq_contracts search helpers. See
        docs/CONTRACT_DRIVEN_ARCHITECTURE.md.
        """

        if self.contract_store:
            items = self.contract_store.list(tenant=self.tenant, environment=self.environment, dataset_type=dataset_type)
            summaries = []
            for item in items:
                dataset_types = getattr(item, "dataset_types", None) or getattr(item, "datasets", []) or []
                if isinstance(dataset_types, list) and dataset_types and not isinstance(dataset_types[0], str):
                    dataset_types = [getattr(ds, "dataset_type", None) for ds in dataset_types]
                summaries.append(
                    DataContractSummary(
                        contract_id=getattr(item, "contract_id", None) or getattr(item, "contractId", ""),
                        dataset_types=[dt for dt in dataset_types if dt],
                        version=getattr(item, "version", None),
                        environment=getattr(item, "environment", None),
                    )
                )
            return summaries
        raise NotImplementedError("Contract listing not implemented (docs/CONTRACT_DRIVEN_ARCHITECTURE.md).")

    def _list_job_definitions(self, tags: Optional[List[str]] = None) -> List[JobDefinitionSummary]:
        """
        List job definitions filtered by tags for the current tenant/environment.

        TODO: Implement using dq_jobs registry once models/search are in place.
        See docs/ACTIONS_AND_JOB_DEFINITIONS.md.
        """

        if self.job_definition_store:
            items = self.job_definition_store.list_by_tags(
                tenant=self.tenant,
                environment=self.environment,
                tags=tags,
            )
            return [
                JobDefinitionSummary(
                    job_definition_id=getattr(item, "job_definition_id", None) or getattr(item, "jobDefinitionId", ""),
                    tags=getattr(item, "tags", []) or [],
                    description=getattr(item, "description", None),
                )
                for item in items
            ]
        raise NotImplementedError("JobDefinition listing not implemented (docs/ACTIONS_AND_JOB_DEFINITIONS.md).")

    def _resolve_contract_from_job(self, job_definition: Any) -> Any:
        """
        Resolve contract reference embedded in a job definition.

        TODO: Extract contract refs once dq_jobs models are defined. See
        docs/ACTIONS_AND_JOB_DEFINITIONS.md.
        """

        raise NotImplementedError("JobDefinition contract resolution not implemented (docs/ACTIONS_AND_JOB_DEFINITIONS.md).")

    def _extract_dataset_type_from_job(self, job_definition: Any) -> str:
        """
        Extract dataset type from a job definition payload.

        TODO: Update once dq_jobs defines the model schema.
        """

        raise NotImplementedError("Dataset type extraction not implemented (docs/ACTIONS_AND_JOB_DEFINITIONS.md).")

    def _build_job_id(self, prefix: str) -> str:
        """Create a deterministic job identifier."""

        return f"{prefix}-{self.tenant}-{self.environment}-{uuid.uuid4().hex}"
