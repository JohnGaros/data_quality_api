# Milestone: MVP Foundation

**Milestone ID:** M1_MVP_FOUNDATION
**Status:** In Progress
**Target:** 2025-12-30
**Priority:** P0

## Overview

The MVP Foundation milestone delivers the semantic catalog foundation and core data quality validation pipeline with cleansing, profiling, and validation capabilities. This milestone establishes the contract-driven architecture (CDA) as the foundation for all future features, with the catalog as the single source of truth for semantic definitions, implements multi-tenant isolation, and creates the metadata tracking infrastructure for lineage and audit trails.

This is the minimum viable product needed to process customer datasets, validate them against business rules, and produce validation reports. The semantic catalog ensures all contracts, rules, and engines reference standardized entity/attribute definitions. All engines (cleansing, profiling, validation) consume DataContracts and rule bindings from the contract registry, which reference the global catalog.

## Goals

1. **Semantic Catalog Foundation:** Establish catalog as single source of truth with representative domain coverage, Postgres persistence, and contract validation
2. **Core Pipeline Operational:** End-to-end workflow from file upload → cleansing → profiling → validation → results export
3. **Contract-Driven Architecture:** All engines consume versioned DataContracts + orthogonal libraries (rule_libraries, schema_libraries, catalog_libraries) with validated catalog references
4. **Multi-Tenant Isolation:** All jobs, contracts, and metadata scoped by tenant_id + environment (catalog is global)
5. **Metadata Foundation:** Job lineage, profiling snapshots, validation results tracked in dq_metadata with catalog IDs
6. **Testing Infrastructure:** Integration tests covering full pipeline + file-based fixtures

## Success Criteria

- [ ] Semantic catalog established with 3-4 domains and 15-20 attributes (representative coverage)
- [ ] Catalog persisted to Postgres with contract validation (100% referential integrity)
- [ ] End-to-end validation workflow working: upload → cleanse → profile → validate → results
- [ ] Contract registry operational (DataContracts + RuleBindings stored in Postgres JSONB with validated catalog references)
- [ ] Cleansing engine produces cleansed datasets + rejection sets with transformation metrics
- [ ] Profiling engine generates snapshots (field-level statistics + distributions) with catalog metadata
- [ ] Validation engine executes rule bindings within profiling-driven context using catalog-aware resolution
- [ ] Metadata layer records job lineage, profiling context IDs, cleansing job IDs, and catalog IDs
- [ ] Multi-tenant isolation enforced (tenant_id + environment filtering on all queries; catalog is global)
- [ ] Integration tests passing for core workflow with catalog-backed contracts
- [ ] File-based test fixtures (Excel/CSV loaders and savers) working

## Epics

### E0: Catalog & Schema Foundation - 0% (Not Started)

Establishes the semantic catalog as the single source of truth for entity and attribute definitions. Implements domain modeling, Postgres persistence, contract validation for referential integrity, and basic engine integration.

**Features:**

- **semantic_model_authoring** (Not Started) - 0%
  - 3 new domain YAML files (Product, Transaction, Billing)
  - Catalog taxonomy design (naming conventions, tag taxonomy)
  - Domain modeling documentation

- **catalog_persistence** (Not Started) - 0%
  - PostgresCatalogStore implementation
  - Canonical JSON serialization for catalog entities/attributes
  - Updated seed script for Postgres

- **contract_validation** (Not Started) - 0%
  - CatalogReferenceValidator class
  - Pre-persistence validation hooks in ContractRegistry
  - Referential integrity enforcement

- **catalog_engine_integration** (Not Started) - 0%
  - Validation engine catalog resolution
  - Profiling engine metadata enrichment
  - E2E integration tests with catalog-backed contracts

**Scope:**

- Semantic catalog with 3-4 domains and 15-20 attributes (representative coverage)
- Postgres persistence (replace in-memory storage)
- Contract validation (prevent orphaned catalog references)
- Engine integration (validation/profiling consume catalog metadata)

**Blocks:** E1.F2 (core_rule_engine) - cannot safely execute rule bindings without validated catalog references

### E1: Core Validation - ~25% (In Progress)

Implements the core validation pipeline components: rule engine, API upload endpoints, file processing utilities, and end-to-end testing infrastructure.

**Features:**

- **e2e_file_testing** (In Progress) - ~30%
  - Excel/CSV file loaders and savers for testing
  - Test fixtures for datasets, contracts, rules
  - End-to-end test harness

**Scope:**

- Rule engine core (logical field mapping, rule catalog loader, per-tenant schema mappings)
- API intake controller (CSV/Excel parsing, size limits, idempotency keys)
- File processing utilities for testing (load/save datasets, validation results, profiling snapshots)

### E2: Metadata & Lineage - 0% (Not Started)

Implements metadata registry, audit trail, and lineage tracking infrastructure to support compliance and troubleshooting.

**Features:**

- **metadata_registry** (Not Started) - 0%

  - Metadata event model (job events, rule version events, user action events)
  - Lineage tracking (cleansing_job_id → profiling_context_id → validation results)
  - Immutable audit trail for configuration changes

- **audit_trail** (Not Started) - 0%
  - Evidence export endpoint (zip or signed package)
  - Compliance tag tracking (GDPR classification, lawful basis, retention policies)
  - Audit event queries and correlation IDs

**Scope:**

- Job, rule version, user action event persistence
- Lineage graph construction (job → cleansing → profiling → validation)
- Evidence pack generation (metadata + reports)

## Dependencies

**Requires:** None (foundational milestone)

**Blocks:**

- M2_SECURITY_COMPLIANCE (security features depend on working pipeline)
- M3_SCALE_OPERATIONS (operations features depend on secured pipeline)

## Architecture Context

This milestone implements components described in:

- **Primary:** docs/ARCHITECTURE.md - Core modules (dq_contracts, dq_cleansing, dq_profiling, dq_core)
- **Contracts:** docs/CONTRACT_DRIVEN_ARCHITECTURE.md - CDA principles and patterns
- **Metadata:** docs/METADATA_LAYER_SPEC.md - Lineage recording and audit events
- **API:** docs/API_CONTRACTS.md - Upload endpoints and job status endpoints

**Modules touched:**

- src/dq_catalog/ - Semantic catalog (models, loader, repository, serialization)
- src/dq_contracts/ - Contract registry with catalog validation
- src/dq_cleansing/ - Cleansing engine
- src/dq_profiling/ - Profiling engine and context builder with catalog metadata
- src/dq_core/ - Rule engine and evaluator with catalog resolution
- src/dq_metadata/ - Metadata layer with catalog IDs
- src/dq_api/ - FastAPI routes for upload, job management, and catalog endpoints
- src/dq_stores/ - PostgresCatalogStore implementation
- catalog_libraries/ - Domain YAML files
- tests/integration/ - E2E tests with catalog-backed contracts

## Progress Tracking

See [PROGRESS.md](./PROGRESS.md) for detailed epic and feature progress.
