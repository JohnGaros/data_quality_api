# Metadata Layer Specification — Governance, Auditability, Compliance

## 1. Purpose
- Provide a consistent way to capture, store, and query metadata across uploads, rules, and user actions.
- Satisfy governance requirements (data catalog, lineage, retention), audit obligations, and compliance reporting.
- Offer a lightweight interface for future agents to plug metadata into monitoring, reporting, and external GRC systems.

## 2. Goals and principles
- **Completeness:** Every validation job, configuration change, and user action emits structured metadata.
- **Traceability:** Metadata ties together data assets, rule versions, and outcomes for end-to-end lineage.
- **Separation of concerns:** Metadata storage and access live in their own module (`dq_metadata`) with APIs used by other layers.
- **Extensibility:** New metadata types (e.g., PII tags) can be added without breaking existing consumers.
- **Compliance-ready:** Supports regulatory evidence (who did what, when, and under which policy) with immutable history.

## 3. Metadata categories
| Category | Description | Examples |
| -------- | ----------- | -------- |
| **Data asset catalog** | Describes datasets, schemas, and retention policies per tenant. | Dataset type, file format, logical fields present, data owner. |
| **Validation job lineage** | Tracks lifecycle of each upload and derived reports. | Job ID, ingestion mode (`direct`, `external_reference`), blob URI/ETag, applied configuration version, profiling context reference, rule outcomes, downstream exports. |
| **Cleansing job lineage** | Captures pre-validation cleansing runs with their own status, rule versions, and outputs. | Cleansing job ID, dataset type, applied cleansing rule version, before/after metrics, linked validation job IDs. |
| **Profiling context snapshots** | Captures the profiling-driven validation context used during each job. | Profiling context ID, profiled_at timestamp, metric overrides per logical field. |
| **Rule and config versions** | Captures change history for validation rules, cleansing rules, mappings, and approvals. | Rule ID, expression hash, severity, approver, activation window, cleansing transformation definitions. |
| **User and system actions** | Audit trail of administrator and configurator operations. | Tenant onboarding, role changes, reruns triggered, token issuance. |
| **Compliance classifiers** | Labels for sensitive data and policy obligations. | PII flag, retention tier, regulatory tags (GDPR, SOX). |

### dq_profiling linkage
- `dq_profiling/models` emit strongly typed profiling job and snapshot records that map directly to the metadata tables noted above (`metadata_jobs.profiling_context_id`, future `metadata_profiling_snapshots`).
- `dq_profiling/engine/context_builder.py` is the single producer of profiling context IDs; metadata consumers can rely on those IDs to stitch cleansing jobs, profiling snapshots, and validation runs without rehydrating state from `dq_core`.
- Profiling overrides captured in `ProfilingJob.overrides` flow through to `ProfilingSnapshot.overrides_applied`, ensuring metadata queries can explain why thresholds differed for a run.
- Future profiling-specific endpoints will live under `dq_profiling/api`, simplifying lineage capture for proactive profiling runs that do not immediately lead to validation.

## 4. Architecture overview
- **Metadata Registry (`dq_metadata.registry.MetadataRegistry`):** Central service exposing CRUD operations for metadata objects.
- **Event stream (`dq_metadata.events`):** Standardized events emitted by API, rule engine, and admin modules.
- **Profiling context store (`dq_metadata.profiling` future):** Persists dataset profiling metrics and serves profiling-driven validation context lookups to the rule engine.
- **Storage adapters (`dq_metadata.adapters` future):** Persistence into PostgreSQL tables, Azure Log Analytics, or data lake.
- **Lineage graph (`dq_metadata.lineage`):** Builds relationships between uploads, rules, reports, and downstream exports.
- **Policy enforcement (`dq_metadata.compliance`):** Validates retention, classification, and approval policies before actions complete.

### Interaction diagram (logical)
1. Upload API (or external trigger) submits job metadata (job ID, tenant, config version, ingestion mode, blob URI/ETag when applicable) → Metadata Registry stores the upload entry.
2. If cleansing is enabled, `dq_api.services.cleansing_job_manager` creates a cleansing job record capturing rule version, chaining preference, and source dataset.
3. Cleansing engine emits transformation metrics, rejected rows, and output references → Registry links them to the cleansing job and any downstream validation job.
4. Profiling workers emit context snapshots (pre- or post-cleansing depending on policy) → Registry links profiling metrics to the relevant job via `profiling_context_id`.
5. Rule engine emits validation outcome events plus profiling adjustments → Registry associates outcomes, context overrides, cleansing references, and rule versions.
6. Config and cleansing rule managers commit new versions → Metadata layer records approval chains, transformation definitions, and refreshed profiling baselines.
7. Admin actions (tenant/user changes) → Audit events stored with context (actor, timestamp, justification).
8. Observability services query metadata for dashboards, compliance reports, SLA tracking, and cleansing-versus-validation comparisons.

## 5. Data model summary

### 5.1 Core tables / collections
- **`metadata_data_assets`**
  - `asset_id` (UUID), `tenant_id`, `dataset_type`, `schema_signature`, `classification`, `retention_policy_id`, `owner`, `created_at`, `updated_at`.
- **`metadata_jobs`**
  - `job_id`, `tenant_id`, `submission_source`, `ingestion_mode`, `blob_uri`, `blob_etag`, `config_version`, `status`, `profiling_context_id`, `profiled_at`, `profiling_adjustments` (JSONB), `input_assets` (FK array), `cleansing_job_id` (FK), `output_report_uri`, `checksum`, `submitted_by`, `submitted_at`, `completed_at`.
- **`metadata_cleansing_jobs`**
  - `cleansing_job_id`, `tenant_id`, `source_upload_job_id`, `dataset_type`, `cleansing_rule_version`, `status`, `before_counts` (JSONB), `after_counts` (JSONB), `rejected_sample` (JSONB), `output_dataset_uri`, `chain_validation` (bool), `linked_validation_job_id`, `submitted_by`, `submitted_at`, `completed_at`.
- **`metadata_rule_versions`**
  - `rule_version_id`, `rule_id`, `expression_hash`, `severity`, `change_type`, `changed_by`, `approved_by`, `approved_at`, `effective_from`, `effective_to`.
- **`metadata_cleansing_rule_versions`**
  - `cleansing_rule_version_id`, `rule_id`, `transformations` (JSONB array), `change_type`, `changed_by`, `approved_by`, `approved_at`, `effective_from`, `effective_to`, `rollback_strategy`.
- **`metadata_audit_events`**
  - `event_id`, `actor_id`, `actor_role`, `action_type`, `resource_type`, `resource_id`, `context`, `ip_address`, `initiated_at`, `is_privileged`.
- **`metadata_compliance_tags`**
  - `tag_id`, `resource_type`, `resource_id`, `tag_key`, `tag_value`, `source`, `assigned_at`.

### 5.2 Derived views
- **Lineage view:** Combines upload, cleansing, validation, rule version, and data asset tables to provide “upload → cleansing → validation → report” chains.
- **Cleansing performance view:** Tracks before/after metrics, rejection reasons, and turnaround times for cleansing runs per dataset type.
- **Profiling performance view:** Surfaces longitudinal profiling metrics and context overrides so teams can tune default thresholds per tenant; indicates whether profiling used raw or cleansed data.
- **External ingestion view:** Highlights validation and cleansing jobs kicked off from blob references, including storage account, ingestion mode, and trigger metadata for audit teams.
- **Compliance dashboard view:** Aggregates audit events and tags to validate policy adherence per tenant.

## 6. API and integration touchpoints
- New REST endpoints (see `docs/API_CONTRACTS.md`) for metadata queries:
  - `/metadata/jobs`, `/metadata/cleansing-jobs`, `/metadata/rules`, `/metadata/assets`, `/metadata/audit`, `/metadata/profiling-contexts`.
- Background workers consume metadata events for streaming to corporate SIEM or GRC systems.
- Metadata registry publishes to message bus (future) for asynchronous consumers (e.g., reporting pipelines).

## 7. Governance and compliance behaviors
- **Immutable history:** Audit, cleansing, and validation rule version entries are append-only; updates create new versions.
- **Retention enforcement:** Before deleting raw data or cleansed outputs, metadata layer verifies retention policy and logs decision.
- **PII guarding:** Sensitive tags trigger encryption and access controls; queries require elevated scope.
- **Approval workflows:** Metadata ties approvals to validation and cleansing rule entries; missing approvals block promotion.
- **Profiling transparency:** Each cleansing and validation job stores the profiling-driven context so teams can trace why thresholds shifted for a given run.
- **External source traceability:** Every externally uploaded file is linked to its blob URI, ETag, and trigger metadata so operational teams can audit the hand-off between services.
- **Evidence collection:** Scheduled exports produce compliance packs (JSON/CSV) for auditors, including cleansing metrics.

## 8. Operational requirements
- Metadata registry must be highly available and write-safe (transactional).
- All metadata changes captured in structured logs with correlation IDs.
- Backups and recovery align with overall RTO/RPO (see `NON_FUNCTIONAL_REQUIREMENTS.md`).
- Health checks include lag metrics (events waiting to be persisted).

## 9. Implementation roadmap
1. Establish `dq_metadata` module with models and registry interface.
2. Connect upload pipeline, cleansing job manager, profiling workers, and rule engine to emit metadata events and profiling context snapshots.
3. Extend admin actions to log into metadata audit stream.
4. Build metadata queries and dashboards for governance teams, including cleansing-versus-validation transparency views.
5. Integrate retention enforcement and compliance tagging.

## 10. Open questions
- Single metadata store vs. hybrid approach (PostgreSQL + data lake)?
- Need for real-time streaming (Kafka/Event Hub) vs. batch ingestion?
- How to mask sensitive metadata in multi-tenant dashboards?
- Should audit events feed directly into corporate SIEM or via intermediate service?
