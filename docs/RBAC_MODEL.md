# Role-Based Access Control (RBAC) Model

## 1. Purpose
- Define who can do what within the Data Quality Assessment API.
- Provide supervisors and engineers with a clear reference when implementing security controls.
- Support compliance audits by showing that access is intentional and documented.

## 2. Core roles
| Role | Description | Primary goals |
| ---- | ----------- | ------------- |
| **Uploader** | External or internal users who submit data files and review results. | Upload datasets, monitor job status, download reports. |
| **Configurator** | Data governance staff or tenant admins who manage rules, mappings, and configurations. | Maintain rule library, run sandbox tests, request promotions. |
| **Admin** | Platform operators responsible for security, tenant management, and compliance oversight. | Manage users, tenants, approvals, metadata exports, and integrations. |

## 3. Access matrix
### 3.1 Functional access (API endpoints)
| Capability | Uploader | Configurator | Admin | Notes |
| ----------- | -------- | ------------ | ----- | ----- |
| Submit uploads (`POST /uploads`) | ✅ | ✅ | ✅ | Admins may upload for troubleshooting. |
| Check job status / download reports (`GET /uploads/...`) | ✅ | ✅ | ✅ | Admin access primarily for support. |
| Rerun jobs (`POST /uploads/{job_id}/rerun`) | ❌ | ✅ | ✅ | Requires elevated approval. |
| View rules (`GET /rules`) | ❌ | ✅ | ✅ | Admins audit changes; Uploaders view only via reports. |
| Import/update rules (`POST /rules/import`, `PATCH /rules/{id}`) | ❌ | ✅ | ✅ (review only) | Admins approve, not author. |
| Validate draft rules (`POST /rules/validate`) | ❌ | ✅ | ✅ | Admin typically observes results. |
| Manage logical fields/mappings (`/logical-fields`, `/mappings`) | ❌ | ✅ | ✅ | Admin oversight for governance. |
| Configuration lifecycle (`/configs/...`) | ❌ | ✅ (submit) | ✅ (approve/promote/rollback) | Configurators cannot self-approve production. |
| Manage tenants and users (`/tenants`, `/users`, `/tokens`) | ❌ | ❌ | ✅ | Admin-only to preserve separation of duties. |
| Notifications settings (`/notifications/...`) | ❌ | ✅ | ✅ | Configurators manage tenant-level alerts; Admin sets defaults. |
| Metadata queries (`/metadata/...`) | ❌ | ✅ (lineage) | ✅ (full access) | Configurator access limited to their tenants. |
| System metrics/audit log (`/metrics`, `/audit-log`) | ❌ | ❌ | ✅ | Sensitive operational data. |

### 3.2 Data access
| Data object | Uploader | Configurator | Admin | Notes |
| ----------- | -------- | ------------ | ----- | ----- |
| Own uploads and reports | Read/Download | Read | Read | Uploader limited to their submissions. |
| Tenant rule library | View (via reports only) | Create/Update | View/Approve | Admin cannot edit rule expressions. |
| Metadata (lineage, audit events) | ❌ | View (tenant scope) | View (all tenants), Export | Admin can generate regulator packs. |
| Secrets / credentials | ❌ | ❌ | Manage | Admin controls via security module. |
| System logs & metrics | ❌ | ❌ | View | Restricted for security/compliance. |

## 4. Separation of duties
- Uploaders cannot modify rules or configurations to maintain objectivity.
- Configurators prepare changes but require Admin approval for production impact.
- Admins oversee promotions, tenant access, and compliance exports but cannot bypass change management by editing rules directly.
- Service accounts (future) inherit least-privilege scopes aligned with their automated task (e.g., `service-uploader`, `service-reporting`).

## 5. Implementation notes
- Enforce scopes via Azure AD app roles mapped to these RBAC roles.
- API gateway (Azure API Management or FastAPI dependencies) checks tokens for required role before executing handlers.
- Audit every admin and configurator action through the metadata layer (`dq_metadata`) for traceability.
- Provide read-only views (dashboards, exports) for auditors without granting admin privileges.

## 6. Open follow-ups
- Define sub-roles or custom scopes if additional personas appear (e.g., Compliance auditor, Support engineer).
- Clarify whether Uploaders need self-service access to historical reports beyond their own submissions.
- Decide on emergency break-glass access procedures and logging requirements.
