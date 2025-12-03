# Epic: Core Validation

**Epic ID:** E1_CORE_VALIDATION
**Milestone:** M1_MVP_FOUNDATION
**Status:** In Progress
**Progress:** ~25%

## Overview

The Core Validation epic delivers the foundational components of the data quality validation pipeline: rule engine, API upload endpoints, file processing utilities, and end-to-end testing infrastructure. This epic establishes the contract-driven execution pattern where all engines consume DataContracts and rule bindings from the contract registry.

This epic focuses on getting the basic validation workflow operational: datasets are uploaded (via API or external blob reference), processed through cleansing and profiling engines, validated against rule bindings, and results are exported for review. File-based testing utilities enable rapid iteration without database dependencies.

## Scope

**In scope:**

- Rule engine core (logical field mapping, rule catalog loader, per-tenant schema mappings)
- API intake controller (CSV/Excel parsing, size limits, idempotency keys, multipart upload)
- File processing utilities for testing (load/save datasets, contracts, validation results, profiling snapshots)
- End-to-end test harness (fixtures, test data, integration tests)
- Contract resolution logic (tenant + environment + dataset_type lookup)
- Validation result aggregation and error normalization

**Out of scope:**

- Database persistence (Postgres store implementation) - deferred to later features
- Azure Blob Storage integration - deferred to M3_SCALE_OPERATIONS
- Job orchestration and ActionProfiles - deferred to M3_SCALE_OPERATIONS
- Authentication and RBAC - deferred to M2_SECURITY_COMPLIANCE
- Advanced profiling (distributions, frequent values) - basic profiling only for MVP

## Features

### Feature 1: E2E File Testing

**Status:** In Progress - ~30%
**Location:** `specs/milestones/M1_MVP_FOUNDATION/epics/E1_CORE_VALIDATION/features/e2e_file_testing/`
**Description:** Excel/CSV file loaders and savers for testing the complete data quality workflow without database dependencies.

**Key Deliverables:**
- File loaders (datasets, contracts, rules, profiling snapshots)
- File savers (cleansed datasets, rejected rows, validation results)
- Test fixtures (sample datasets, contracts, rule bindings)
- Integration test harness

### Feature 2: Core Rule Engine (Blocked)

**Status:** Not Started - 0% (BLOCKED on E0.F3 - Contract Validation)
**Location:** TBD
**Description:** Rule engine core with catalog-aware field resolution, rule catalog loader, per-tenant schema mappings, and rule binding execution within profiling-driven context.

**Blocking Dependency:** E0.F3 (Contract Validation & Referential Integrity) must complete before this feature can start. Rule engine requires validated catalog references to safely execute rule bindings.

**Key Deliverables:**
- Rule engine evaluator (dq_core/engine/rule_evaluator.py) with catalog resolution
- Profiling context integration (dynamic threshold overrides)
- Rule catalog loader (YAML/JSON/Excel → canonical JSON)
- Per-tenant schema mapping and catalog-aware field resolution

### Feature 3: API Upload Endpoints (Planned)

**Status:** Not Started - 0%
**Location:** TBD
**Description:** FastAPI routes for dataset upload via multipart file upload or external blob reference, with size limits, content-type validation, and idempotency keys.

**Key Deliverables:**
- POST /jobs/upload endpoint (multipart CSV/Excel upload)
- POST /jobs/external endpoint (external blob URI reference)
- Job ID generation and status polling endpoints
- Request validation (size limits, content-type, schema mapping)

## Dependencies

**Feature order:**

1. **e2e_file_testing** - Foundational (enables testing without database)
2. **core_rule_engine** - BLOCKED on E0.F3 (Contract Validation), also depends on e2e_file_testing (needs test fixtures)
3. **api_upload_endpoints** - Depends on core_rule_engine (needs working validation)

**External dependencies:**

- **E0.F3 (Contract Validation & Referential Integrity)** - BLOCKS E1.F2 (core_rule_engine) - must complete before rule engine can safely execute
- dq_contracts module must be operational (DataContract + RuleBinding models with validated catalog references)
- dq_catalog module must be operational (catalog entities/attributes persisted to Postgres)
- dq_cleansing module must produce cleansed datasets
- dq_profiling module must generate profiling snapshots

## Architecture Context

This epic implements components described in:

- **Primary:** docs/ARCHITECTURE.md - Section 4.2 (Core Validation Module), Section 4.6 (API Layer)
- **Contracts:** docs/CONTRACT_DRIVEN_ARCHITECTURE.md - CDA Principles
- **API:** docs/API_CONTRACTS.md - Upload endpoints specification
- **Workflow:** docs/WORKFLOW_SEQUENCES.md - Validation pipeline flow

**Modules touched:**
- src/dq_core/ - Rule engine and evaluator
- src/dq_api/routes/ - Upload and job status endpoints
- tests/fixtures/ - File loaders and savers
- tests/integration/ - E2E tests

## Success Criteria

- [ ] File loaders working for datasets, contracts, rules, profiling snapshots (Excel, CSV, JSON)
- [ ] File savers working for validation results, cleansed datasets, rejected rows
- [ ] Test fixtures available (sample datasets, contracts, rule bindings)
- [ ] Rule engine executes rule bindings within profiling-driven context
- [ ] API upload endpoints accept CSV/Excel files and external blob URIs
- [ ] Integration tests passing for full upload → validate → results flow
- [ ] Contract resolution working (tenant + environment + dataset_type lookup)
- [ ] Validation results include error normalization and correlation IDs

## Progress Tracking

See [PROGRESS.md](./PROGRESS.md) for detailed feature progress.
