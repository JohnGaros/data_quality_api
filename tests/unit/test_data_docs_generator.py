"""Tests for DataDocsGenerator scaffolding."""

import sys
from pathlib import Path
from unittest.mock import MagicMock

import pytest

sys.path.append(str(Path(__file__).resolve().parents[2] / "src"))

from dq_docs.generator import DataDocsGenerator
from dq_docs.models import ContractDoc


def test_generator_maps_basic_contract() -> None:
    """Generator should map simple contract objects to ContractDoc."""

    class DummyContract:
        contract_id = "c1"
        name = "Demo"
        version = "1.0"
        tenant_id = "tenant-a"
        environment = "dev"

    gen = DataDocsGenerator(tenant="tenant-a", environment="dev")
    doc = gen._map_contract_to_doc(DummyContract())
    assert isinstance(doc, ContractDoc)
    assert doc.contract_id == "c1"


def test_generator_stubs_raise_not_implemented() -> None:
    """Stubbed loaders should raise NotImplementedError until wired."""

    gen = DataDocsGenerator()
    with pytest.raises(NotImplementedError):
        gen._load_contract("c1")
    with pytest.raises(NotImplementedError):
        gen._load_job_definition("j1")
    with pytest.raises(NotImplementedError):
        gen._load_run("r1")
