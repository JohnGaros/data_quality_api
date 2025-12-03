# Project Roadmap - Data Quality Platform

**Last Updated:** 2025-11-27
**Current Phase:** M1_MVP_FOUNDATION

## Vision

Production-ready, contract-driven, multi-tenant data quality platform with cleansing, profiling, validation, metadata lineage, GDPR compliance, and Azure integration.

## Current State → Production

**Overall Progress:** ~15% (Documentation complete, core implementation in progress)

---

## Milestones

### M1: MVP Foundation [In Progress] - ~15%

**Target:** 2025-12-30
**Status:** In Progress
**Priority:** P0

Core validation pipeline with semantic catalog foundation, cleansing, profiling, validation, and basic metadata tracking.

**Epics:**

- **E0: Catalog & Schema Foundation** (Not Started) - 0%
  - Establishes semantic catalog as single source of truth
  - Implements domain modeling, Postgres persistence, contract validation, engine integration
  - 4 features planned (blocks E1.F2)

- **E1: Core Validation** (In Progress) - ~25%
  - Implements rule engine, API upload endpoints, file processing, and E2E testing
  - 2 features in progress (E1.F2 blocked on E0.F3)

- **E2: Metadata & Lineage** (Not Started) - 0%
  - Implements metadata registry, audit trail, lineage tracking
  - 2 features planned

**Success Criteria:**

- [ ] Semantic catalog established with representative domain coverage (3-4 domains, 15-20 attributes)
- [ ] Catalog persisted to Postgres with contract validation (referential integrity)
- [ ] End-to-end validation workflow: upload → cleanse → profile → validate → results
- [ ] Contract-driven architecture implemented (DataContracts + rule bindings + catalog references)
- [ ] Basic metadata recording (job lineage, profiling snapshots, validation results)
- [ ] Multi-tenant isolation working (tenant_id + environment scoping)
- [ ] Integration tests passing for core workflow

**Dependencies:** None

**Blockers:** None

---

### M2: Security & Compliance [Not Started] - 0%

**Target:** 2026-01-31
**Status:** Not Started
**Priority:** P1

Azure AD authentication, RBAC, GDPR compliance, audit trails, and evidence pack generation.

**Epics:**

- **E3: RBAC & GDPR** (Not Started) - 0%
  - Azure AD integration, role-based access control, GDPR compliance tags
  - Storage retention policies, evidence pack generation
  - 3 features planned

**Success Criteria:**

- [ ] Azure AD OAuth 2.0 authentication working
- [ ] RBAC enforced on all API endpoints (tenant + role checks)
- [ ] GDPR compliance tags on all personal data processing
- [ ] Retention policies enforced with audit logging
- [ ] Evidence pack export endpoint operational

**Dependencies:** M1 completion (core pipeline must exist first)

**Blockers:** None

---

### M3: Scale & Operations [Not Started] - 0%

**Target:** 2026-02-28
**Status:** Not Started
**Priority:** P2

Performance optimization, Azure Blob storage integration, job orchestration, observability, and CI/CD.

**Epics:**

- **E4: Operations** (Not Started) - 0%
  - Tenant management, observability (logging, metrics, tracing)
  - CI/CD pipelines, infrastructure as code
  - Azure Blob integration for large datasets
  - 4 features planned

**Success Criteria:**

- [ ] Azure Blob integration for dataset storage (replace filesystem)
- [ ] Job orchestration with external triggers (Airflow, ADF)
- [ ] Observability stack (App Insights, structured logging, tracing)
- [ ] CI/CD pipelines with automated deployments
- [ ] Performance benchmarks met (≤5 min for typical datasets)

**Dependencies:** M2 completion (security must be in place for production)

**Blockers:** None

---

## Progress Summary

| Milestone | Status | Progress | Target | Dependencies |
|-----------|--------|----------|--------|--------------|
| M1: MVP Foundation | In Progress | ~15% | 2025-12-30 | None |
| M2: Security & Compliance | Not Started | 0% | 2026-01-31 | M1 complete |
| M3: Scale & Operations | Not Started | 0% | 2026-02-28 | M2 complete |

**Next Milestone:** M1_MVP_FOUNDATION
**Next Epic:** E0_CATALOG_FOUNDATION (foundational, blocks E1.F2)
**Active Features:** e2e_file_testing (E1.F1 - E2E File Testing)

---

## Notes

- Documentation phase (Feature: Product documentation and governance) is ~95% complete
- Current focus: E2E file testing infrastructure to enable full pipeline testing
- All features follow contract-driven architecture (CDA) principles
- Checkpoint-based progress tracking implemented for /clear recovery
