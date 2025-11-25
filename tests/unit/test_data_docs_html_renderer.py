"""Tests for HtmlRenderer output."""

import sys
from pathlib import Path

sys.path.append(str(Path(__file__).resolve().parents[2] / "src"))

from dq_docs.models import ContractDoc, DatasetDoc, JobDefinitionDoc, RunDoc
from dq_docs.renderers.html_renderer import HtmlRenderer


def test_render_contract_doc_includes_heading() -> None:
    """Renderer should include contract id in HTML."""

    doc = ContractDoc(contract_id="c1", name=None, version=None, tenant="t1", environment="dev", datasets=[DatasetDoc(dataset_type="ds1")])
    html = HtmlRenderer().render_contract_doc(doc)
    assert "<h1>Contract: c1</h1>" in html
    assert "Dataset: ds1" in html


def test_render_job_definition_doc_includes_id() -> None:
    """Renderer should include job definition id."""

    doc = JobDefinitionDoc(job_definition_id="job-1", name=None, tenant="t1", environment="dev")
    html = HtmlRenderer().render_job_definition_doc(doc)
    assert "job-1" in html


def test_render_run_doc_includes_run_id() -> None:
    """Renderer should include run id."""

    doc = RunDoc(
        run_id="run-1",
        job_definition_id=None,
        contract_id=None,
        contract_version=None,
        tenant="t1",
        environment="dev",
    )
    html = HtmlRenderer().render_run_doc(doc)
    assert "run-1" in html
