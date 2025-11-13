"""Expression evaluator that reads profiling-driven context flags before applying rules."""

from __future__ import annotations

from typing import Any

from dq_profiling.engine.context_builder import ProfilingContext


class ExpressionEvaluator:
    """Minimal placeholder evaluator wired to profiling contexts."""

    def __init__(self, context: ProfilingContext) -> None:
        self._context = context

    def evaluate(self, expression: str, row: dict[str, Any]) -> Any:
        """Evaluate an expression in the context of a dataset row."""
        raise NotImplementedError(
            f"Expression evaluation for '{expression}' is pending implementation. "
            "Profiling thresholds available under self._context."
        )
