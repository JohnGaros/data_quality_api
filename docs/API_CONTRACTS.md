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
- **Cleansing job stages:** `planned`, `running`, `succeeded`, `failed`, `skipped` (used when validation runs without cleansing).
- **Rule severity:** `hard` (blocks) or `soft` (warns).
- **Identifiers:** UUID strings supplied by the platform; clients provide idempotency keys via header `X-Idempotency-Key`.
- **Profiling context metadata:** `profiling_context_id`, `profiled_at`, and a list of dynamic threshold overrides applied during validation.
- **Upload orchestration:** Until the organization finalises an approach, clients may either upload files directly or supply blob references gathered from an external upload service. The DQ API always expects an immutable blob URI plus integrity metadata (ETag or checksum).

## 4. Endpoint catalog

### 4.1 Upload and validation jobs (Uploader scope)
> **Decoupled uploads:** Direct file uploads remain supported. When uploads are handled by another service, that service (or middleware) will call the placeholder `external uploads` endpoint with blob metadata so the DQ API can queue validation jobs. The choice between event, webhook, or polling triggers will be documented once decided.

| Method | Path | Purpose | Notes |
| ------ | ---- | ------- | ----- |
| POST | `/uploads` | Submit one or more files for validation | Multipart form with `tenant_id`, optional `config_version`, file attachments. Returns `job_id` and `profiling_context_id`. |
| POST | `/external-uploads` | Register a blob already stored in Azure Blob Storage (future) | JSON payload with `tenant_id`, `blob_uri`, `etag`, `content_type`, optional profiling overrides. Designed for event/webhook integrations once orchestration path is chosen. |
| GET | `/uploads/{job_id}` | Check job status | Includes timestamps, counts, severity breakdown, active config version, and profiling-driven context metadata. |
| GET | `/uploads/{job_id}/report` | Download validation report | Query `format=json\|csv`. Includes list of failed rows, rules, and profiling adjustments that impacted outcomes. |
| POST | `/uploads/{job_id}/rerun` | Revalidate with latest config | Admin or Configurator scope; creates new job linked to original and rebuilds the profiling-driven validation context. |

### 4.2 Data cleansing rules and jobs (Configurator scope)
#### Rule catalog
| Method | Path | Purpose | Notes |
| ------ | ---- | ------- | ----- |
| GET | `/cleansing-rules` | List cleansing rules | Filters: `status`, `category`, `tenant`, `transformation_type`. |
| GET | `/cleansing-rules/{rule_id}` | Fetch cleansing rule details | Returns ordered transformation steps, preconditions, and rollback policy. |
| POST | `/cleansing-rules/import` | Upload cleansing rule template | Accepts Excel/JSON payload; validates schema and stores as draft version. |
| PATCH | `/cleansing-rules/{rule_id}` | Update cleansing rule metadata | Edit description, activation window, default chaining behaviour. |
| POST | `/cleansing-rules/validate` | Dry-run cleansing rule set | Accepts sample dataset reference; returns transformed preview and metrics. |

#### Job operations
| Method | Path | Purpose | Notes |
| ------ | ---- | ------- | ----- |
| POST | `/cleansing-jobs` | Launch cleansing job | Body includes `dataset_type`, `tenant_id`, optional `rule_version`, chaining preferences. Returns `cleansing_job_id`. |
| GET | `/cleansing-jobs` | List cleansing jobs | Supports filters: `tenant_id`, `status`, `dataset_type`, `submitted_by`. |
| GET | `/cleansing-jobs/{job_id}` | Check cleansing job status | Includes before/after row counts, rejected records, linked validation job if chained. |
| POST | `/cleansing-jobs/{job_id}/rerun` | Rerun cleansing job | Optionally supply new rule version; records reason in metadata. |
| POST | `/cleansing-jobs/{job_id}/chain-validation` | Trigger validation with cleansed output | Creates validation job referencing cleansing output; returns new `job_id`. |

### 4.3 Rule library management (Configurator scope)
> Rule endpoints are segmented by rule family (validation, profiling, cleansing) so governance can manage promotions independently.
| Method | Path | Purpose | Notes |
| ------ | ---- | ------- | ----- |
| GET | `/rules` | List rules with filters | Supports query params: `status`, `category`, `severity`, `tenant`. |
| GET | `/rules/{rule_id}` | Fetch specific rule details | Returns expression, linked logical fields, metadata. |
| POST | `/rules/import` | Upload rule template file | Accepts Excel/JSON payload; validates and stores as draft configuration. |
| PATCH | `/rules/{rule_id}` | Update rule metadata | Allows editing severity, description, activation dates. |
| POST | `/rules/validate` | Dry-run rule set | Accepts sample dataset reference; returns validation outcome without persisting. |

### 4.4 Logical fields and mappings (Configurator scope)
| Method | Path | Purpose | Notes |
| ------ | ---- | ------- | ----- |
| GET | `/logical-fields` | List logical fields | Includes description, data type, default transformations. |
| POST | `/logical-fields` | Create or update logical field | Idempotent via field key; captures author and version comment. |
| GET | `/mappings` | Retrieve field mappings per tenant | Query by `tenant_id` and optionally `version`. |
| POST | `/mappings` | Upload mapping template | Validates column references and calculation syntax. |

### 4.5 Configuration lifecycle (Configurator + Admin scope)
| Method | Path | Purpose | Notes |
| ------ | ---- | ------- | ----- |
| GET | `/configs` | List configuration versions | Shows status: `draft`, `pending_approval`, `approved`, `retired`. |
| POST | `/configs/{config_id}/submit` | Request approval | Moves draft to pending state; triggers workflow notification. |
| POST | `/configs/{config_id}/approve` | Approve configuration | Admin only; records approver and activation timestamp. |
| POST | `/configs/{config_id}/promote` | Promote to production | Activates configuration for specified tenants. |
| POST | `/configs/{config_id}/rollback` | Restore previous version | Reverts active config; logs reason. |

### 4.6 Tenant and user administration (Admin scope)
| Method | Path | Purpose | Notes |
| ------ | ---- | ------- | ----- |
| POST | `/tenants` | Create tenant | Requires name, contact info, retention policy. Returns tenant credentials stub. |
| PATCH | `/tenants/{tenant_id}` | Update tenant settings | Enable/disable, tweak retention, assign default configs. |
| GET | `/tenants` | List tenants with status | Supports pagination, filter by active flag. |
| POST | `/users` | Invite user | Body includes role, email, tenant scope. Sends activation email. |
| PATCH | `/users/{user_id}` | Update role or disable user | Audit trail captures modifier and reason. |
| POST | `/tokens` | Issue integration token | Admin chooses scopes and expiry. Response masks secret after first view. |

### 4.7 Observability and auditing (Admin scope)
| Method | Path | Purpose | Notes |
| ------ | ---- | ------- | ----- |
| GET | `/metrics` | Retrieve platform metrics snapshot | Returns counts, durations, queue depth; formatted for dashboards. |
| GET | `/audit-log` | Query audit events | Filters: `actor`, `action`, `tenant`, `date_range`. Supports pagination. |
| GET | `/health` | Lightweight health check | Used by load balancers; returns dependency status. |

### 4.8 Notifications and webhooks (Configurator/Admin scope)
| Method | Path | Purpose | Notes |
| ------ | ---- | ------- | ----- |
| GET | `/notifications/settings` | View current notification preferences | Includes email groups, webhook URLs, severity thresholds. |
| POST | `/notifications/settings` | Create or update preferences | Validates webhook endpoints via challenge handshake. |
| POST | `/notifications/test` | Send test notification | Confirms channels before going live. |

### 4.9 Metadata and audit catalog (Configurator/Admin scope)
| Method | Path | Purpose | Notes |
| ------ | ---- | ------- | ----- |
| GET | `/metadata/assets` | List registered data assets | Filters by `tenant_id`, `dataset_type`, `classification`. |
| GET | `/metadata/jobs` | Query cleansing and validation job lineage | Supports filters: `job_id`, `tenant_id`, `status`, `config_version`, `cleansing_rule_version`, date range. |
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
  "profiling_overrides": {
    "PaymentAmount": {
      "null_ratio": 0.02
    }
  },
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
    "profiling_context_id": "ctx-456",
    "submitted_at": "2024-05-09T12:30:00Z"
  },
  "meta": {},
  "errors": []
}

### 5.2 Example: POST `/external-uploads` (future)
```json
{
  "tenant_id": "TNT-001",
  "blob_uri": "https://storage.example.com/tenants/tnt-001/billing/billing_2024_09_01.csv",
  "etag": "\"0x8DB2B3E7C5A1F42\"",
  "content_type": "text/csv",
  "metadata": {
    "source_system": "ops-bridge",
    "upload_trigger": "event_grid"
  },
  "profiling_overrides": {
    "PaymentAmount": {
      "null_ratio": 0.02
    }
  }
}
```
```json
{
  "data": {
    "job_id": "job-789",
    "profiling_context_id": "ctx-987",
    "status": "pending",
    "received_via": "external_uploads"
  },
  "meta": {
    "blob_uri": "https://storage.example.com/tenants/tnt-001/billing/billing_2024_09_01.csv"
  },
  "errors": []
}
```

### 5.3 Example: GET `/uploads/{job_id}`
```json
{
  "data": {
    "job_id": "job-123",
    "tenant_id": "TNT-001",
    "status": "succeeded",
    "config_version": "cfg_2024_05_01",
    "profiling_context_id": "ctx-456",
    "profiling_adjustments": [
      {
        "field": "PaymentAmount",
        "metric": "null_ratio",
        "baseline": 0.02,
        "adjusted_threshold": 0.03,
        "impact": "warning"
      }
    ],
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

### 5.4 Example: POST `/cleansing-jobs`
```json
{
  "tenant_id": "TNT-001",
  "dataset_type": "billing",
  "source_job_id": "job-123",
  "rule_version": "cln_2024_06_01",
  "chain_validation": true,
  "options": {
    "deduplicate_by": ["InvoiceNumber", "BillingPeriod"],
    "standardize_currency": "tenant_default"
  }
}
```
```json
{
  "data": {
    "cleansing_job_id": "cln-job-456",
    "status": "planned",
    "rule_version": "cln_2024_06_01",
    "chain_validation": true
  },
  "meta": {
    "linked_upload_job_id": "job-123"
  },
  "errors": []
}
```

### 5.5 Example: GET `/cleansing-jobs/{job_id}`
```json
{
  "data": {
    "cleansing_job_id": "cln-job-456",
    "tenant_id": "TNT-001",
    "dataset_type": "billing",
    "status": "succeeded",
    "rule_version": "cln_2024_06_01",
    "before_counts": {
      "rows": 12850,
      "duplicates": 320
    },
    "after_counts": {
      "rows": 12530,
      "deduplicated": 300,
      "rejected": 20
    },
    "rejected_sample": [
      {
        "row_number": 512,
        "reason": "Missing CustomerId after normalization"
      }
    ],
    "started_at": "2024-06-01T10:05:00Z",
    "finished_at": "2024-06-01T10:07:35Z",
    "linked_validation_job_id": "job-789"
  },
  "meta": {
    "chain_state": "complete"
  },
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
