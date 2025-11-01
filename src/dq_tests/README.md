# dq_tests Module

## Purpose
- Dedicated space for automated rule regression tests and reusable testing tools.
- Complements the general `tests/` directory with domain-specific scenarios.

## Components (current and planned)
- `test_cases/`: YAML or JSON definitions for complex rule suites.
- `generator.py`: builds synthetic datasets to exercise rules.
- `runner.py`: orchestrates regression runs and aggregates results.
- `reports/`: stores outputs from regression executions.

## Guidance
- Use this module when validating new rules or customer-specific configurations.
- Align scenarios with the metadata layer so test results contribute to audit evidence when needed.

