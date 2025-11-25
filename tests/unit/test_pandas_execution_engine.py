"""Tests for the Pandas execution engine stubs."""

import sys
from pathlib import Path

import pytest

sys.path.append(str(Path(__file__).resolve().parents[2] / "src"))

from dq_engine.pandas_engine import PandasExecutionEngine


def test_pandas_execution_engine_instantiation() -> None:
    """Engine should instantiate as default backend."""

    engine = PandasExecutionEngine()
    assert isinstance(engine, PandasExecutionEngine)


@pytest.mark.parametrize(
    "method_name",
    ["load_dataset", "persist_dataset", "apply_transformations", "compute_profile", "evaluate_rules"],
)
def test_pandas_execution_engine_methods_raise(method_name: str) -> None:
    """Stubbed methods should raise NotImplementedError with clear messages."""

    engine = PandasExecutionEngine()
    method = getattr(engine, method_name)
    with pytest.raises(NotImplementedError):
        # Pass minimal dummy args per method signature
        if method_name in ("load_dataset",):
            method({"uri": "x"})
        elif method_name in ("persist_dataset", "apply_transformations"):
            method(object(), {"uri": "y"} if method_name == "persist_dataset" else [])
        else:
            method(object(), {})
