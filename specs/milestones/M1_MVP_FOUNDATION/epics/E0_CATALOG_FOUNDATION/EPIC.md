# Epic: Catalog & Schema Foundation

**Epic ID:** E0_CATALOG_FOUNDATION
**Milestone:** M1_MVP_FOUNDATION
**Status:** Not Started
**Progress:** 0%

## Overview

The Catalog & Schema Foundation epic establishes the semantic catalog as the single source of truth for entity and attribute definitions across the platform. This foundational epic ensures that all contracts, rules, and engines reference standardized catalog IDs rather than ad-hoc field names, enabling semantic consistency, reusability, and referential integrity.

This epic delivers representative domain coverage (Customer, Product, Transaction, Billing), persistent storage (Postgres), contract validation against catalog references, and basic engine integration. The catalog follows an append-only versioning pattern where IDs are immutable (e.g., `customer_email_v2`) to prevent breaking changes.

## Rationale

The catalog is foundational infrastructure that other components depend on:

1. **Referential Integrity**: Contracts currently can reference non-existent `catalog_entity_ids` and `catalog_attribute_id` without validation
2. **Semantic Consistency**: Rules and mappings need stable, versioned semantic definitions
3. **Blocking Dependency**: E1.F2 (core_rule_engine) requires validated catalog references to safely execute rule bindings
4. **Platform Integrity**: Contract-driven architecture demands validated relationships between contracts and semantic model

## Scope

**In scope:**

- Semantic model authoring (domain modeling, taxonomy design, YAML authoring patterns)
- Persistent storage (Postgres JSONB, canonical JSON serialization)
- Contract validation (referential integrity checks on catalog references)
- Engine integration (validation/profiling engines consume catalog metadata)
- Representative domain coverage (3-4 domains with 15-20 attributes)
- Seed script and API endpoints for catalog CRUD

**Out of scope:**

- External catalog sync (Collibra/Purview integration) - deferred to M2/M3
- Advanced relationship types beyond simple references - deferred to future
- Catalog search/discovery UI - CLI-only for M1
- Automated catalog ID generation tooling - manual YAML authoring for M1
- Multi-language support - English-only descriptions for M1
- Catalog-driven UI generation - deferred to future

## Features

### Feature 1: Semantic Model Authoring & Design

**Status:** Not Started - 0%
**Location:** `specs/milestones/M1_MVP_FOUNDATION/epics/E0_CATALOG_FOUNDATION/features/semantic_model_authoring/`
**Duration:** 2 weeks
**Description:** Create representative catalog coverage with well-defined domains, taxonomies, and authoring patterns.

**Key Deliverables:**
- 3 new domain YAML files (Product, Transaction, Billing)
- Catalog taxonomy design (naming conventions, tag taxonomy, relationship types)
- Domain modeling documentation (DOMAIN_MODELING.md)
- Enhanced authoring guidelines

**Success Criteria:**
- 15-20 total attributes across 4 domains (including existing customer domain)
- Consistent naming conventions (`{domain}_{field}_v{N}`)
- Accurate PII classifications
- At least 2 entity relationships defined

### Feature 2: Catalog Persistence Layer

**Status:** Not Started - 0%
**Location:** `specs/milestones/M1_MVP_FOUNDATION/epics/E0_CATALOG_FOUNDATION/features/catalog_persistence/`
**Duration:** 1.5 weeks
**Description:** Replace in-memory storage with Postgres, add canonical JSON serialization following the same pattern as contracts.

**Key Deliverables:**
- Postgres schema for catalog entities/attributes (JSONB storage)
- PostgresCatalogStore implementation (extends Store pattern)
- Canonical JSON serialization for CatalogEntity and CatalogAttribute
- Updated seed script for Postgres persistence
- Unit and integration tests for repository CRUD operations

**Success Criteria:**
- Catalog data persists across app restarts
- Query performance < 50ms for typical lookups
- Seed script runs cleanly for all 4 domains
- 100% test coverage for store operations

### Feature 3: Contract Validation & Referential Integrity

**Status:** Not Started - 0%
**Location:** `specs/milestones/M1_MVP_FOUNDATION/epics/E0_CATALOG_FOUNDATION/features/contract_validation/`
**Duration:** 2 weeks
**Description:** Prevent contracts from referencing non-existent catalog IDs through pre-persistence validation.

**Key Deliverables:**
- CatalogReferenceValidator class
- Pre-persistence validation hook in ContractRegistry.save()
- Clear error messages for invalid catalog references
- Validation for both catalog_entity_ids and catalog_attribute_id
- Rule binding validation (when scope is catalog-based)
- Unit and integration tests for validation scenarios

**Success Criteria:**
- Contracts with valid catalog IDs save successfully
- Contracts with invalid IDs rejected with clear error messages
- Validation runs in < 100ms for typical contract (10 columns)
- Zero orphaned catalog references possible

### Feature 4: Catalog-Engine Integration

**Status:** Not Started - 0%
**Location:** `specs/milestones/M1_MVP_FOUNDATION/epics/E0_CATALOG_FOUNDATION/features/catalog_engine_integration/`
**Duration:** 1.5 weeks
**Description:** Wire catalog into validation/profiling engines for semantic metadata enrichment and lineage tracking.

**Key Deliverables:**
- Validation engine: Resolve catalog attributes during rule evaluation
- Profiling engine: Tag profiling snapshots with catalog metadata
- Metadata enrichment: Include catalog IDs in job lineage
- Enhanced API endpoints: Add filtering/search capabilities
- E2E integration tests with catalog-backed contracts

**Success Criteria:**
- E2E test passes: Upload → Validate → Results (with catalog-backed contract)
- Profiling snapshots include entity/attribute names from catalog
- API endpoints return catalog data from Postgres
- Integration tests demonstrate semantic metadata flow

## Dependencies

**Feature order:**

1. **semantic_model_authoring** - Foundational (creates domain YAML files)
2. **catalog_persistence** - Depends on F1 (needs YAML files to load into Postgres)
3. **contract_validation** - Depends on F2 (needs Postgres catalog for validation queries)
4. **catalog_engine_integration** - Depends on F3 (validation ensures only valid IDs reach engines)

**Blocks external features:**

- **E1.F2 (core_rule_engine)** - BLOCKED until E0.F3 completes (cannot safely execute rule bindings with unvalidated catalog references)

**Parallel work:**

- E1.F1 (e2e_file_testing) can continue in parallel with E0.F1 and E0.F2 (no overlap)

## Architecture Context

This epic implements components described in:

- **Primary:** docs/ARCHITECTURE.md - Section 2.5 (Semantic Catalog), Section 4.1 (dq_catalog module)
- **Refactor Plan:** CATALOG_REFACTOR_PLAN.md (moved to this epic directory)
- **Contracts:** docs/CONTRACT_DRIVEN_ARCHITECTURE.md - Catalog-driven references
- **Libraries:** catalog_libraries/README.md - YAML authoring patterns

**Modules touched:**
- src/dq_catalog/ - Models, loader, repository, serialization
- src/dq_stores/ - PostgresCatalogStore implementation
- src/dq_contracts/ - Validation hooks
- src/dq_core/ - Engine integration (rule evaluator)
- src/dq_profiling/ - Engine integration (metadata enrichment)
- src/dq_api/ - Catalog endpoints
- catalog_libraries/ - Domain YAML files
- tests/unit/ - Catalog validation tests
- tests/integration/ - E2E catalog workflow tests

## Success Criteria

- [ ] 4 domains with 15-20 total attributes in catalog_libraries/
- [ ] Catalog persisted to Postgres (not in-memory)
- [ ] 100% referential integrity (no orphaned catalog references possible)
- [ ] Contract validation rejects invalid catalog IDs with clear errors
- [ ] Profiling snapshots include catalog metadata (entity/attribute names)
- [ ] Seed script runs cleanly for all domains
- [ ] E2E test passes with catalog-backed contract
- [ ] All E1.F2 contracts can use catalog references safely
- [ ] Query performance < 50ms for typical catalog lookups
- [ ] Validation performance < 100ms for typical contract (10 columns)

## Progress Tracking

See individual feature IMPLEMENTATION.md files for detailed task breakdowns:

- `features/semantic_model_authoring/IMPLEMENTATION.md`
- `features/catalog_persistence/IMPLEMENTATION.md`
- `features/contract_validation/IMPLEMENTATION.md`
- `features/catalog_engine_integration/IMPLEMENTATION.md`

Use `/planning/checkpoint` commands to track progress at the feature level.

## Timeline

| Week | Work | Dependencies | Notes |
|------|------|--------------|-------|
| 1-2  | E0.F1 (Semantic Authoring) | None | Can parallel with E1.F1 |
| 2-3  | E0.F2 (Persistence Layer) | Requires E0.F1 YAML files | Can parallel with E1.F1 |
| 3-4  | E0.F3 (Contract Validation) | Requires E0.F2 Postgres | Blocks E1.F2 start |
| 4-5  | E0.F4 (Engine Integration) | Requires E0.F3 validation | Can parallel with E1.F2 |

**Critical Path:** E0.F1 → E0.F2 → E0.F3 (blocks E1.F2) → E0.F4

**Total Duration:** 4-6 weeks

## Risk Mitigation

### Risk: Scope creep (catalog work exceeds 6 weeks)

**Mitigation:**
- Strict scope: 3 new domains, 15-20 attributes total (not comprehensive coverage)
- Time-box E0.F1 to 2 weeks; reduce to 2 domains if needed
- E0.F4 simplified: basic wiring only, deep integration happens in E1.F2

### Risk: Catalog design changes mid-implementation

**Mitigation:**
- Front-load design in E0.F1 (taxonomy/naming decisions documented early)
- Review CATALOG_REFACTOR_PLAN.md before starting
- Checkpoint reviews at end of F1 and F2
- Append-only versioning prevents breaking changes

### Risk: Postgres persistence adds complexity

**Mitigation:**
- E0.F2 uses existing Store abstraction pattern (proven in dq_stores)
- Test DB setup already exists (integration tests use test DB)
- Fallback: If Postgres blocking, defer to post-M1 and continue with in-memory

## Notes

- Catalog is global (not tenant-scoped), but contracts referencing it remain tenant-isolated
- Append-only versioning: catalog IDs are immutable (e.g., `customer_email_v2`)
- Catalog infrastructure already exists (models, loader, repository, API) but needs hardening
- This epic prevents referential integrity issues that would be costly to fix later
- The 4-week delay to E1.F2 is acceptable given the critical importance of catalog validation
