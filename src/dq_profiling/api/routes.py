from __future__ import annotations

from typing import Any, Callable, Optional

from ..engine.profiler import ProfilingEngine
from ..models.profiling_job import ProfilingJob, ProfilingJobResult


class ProfilingRouter:
    """Placeholder router that wires profiling operations into the API layer."""

    def __init__(self, engine: Optional[ProfilingEngine] = None) -> None:
        self._engine = engine or ProfilingEngine()

    def register(self, post: Callable[[str], Any]) -> None:
        """Register endpoints with a lightweight FastAPI-compatible interface.

        Args:
            post: Callable mirroring `FastAPI.post`. The callable should accept a
                  path and return a decorator; we accept a simplified signature to
                  avoid importing the whole web stack in this placeholder.
        """

        @post("/profiling/jobs")
        def create_profiling_job(job: ProfilingJob) -> ProfilingJobResult:  # type: ignore[return-type]
            return self._engine.profile(job, dataset=[])  # dataset injected later

        @post("/profiling/jobs/{job_id}/rerun")
        def rerun_profiling_job(job_id: str) -> Any:  # type: ignore[return-type]
            raise NotImplementedError(
                "Profiling rerun endpoint will be implemented once the HTTP layer is ready."
            )
