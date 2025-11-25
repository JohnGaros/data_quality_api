"""HTML renderer for Data Docs view models."""

from __future__ import annotations

from typing import List

from dq_docs.models import ContractDoc, DatasetDoc, JobDefinitionDoc, RunDoc


class HtmlRenderer:
    """Render Data Docs into HTML strings."""

    def render_contract_doc(self, doc: ContractDoc) -> str:
        """Return HTML for a contract doc."""

        parts: List[str] = [
            f"<h1>Contract: {doc.contract_id}</h1>",
            f"<p>Tenant: {doc.tenant} | Environment: {doc.environment} | Version: {doc.version or ''}</p>",
        ]
        for dataset in doc.datasets:
            parts.append(self._render_dataset(dataset))
        return "\n".join(parts)

    def render_job_definition_doc(self, doc: JobDefinitionDoc) -> str:
        """Return HTML for a job definition doc."""

        parts = [
            f"<h1>JobDefinition: {doc.job_definition_id}</h1>",
            f"<p>Tenant: {doc.tenant} | Environment: {doc.environment}</p>",
            f"<p>Dataset: {doc.dataset_type or ''} | Contract: {doc.contract_id or ''}</p>",
        ]
        if doc.tags:
            parts.append(f"<p>Tags: {', '.join(doc.tags)}</p>")
        return "\n".join(parts)

    def render_run_doc(self, doc: RunDoc) -> str:
        """Return HTML for a run doc."""

        parts = [
            f"<h1>Run: {doc.run_id}</h1>",
            f"<p>Tenant: {doc.tenant} | Environment: {doc.environment}</p>",
            f"<p>JobDefinition: {doc.job_definition_id or ''} | Contract: {doc.contract_id or ''}</p>",
            f"<p>Status: {getattr(doc.validation, 'status', '') if doc.validation else ''}</p>",
        ]
        return "\n".join(parts)

    def _render_dataset(self, dataset: DatasetDoc) -> str:
        """Render a dataset section."""

        parts = [f"<h2>Dataset: {dataset.dataset_type}</h2>"]
        if dataset.columns:
            cols = "".join(
                f"<li>{col.name} ({col.data_type}){' required' if col.required else ''}</li>" for col in dataset.columns
            )
            parts.append(f"<ul>{cols}</ul>")
        return "\n".join(parts)
