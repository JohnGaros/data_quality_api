"""Unit tests for the DQContext facade."""

import sys
from pathlib import Path
from unittest.mock import MagicMock

import pytest

sys.path.append(str(Path(__file__).resolve().parents[2] / "src"))

from dq_sdk.context import DQContext, DQJobStatus


def test_context_instantiation() -> None:
    """Context should capture tenant/environment without extra config."""

    ctx = DQContext(tenant="tenant-a", env="dev")

    assert ctx.tenant == "tenant-a"
    assert ctx.environment == "dev"


def test_run_validation_on_file_invokes_internal_helpers(monkeypatch: pytest.MonkeyPatch) -> None:
    """run_validation_on_file should orchestrate helper calls when provided."""

    ctx = DQContext(tenant="tenant-a", env="dev")
    contract = {"contract_id": "contract-1"}

    resolve_contract = MagicMock(return_value=contract)
    upload = MagicMock(return_value={"blob_uri": "https://blob"})
    cleanse = MagicMock(return_value={"cleansed": True})
    profile = MagicMock(return_value={"snapshot_id": "snap-1"})
    validate = MagicMock(return_value={"validation": "ok"})
    record = MagicMock()

    monkeypatch.setattr(ctx, "_resolve_contract_for_dataset", resolve_contract)
    monkeypatch.setattr(ctx, "_upload_local_file", upload)
    monkeypatch.setattr(ctx, "_run_cleansing_pipeline", cleanse)
    monkeypatch.setattr(ctx, "_run_profiling_pipeline", profile)
    monkeypatch.setattr(ctx, "_run_validation_engine", validate)
    monkeypatch.setattr(ctx, "_record_metadata_event", record)

    result = ctx.run_validation_on_file(
        dataset_type="billing",
        local_path="/tmp/file.csv",
        job_definition_id=None,
    )

    assert resolve_contract.called
    assert upload.called
    assert cleanse.called
    assert profile.called
    assert validate.called
    assert record.called
    assert result.status == DQJobStatus.SUCCEEDED
    assert result.contract_id == "contract-1"


def test_list_contracts_raises_not_implemented() -> None:
    """Discovery helpers should surface clear TODOs until wired up."""

    ctx = DQContext(tenant="tenant-a", env="dev")

    with pytest.raises(NotImplementedError):
        ctx.list_contracts()

    with pytest.raises(NotImplementedError):
        ctx.list_job_definitions()
