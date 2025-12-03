# Epic: RBAC & GDPR

**Epic ID:** E3_RBAC_GDPR
**Milestone:** M2_SECURITY_COMPLIANCE
**Status:** Not Started
**Progress:** 0%

## Overview

The RBAC & GDPR epic implements Azure AD authentication, role-based access control, GDPR compliance infrastructure, retention policies, and evidence pack generation. This epic transforms the platform from a development prototype into a production-ready system capable of safely handling personal data with full compliance and audit capabilities.

Azure AD integration provides OAuth 2.0 authentication with multi-tenant claims validation. RBAC middleware enforces role-based access on all API endpoints. Governance profiles capture GDPR classifications, lawful basis, data subject rights, and retention policies. Evidence packs enable compliance audits and breach investigations.

## Scope

**In scope:**

- Azure AD OAuth 2.0 / OpenID Connect authentication
- Multi-tenant claims validation (tenant_id, environment, roles)
- RBAC enforcement in FastAPI routes (role-based permission checks)
- Governance profiles (GDPR classification, lawful basis, special category flags)
- Compliance tag tracking in metadata (gdpr_classification, lawful_basis, data_subject_rights)
- Data subject rights endpoints (access, rectification, erasure, restriction, portability, objection)
- Retention policies per tenant with enforcement checkpoints
- Evidence pack generation (metadata + reports + audit trail)
- Azure Key Vault integration for all secrets

**Out of scope:**

- Advanced identity features (MFA, conditional access) - rely on Azure AD configuration
- Automated data subject rights fulfillment - manual approval workflows initially
- Cross-border data transfer controls - assume single Azure region initially
- Data loss prevention (DLP) scanning - deferred to future enhancements

## Features

### Feature 1: Azure AD Integration

**Status:** Not Started - 0%
**Location:** `specs/milestones/M2_SECURITY_COMPLIANCE/epics/E3_RBAC_GDPR/features/azure_ad_integration/` (TBD)
**Description:** Azure AD OAuth 2.0 authentication with multi-tenant claims validation and RBAC enforcement in FastAPI routes.

**Key Deliverables:**
- Azure AD OAuth 2.0 / OpenID Connect authentication
- Token validation middleware (dq_security/auth_provider.py)
- Multi-tenant claims extraction (tenant_id, environment, roles from JWT)
- RBAC middleware for FastAPI routes (role-based permission checks)
- Azure Key Vault integration for secrets (DB credentials, API keys)

### Feature 2: GDPR Compliance

**Status:** Not Started - 0%
**Location:** `specs/milestones/M2_SECURITY_COMPLIANCE/epics/E3_RBAC_GDPR/features/gdpr_compliance/` (TBD)
**Description:** GDPR compliance infrastructure including classifications, compliance tags, data subject rights, and breach investigation support.

**Key Deliverables:**
- Governance profiles (classification, lawful basis, special category flags)
- Compliance tag tracking in dq_metadata (gdpr_classification, lawful_basis, is_special_category)
- Data subject rights endpoints (access requests, rectification, erasure, restriction, portability, objection)
- Breach investigation support (metadata exports with lineage + audit trail)
- Privacy impact assessment (PIA) documentation

### Feature 3: Storage & Retention

**Status:** Not Started - 0%
**Location:** `specs/milestones/M2_SECURITY_COMPLIANCE/epics/E3_RBAC_GDPR/features/storage_retention/` (TBD)
**Description:** Configurable retention policies per tenant with enforcement checkpoints and audit logging.

**Key Deliverables:**
- Retention policy configuration per tenant (retention_days, enforcement_mode)
- Enforcement checkpoints (lifecycle policies on Azure Blob)
- Retention decision audit logging (immutable trail before deletion)
- Secure report distribution process (encrypted exports, SAS tokens)
- Evidence pack generation endpoint (zip or signed package)

## Dependencies

**Feature order:**

1. **azure_ad_integration** - Foundational (authentication must work before GDPR features)
2. **gdpr_compliance** - Depends on azure_ad_integration (RBAC needed for data subject rights)
3. **storage_retention** - Depends on azure_ad_integration (RBAC needed for retention policy management)

**External dependencies:**

- M1_MVP_FOUNDATION complete (core pipeline must exist to secure)
- E2_METADATA_LINEAGE complete (audit trail must exist for evidence packs)
- Azure AD tenant configured with app registration
- Azure Key Vault provisioned with secret access policies

## Architecture Context

This epic implements components described in:

- **Primary:** docs/SECURITY_GUIDE.md - Authentication, RBAC, Key Vault, GDPR
- **RBAC:** docs/RBAC_MODEL.md - Role definitions and permission matrix
- **Metadata:** docs/METADATA_LAYER_SPEC.md - Compliance tags and audit events
- **Governance:** governance_libraries/ - PII classifications, retention policies, access controls

**Modules touched:**
- src/dq_security/ - Azure AD auth, RBAC, Key Vault, audit logging
- src/dq_metadata/ - Compliance tags, audit events, evidence export
- src/dq_api/ - RBAC middleware and authentication gates
- infra/azure/ - Key Vault configuration, Azure AD app registration

## Success Criteria

- [ ] Azure AD OAuth 2.0 authentication working (token validation, multi-tenant claims)
- [ ] RBAC enforced on all API endpoints (tenant + role + environment checks)
- [ ] Governance profiles defined for all datasets processing personal data
- [ ] Compliance tags tracked in metadata (gdpr_classification, lawful_basis, is_special_category)
- [ ] Data subject rights endpoints operational (access, rectification, erasure, restriction, portability, objection)
- [ ] Retention policies configurable per tenant with enforcement checkpoints
- [ ] Retention decision audit logging working (immutable trail before deletion)
- [ ] Evidence pack export endpoint operational (zip or signed package)
- [ ] Azure Key Vault integration complete (no secrets in config files)
- [ ] Security hardening complete per docs/SECURITY_GUIDE.md

## Progress Tracking

See [PROGRESS.md](./PROGRESS.md) for detailed feature progress (will be generated when features start).
