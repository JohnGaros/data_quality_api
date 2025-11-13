"""Rule engine entry point."""

from __future__ import annotations

from typing import Any, Iterable, Optional

from dq_profiling.engine.context_builder import ProfilingContext, ProfilingContextBuilder
from dq_profiling.models.profiling_job import ProfilingJob
from dq_profiling.models.profiling_snapshot import ProfilingSnapshot


class RuleEngine:
    """Coordinates rule execution inside a profiling-aware context."""

    def __init__(self, context_builder: Optional[ProfilingContextBuilder] = None) -> None:
        self._context_builder = context_builder or ProfilingContextBuilder()

    def build_context(
        self,
        snapshot: ProfilingSnapshot,
        job: Optional[ProfilingJob] = None,
    ) -> ProfilingContext:
        """Expose context creation so other components can stage datasets."""

        return self._context_builder.build(snapshot, job=job)

    def run_rules(
        self,
        dataset: Iterable[dict[str, Any]],
        rules: Iterable[Any],
        snapshot: ProfilingSnapshot,
        job: Optional[ProfilingJob] = None,
    ) -> None:
        """Placeholder rule execution loop."""

        _ = self.build_context(snapshot, job=job)
        raise NotImplementedError("Rule execution pipeline will integrate with dq_profiling contexts.")
