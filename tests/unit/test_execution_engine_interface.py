"""Tests for ExecutionEngine base interface."""

import sys
from pathlib import Path

sys.path.append(str(Path(__file__).resolve().parents[2] / "src"))

from dq_engine.base import ExecutionEngine


class DummyEngine(ExecutionEngine):
    """Minimal concrete subclass for testing abstract methods."""

    def load_dataset(self, source_ref):
        return source_ref

    def persist_dataset(self, handle, target_ref):
        return target_ref

    def apply_transformations(self, handle, transformations):
        return handle

    def compute_profile(self, handle, spec):
        return {"profile": True}

    def evaluate_rules(self, handle, rules_bundle):
        return {"rules": True}


def test_execution_engine_can_be_subclassed() -> None:
    """Ensure abstract interface can be implemented."""

    engine = DummyEngine()
    assert engine.load_dataset({"uri": "x"}) == {"uri": "x"}
