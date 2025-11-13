"""Utilities for building profiling-driven validation contexts and preparing datasets."""

from __future__ import annotations

from typing import Optional

from dq_profiling.engine.context_builder import (
    ProfilingContext,
    ProfilingContextBuilder,
)
from dq_profiling.models.profiling_job import ProfilingJob
from dq_profiling.models.profiling_snapshot import ProfilingSnapshot

_context_builder = ProfilingContextBuilder()


def build_profiling_context(
    snapshot: ProfilingSnapshot,
    job: Optional[ProfilingJob] = None,
) -> ProfilingContext:
    """Compatibility helper that delegates to dq_profiling."""

    return _context_builder.build(snapshot, job=job)
