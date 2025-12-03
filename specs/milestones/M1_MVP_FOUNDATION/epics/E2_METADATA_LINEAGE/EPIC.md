# Epic: Metadata & Lineage

**Epic ID:** E2_METADATA_LINEAGE
**Milestone:** M1_MVP_FOUNDATION
**Status:** Not Started
**Progress:** 0%

## Overview

The Metadata & Lineage epic implements the metadata registry, audit trail, and lineage tracking infrastructure to support compliance, troubleshooting, and observability. This epic establishes the metadata layer as the system of record for all job executions, configuration changes, and data transformations.

This epic focuses on capturing metadata at every stage of the validation pipeline: job submissions, cleansing transformations, profiling snapshots, validation results, and user actions. Lineage tracking enables tracing data flow from upload through cleansing, profiling, and validation. Audit trails provide immutable evidence for compliance investigations.

## Scope

**In scope:**

- Metadata event model (job events, rule version events, user action events)
- Lineage tracking (cleansing_job_id → profiling_context_id → validation results)
- Immutable audit trail for configuration changes (contracts, rules, action profiles)
- Evidence pack generation (metadata + reports + audit trail)
- Compliance tag tracking (GDPR classification, lawful basis, retention policies)
- Correlation IDs for troubleshooting (job_id, tenant_id, trace_id)

**Out of scope:**

- Azure AD authentication and RBAC (deferred to M2_SECURITY_COMPLIANCE)
- Advanced analytics on metadata (dashboards, trends) - basic queries only for MVP
- Automated evidence pack scheduling - on-demand export only for MVP
- Data subject rights automation (access, erasure) - deferred to M2_SECURITY_COMPLIANCE

## Features

### Feature 1: Metadata Registry

**Status:** Not Started - 0%
**Location:** `specs/milestones/M1_MVP_FOUNDATION/epics/E2_METADATA_LINEAGE/features/metadata_registry/` (TBD)
**Description:** Metadata event model for job executions, rule versions, and user actions with lineage graph construction.

**Key Deliverables:**
- Metadata event persistence (job events, rule version events, user action events)
- Lineage graph construction (job → cleansing → profiling → validation)
- Profiling snapshot storage (field-level statistics, distributions, overrides)
- Job metadata recording (job_id, tenant_id, config_version, blob_uri, submission_source)

### Feature 2: Audit Trail

**Status:** Not Started - 0%
**Location:** `specs/milestones/M1_MVP_FOUNDATION/epics/E2_METADATA_LINEAGE/features/audit_trail/` (TBD)
**Description:** Immutable audit trail for configuration changes, compliance tag tracking, and evidence pack export.

**Key Deliverables:**
- Immutable audit trail (no updates to audit/rule_version entries; insert new versions only)
- Compliance tag tracking (gdpr_classification, lawful_basis, is_special_category, data_subject_rights)
- Evidence pack export endpoint (zip or signed package with metadata + reports + audit trail)
- Audit event queries with correlation IDs (job_id, tenant_id, trace_id)

## Dependencies

**Feature order:**

1. **metadata_registry** - Foundational (establishes event model and lineage tracking)
2. **audit_trail** - Depends on metadata_registry (builds on event model)

**External dependencies:**

- E1_CORE_VALIDATION must have basic implementation (jobs must exist to track metadata)
- dq_metadata module models must be defined (MetadataEvent, AuditEvent, ProfilingSnapshot)
- dq_stores module must support JSONB persistence (for flexible metadata storage)

## Architecture Context

This epic implements components described in:

- **Primary:** docs/METADATA_LAYER_SPEC.md - Metadata event model, lineage tracking, compliance tags
- **Architecture:** docs/ARCHITECTURE.md - Section 4.5 (Metadata Module)
- **API:** docs/API_CONTRACTS.md - Evidence pack export endpoints
- **Governance:** governance_libraries/ - GDPR classifications, retention policies

**Modules touched:**
- src/dq_metadata/ - Metadata event model, lineage tracking, audit trail
- src/dq_stores/ - JSONB persistence for metadata events
- src/dq_api/routes/ - Evidence pack export endpoints
- tests/integration/ - Metadata recording and lineage tests

## Success Criteria

- [ ] Metadata events recorded for all job executions (job_id, tenant_id, config_version, timestamps)
- [ ] Lineage tracking operational (cleansing_job_id → profiling_context_id → validation results)
- [ ] Profiling snapshots stored with field-level statistics and overrides
- [ ] Immutable audit trail working (insert-only for configuration changes)
- [ ] Compliance tags tracked (gdpr_classification, lawful_basis, data_subject_rights)
- [ ] Evidence pack export endpoint operational (zip or signed package)
- [ ] Audit event queries working with correlation IDs (job_id, tenant_id, trace_id)
- [ ] Integration tests passing for metadata recording across pipeline stages

## Progress Tracking

See [PROGRESS.md](./PROGRESS.md) for detailed feature progress (will be generated when features start).
