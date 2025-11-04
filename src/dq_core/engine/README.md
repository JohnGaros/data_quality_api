# dq_core.engine

## Purpose
- Runs the actual rule checks against uploaded datasets.
- Handles expression evaluation, derived field calculations, and error handling.

## Key components
- `rule_engine.py`: entry point for executing all active rules.
- `evaluator.py`: safely computes formulas and comparisons.
- `helpers.py`: shared utilities for data preparation and profiling-driven validation contexts.

## Notes
- Performance and accuracy improvements typically happen here.
- Profiling data is ingested up front so each job runs inside a profiling-driven validation context tailored to the dataset.
- When adding new rule types, document assumptions so PMs can explain behaviour to stakeholders.
