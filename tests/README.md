# Test Suites Overview

## Purpose

- Ensures the platform behaves as expected before release.
- Provides confidence to stakeholders that critical paths are covered.

## Structure

- `unit/`: quick checks on individual functions or classes.
- `integration/`: verifies how modules work together (API, database, metadata).
- `regression/`: guards against previously fixed issues returning.

## How to use

- Run the appropriate suite during development and before merging changes.
- Review test results with PMs or QA leads when planning releases.
- Add new tests whenever requirements or bug fixes call for coverage.
