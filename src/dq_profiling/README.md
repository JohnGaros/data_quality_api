# dq_profiling Module

## Purpose
- Produces profiling snapshots and statistics from datasets so validation rules can adapt to real-world data behaviour.
- Builds profiling-driven validation contexts consumed by `dq_core` during rule execution.

## Layout
- `models/`: Profiling jobs, snapshots, and report-friendly structures.
- `engine/`: Profiling workers and context builders that turn cleansed datasets into reusable profiling contexts.
- `api/`: Placeholder FastAPI routes for future standalone profiling endpoints.
- `report/`: Helpers for exporting profiling results (JSON/CSV) for auditors and configurators.

## Notes
- Profiling outputs feed dynamic thresholds and metadata; ensure profiling runs after cleansing when enabled.
- Profiling rule templates live in `rule_libraries/` and are stored as canonical JSON via the registry layer.
