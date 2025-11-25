"""Tests for Data Docs view models."""

import sys
from pathlib import Path
from datetime import datetime

sys.path.append(str(Path(__file__).resolve().parents[2] / "src"))

from dq_docs.models import (
    ActionProfileDoc,
    ColumnDoc,
    ContractDoc,
    DatasetDoc,
    JobDefinitionDoc,
    RunDoc,
)


def test_contract_doc_instantiation() -> None:
    """Ensure ContractDoc can be constructed with nested datasets and columns."""

    col = ColumnDoc(name="id", data_type="string", required=True)
    dataset = DatasetDoc(dataset_type="customers", columns=[col])
    doc = ContractDoc(
        contract_id="contract-1",
        name="Customer Contract",
        version="1.0",
        tenant="tenant-a",
        environment="dev",
        datasets=[dataset],
    )
    assert doc.contract_id == "contract-1"
    assert doc.datasets[0].columns[0].name == "id"


def test_job_definition_doc_instantiation() -> None:
    """Ensure JobDefinitionDoc holds action profiles and tags."""

    action = ActionProfileDoc(action_profile_id="act-1", name="Notify")
    doc = JobDefinitionDoc(
        job_definition_id="job-1",
        name="Daily customers",
        tenant="tenant-a",
        environment="dev",
        tags=["daily"],
        action_profiles=[action],
    )
    assert doc.tags == ["daily"]
    assert doc.action_profiles[0].action_profile_id == "act-1"


def test_run_doc_instantiation() -> None:
    """Ensure RunDoc captures run metadata."""

    now = datetime.utcnow()
    doc = RunDoc(
        run_id="run-1",
        job_definition_id="job-1",
        contract_id="contract-1",
        contract_version="1.0",
        tenant="tenant-a",
        environment="dev",
        started_at=now,
    )
    assert doc.run_id == "run-1"
    assert doc.started_at == now
