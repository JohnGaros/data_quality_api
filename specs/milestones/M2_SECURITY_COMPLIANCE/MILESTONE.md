# Milestone: Security & Compliance

**Milestone ID:** M2_SECURITY_COMPLIANCE
**Status:** Not Started
**Target:** 2026-01-31
**Priority:** P1

## Overview

The Security & Compliance milestone adds production-grade authentication, authorization, GDPR compliance, and audit capabilities to the platform. This milestone ensures the platform can safely handle personal data, enforce tenant isolation with role-based access controls, meet GDPR requirements, and provide evidence packs for compliance audits.

Azure AD integration provides OAuth 2.0 authentication with multi-tenant claims validation. RBAC middleware enforces role-based access on all API endpoints. Governance profiles capture GDPR classifications, lawful basis, data subject rights, and retention policies.

## Goals

1. **Authentication & Authorization:** Azure AD OAuth 2.0 integration with role-based access control (RBAC)
2. **GDPR Compliance:** Classification tags, lawful basis tracking, data subject rights support
3. **Retention Policies:** Configurable retention with enforcement checkpoints and audit logging
4. **Evidence Packs:** On-demand generation of compliance evidence (metadata + reports + audit trail)
5. **Secret Management:** Azure Key Vault integration for all secrets (DB credentials, API keys)

## Success Criteria

- [ ] Azure AD OAuth 2.0 authentication working (token validation, multi-tenant claims)
- [ ] RBAC enforced on all API endpoints (tenant + role + environment checks)
- [ ] GDPR compliance tags on all personal data processing (classification, lawful basis, special category)
- [ ] Data subject rights supported (access requests, rectification, erasure, restriction, portability, objection)
- [ ] Retention policies enforced with audit logging (decisions logged before deletion)
- [ ] Evidence pack export endpoint operational (zip or signed package)
- [ ] Azure Key Vault integration for all secrets (no credentials in config files)
- [ ] Security hardening complete (per docs/SECURITY_GUIDE.md)

## Epics

### E3: RBAC & GDPR - 0% (Not Started)

Implements Azure AD authentication, role-based access control, GDPR compliance tags, retention policies, and evidence pack generation.

**Features:**

- **azure_ad_integration** (Not Started) - 0%
  - Azure AD OAuth 2.0 / OpenID Connect authentication
  - Multi-tenant claims validation (tenant_id, environment, roles)
  - Token validation middleware
  - RBAC enforcement in dq_api routes

- **gdpr_compliance** (Not Started) - 0%
  - Governance profiles (classification, lawful basis, special category flags)
  - Compliance tag tracking in metadata (gdpr_classification, lawful_basis, data_subject_rights)
  - Data subject rights endpoints (access, rectification, erasure, restriction, portability, objection)
  - Breach investigation support (metadata exports with lineage + audit trail)

- **storage_retention** (Not Started) - 0%
  - Configurable retention policies per tenant
  - Enforcement checkpoints (lifecycle policies on Azure Blob)
  - Retention decision audit logging (immutable trail before deletion)
  - Secure report distribution process

**Scope:**
- Azure AD integration and RBAC enforcement
- GDPR compliance infrastructure (classifications, tags, rights)
- Retention policy management and enforcement
- Evidence pack generation endpoint

## Dependencies

**Requires:** M1_MVP_FOUNDATION complete (core pipeline must exist first)

**Blocks:** M3_SCALE_OPERATIONS (operations features depend on secured pipeline)

## Architecture Context

This milestone implements components described in:

- **Primary:** docs/SECURITY_GUIDE.md - Authentication, RBAC, Key Vault, GDPR
- **RBAC:** docs/RBAC_MODEL.md - Role definitions and permission matrix
- **Metadata:** docs/METADATA_LAYER_SPEC.md - Compliance tags and audit events
- **Governance:** governance_libraries/ - PII classifications, retention policies, access controls

**Modules touched:**
- src/dq_security/ - Azure AD auth, RBAC, Key Vault, audit logging
- src/dq_metadata/ - Compliance tags, audit events, evidence export
- src/dq_api/ - RBAC middleware and authentication gates
- infra/azure/ - Key Vault configuration

## Progress Tracking

See [PROGRESS.md](./PROGRESS.md) for detailed epic and feature progress (will be generated when epics start).
