# API Contracts — Data Quality Assessment API

## 1. Why this document exists
- Gives future agents a starting point for building or mocking the API.
- Keeps supervisors informed on which endpoints exist and what they return.
- Ensures all roles share the same understanding of input, output, and auth rules.

## 2. Base conventions
- **API root:** `/api/v1`
- **Auth:** OAuth 2.0 bearer tokens issued via Azure AD; service accounts use client credentials.
- **Roles:** Uploader, Configurator, Admin; scopes are enforced per endpoint.
- **Response shape:** JSON objects with `data`, `meta`, and `errors` keys. Empty arrays when no data.
- **Errors:** Standard HTTP status codes plus machine-readable `code` values (see section 6).

## 3. Shared objects
- **Job status values:** `pending`, `running`, `succeeded`, `failed`, `cancelled`.
- **Rule severity:** `hard` (blocks) or `soft` (warns).
- **Identifiers:** UUID strings supplied by the platform; clients provide idempotency keys via header `X-Idempotency-Key`.

## 4. Endpoint catalog

### 4.1 Upload and validation jobs (Uploader scope)
| Method | Path | Purpose | Notes |
| ------ | ---- | ------- | ----- |
| POST | `/uploads` | Submit one or more files for validation | Multipart form with `tenant_id`, optional `config_version`, file attachments. Returns `job_id`. |
| GET | `/uploads/{job_id}` | Check job status | Includes timestamps, counts, severity breakdown, and active config version. |
| GET | `/uploads/{job_id}/report` | Download validation report | Query `format=json\|csv`. Includes list of failed rows and rules. |
| POST | `/uploads/{job_id}/rerun` | Revalidate with latest config | Admin or Configurator scope; creates new job linked to original. |

### 4.2 Rule library management (Configurator scope)
| Method | Path | Purpose | Notes |
| ------ | ---- | ------- | ----- |
| GET | `/rules` | List rules with filters | Supports query params: `status`, `category`, `severity`, `tenant`. |
| GET | `/rules/{rule_id}` | Fetch specific rule details | Returns expression, linked logical fields, metadata. |
| POST | `/rules/import` | Upload rule template file | Accepts Excel/JSON payload; validates and stores as draft configuration. |
| PATCH | `/rules/{rule_id}` | Update rule metadata | Allows editing severity, description, activation dates. |
| POST | `/rules/validate` | Dry-run rule set | Accepts sample dataset reference; returns validation outcome without persisting. |

### 4.3 Logical fields and mappings (Configurator scope)
| Method | Path | Purpose | Notes |
| ------ | ---- | ------- | ----- |
| GET | `/logical-fields` | List logical fields | Includes description, data type, default transformations. |
| POST | `/logical-fields` | Create or update logical field | Idempotent via field key; captures author and version comment. |
| GET | `/mappings` | Retrieve field mappings per tenant | Query by `tenant_id` and optionally `version`. |
| POST | `/mappings` | Upload mapping template | Validates column references and calculation syntax. |

### 4.4 Configuration lifecycle (Configurator + Admin scope)
| Method | Path | Purpose | Notes |
| ------ | ---- | ------- | ----- |
| GET | `/configs` | List configuration versions | Shows status: `draft`, `pending_approval`, `approved`, `retired`. |
| POST | `/configs/{config_id}/submit` | Request approval | Moves draft to pending state; triggers workflow notification. |
| POST | `/configs/{config_id}/approve` | Approve configuration | Admin only; records approver and activation timestamp. |
| POST | `/configs/{config_id}/promote` | Promote to production | Activates configuration for specified tenants. |
| POST | `/configs/{config_id}/rollback` | Restore previous version | Reverts active config; logs reason. |

### 4.5 Tenant and user administration (Admin scope)
| Method | Path | Purpose | Notes |
| ------ | ---- | ------- | ----- |
| POST | `/tenants` | Create tenant | Requires name, contact info, retention policy. Returns tenant credentials stub. |
| PATCH | `/tenants/{tenant_id}` | Update tenant settings | Enable/disable, tweak retention, assign default configs. |
| GET | `/tenants` | List tenants with status | Supports pagination, filter by active flag. |
| POST | `/users` | Invite user | Body includes role, email, tenant scope. Sends activation email. |
| PATCH | `/users/{user_id}` | Update role or disable user | Audit trail captures modifier and reason. |
| POST | `/tokens` | Issue integration token | Admin chooses scopes and expiry. Response masks secret after first view. |

### 4.6 Observability and auditing (Admin scope)
| Method | Path | Purpose | Notes |
| ------ | ---- | ------- | ----- |
| GET | `/metrics` | Retrieve platform metrics snapshot | Returns counts, durations, queue depth; formatted for dashboards. |
| GET | `/audit-log` | Query audit events | Filters: `actor`, `action`, `tenant`, `date_range`. Supports pagination. |
| GET | `/health` | Lightweight health check | Used by load balancers; returns dependency status. |

### 4.7 Notifications and webhooks (Configurator/Admin scope)
| Method | Path | Purpose | Notes |
| ------ | ---- | ------- | ----- |
| GET | `/notifications/settings` | View current notification preferences | Includes email groups, webhook URLs, severity thresholds. |
| POST | `/notifications/settings` | Create or update preferences | Validates webhook endpoints via challenge handshake. |
| POST | `/notifications/test` | Send test notification | Confirms channels before going live. |

### 4.8 Metadata and audit catalog (Configurator/Admin scope)
| Method | Path | Purpose | Notes |
| ------ | ---- | ------- | ----- |
| GET | `/metadata/assets` | List registered data assets | Filters by `tenant_id`, `dataset_type`, `classification`. |
| GET | `/metadata/jobs` | Query validation job lineage | Supports filters: `job_id`, `tenant_id`, `status`, `config_version`, date range. |
| GET | `/metadata/rules` | Fetch rule version history | Returns version chain with approval metadata. |
| GET | `/metadata/audit-events` | Retrieve audit trail entries | Requires Admin scope; supports pagination and action filters. |
| POST | `/metadata/export` | Generate compliance evidence package | Async job returning signed URL when ready. |
| POST | `/metadata/tags` | Assign compliance tags | Body includes resource type, resource id, tags; enforces retention rules. |
| DELETE | `/metadata/tags/{tag_id}` | Remove tag with justification | Records deletion reason and actor. |

## 5. Request and response templates
### 5.1 Example: POST `/uploads`
```json
{
  "tenant_id": "TNT-001",
  "config_version": "cfg_2024_05_01",
  "files": [
    {
      "name": "billing.xlsx",
      "checksum": "1b2m..."
    }
  ]
}
```
```json
{
  "data": {
    "job_id": "job-123",
    "status": "pending",
    "submitted_at": "2024-05-09T12:30:00Z"
  },
  "meta": {},
  "errors": []
}
```

### 5.2 Example: GET `/uploads/{job_id}`
```json
{
  "data": {
    "job_id": "job-123",
    "tenant_id": "TNT-001",
    "status": "succeeded",
    "config_version": "cfg_2024_05_01",
    "summary": {
      "records_checked": 12500,
      "hard_failures": 3,
      "soft_failures": 12
    },
    "started_at": "2024-05-09T12:30:10Z",
    "finished_at": "2024-05-09T12:34:55Z"
  },
  "meta": {},
  "errors": []
}
```

## 6. Error model
- **400** `invalid_request`: Missing fields, malformed payloads.
- **401** `unauthorized`: Token missing or expired.
- **403** `forbidden`: Role lacks scope for endpoint.
- **404** `not_found`: Resource ID unknown or not visible to tenant.
- **409** `conflict`: Duplicate idempotency key, version mismatch, or concurrent update.
- **422** `validation_error`: Business rule check failed (e.g., invalid rule expression).
- **429** `rate_limited`: Client exceeded allowed requests; includes `retry_after`.
- **500** `server_error`: Unexpected failure; includes correlation ID.

## 7. Acceptance checkpoints
- Each endpoint has OpenAPI/Swagger documentation with request and response schemas.
- Mock server or contract tests verify status codes and example payloads.
- RBAC matrix confirms which roles can call each endpoint.
- Error codes mapped to user-facing messages or operational playbooks.

## 8. Open questions to resolve later
- Final decision on synchronous vs. async upload confirmation (especially for large files).
- Whether admins can impersonate other roles for troubleshooting.
- Notification delivery guarantees (at least once vs. exactly once).
- Need for bulk endpoints (e.g., export all reports for a month).
