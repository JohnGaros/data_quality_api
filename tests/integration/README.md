# Integration Tests

## Purpose

- Confirm that major components work together correctly (API, rule engine, metadata, storage).

## Typical scenarios

- Submit an upload and check that validation jobs, reports, and metadata entries are created.
- Exercise configuration changes and approvals end-to-end.

## When to run

- During release preparation or when changing cross-module behaviour.
- After updating external dependencies like databases or message queues.
