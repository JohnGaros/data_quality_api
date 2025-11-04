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
| **Profiling context snapshots** | Captures the profiling-driven validation context used during each job. | Profiling context ID, profiled_at timestamp, metric overrides per logical field. |
| **Rule and config versions** | Captures change history for rules, mappings, and approvals. | Rule ID, expression hash, severity, approver, activation window. |
| **User and system actions** | Audit trail of administrator and configurator operations. | Tenant onboarding, role changes, reruns triggered, token issuance. |
| **Compliance classifiers** | Labels for sensitive data and policy obligations. | PII flag, retention tier, regulatory tags (GDPR, SOX). |

## 4. Architecture overview
- **Metadata Registry (`dq_metadata.registry.MetadataRegistry`):** Central service exposing CRUD operations for metadata objects.
- **Event stream (`dq_metadata.events`):** Standardized events emitted by API, rule engine, and admin modules.
- **Profiling context store (`dq_metadata.profiling` future):** Persists dataset profiling metrics and serves profiling-driven validation context lookups to the rule engine.
- **Storage adapters (`dq_metadata.adapters` future):** Persistence into PostgreSQL tables, Azure Log Analytics, or data lake.
- **Lineage graph (`dq_metadata.lineage`):** Builds relationships between uploads, rules, reports, and downstream exports.
- **Policy enforcement (`dq_metadata.compliance`):** Validates retention, classification, and approval policies before actions complete.

### Interaction diagram (logical)
1. Upload API (or external trigger) submits job metadata (job ID, tenant, config version, ingestion mode, blob URI/ETag when applicable) → Metadata Registry stores job entry.
2. Profiling workers emit context snapshots → Registry links profiling metrics to the job via `profiling_context_id`.
3. Rule engine emits rule outcome events plus profiling adjustments → Registry associates outcomes, context overrides, and rule versions.
4. Config manager commits new rule version → Metadata layer records version metadata, approval chain, and refreshed profiling baselines.
5. Admin actions (tenant/user changes) → Audit events stored with context (actor, timestamp, justification).
6. Observability services query metadata for dashboards, compliance reports, and SLA tracking.

## 5. Data model summary

### 5.1 Core tables / collections
- **`metadata_data_assets`**
  - `asset_id` (UUID), `tenant_id`, `dataset_type`, `schema_signature`, `classification`, `retention_policy_id`, `owner`, `created_at`, `updated_at`.
- **`metadata_jobs`**
  - `job_id`, `tenant_id`, `submission_source`, `ingestion_mode`, `blob_uri`, `blob_etag`, `config_version`, `status`, `profiling_context_id`, `profiled_at`, `profiling_adjustments` (JSONB), `input_assets` (FK array), `output_report_uri`, `checksum`, `submitted_by`, `submitted_at`, `completed_at`.
- **`metadata_rule_versions`**
  - `rule_version_id`, `rule_id`, `expression_hash`, `severity`, `change_type`, `changed_by`, `approved_by`, `approved_at`, `effective_from`, `effective_to`.
- **`metadata_audit_events`**
  - `event_id`, `actor_id`, `actor_role`, `action_type`, `resource_type`, `resource_id`, `context`, `ip_address`, `initiated_at`, `is_privileged`.
- **`metadata_compliance_tags`**
  - `tag_id`, `resource_type`, `resource_id`, `tag_key`, `tag_value`, `source`, `assigned_at`.

### 5.2 Derived views
- **Lineage view:** Combines job, rule version, and data asset tables to provide “upload → rules → report” chains.
- **Profiling performance view:** Surfaces longitudinal profiling metrics and context overrides so teams can tune default thresholds per tenant.
- **External ingestion view:** Highlights validation jobs kicked off from blob references, including storage account, ingestion mode, and trigger metadata for audit teams.
- **Compliance dashboard view:** Aggregates audit events and tags to validate policy adherence per tenant.

## 6. API and integration touchpoints
- New REST endpoints (see `docs/API_CONTRACTS.md`) for metadata queries:
  - `/metadata/jobs`, `/metadata/rules`, `/metadata/assets`, `/metadata/audit`, `/metadata/profiling-contexts`.
- Background workers consume metadata events for streaming to corporate SIEM or GRC systems.
- Metadata registry publishes to message bus (future) for asynchronous consumers (e.g., reporting pipelines).

## 7. Governance and compliance behaviors
- **Immutable history:** Audit and rule version entries append-only; updates create new versions.
- **Retention enforcement:** Before deleting raw data, metadata layer verifies retention policy and logs decision.
- **PII guarding:** Sensitive tags trigger encryption and access controls; queries require elevated scope.
- **Approval workflows:** Metadata ties approvals to rule and config entries; missing approvals block promotion.
- **Profiling transparency:** Each validation stores the profiling-driven context so teams can trace why thresholds shifted for a given job.
- **External source traceability:** Every externally uploaded file is linked to its blob URI, ETag, and trigger metadata so operational teams can audit the hand-off between services.
- **Evidence collection:** Scheduled exports produce compliance packs (JSON/CSV) for auditors.

## 8. Operational requirements
- Metadata registry must be highly available and write-safe (transactional).
- All metadata changes captured in structured logs with correlation IDs.
- Backups and recovery align with overall RTO/RPO (see `NON_FUNCTIONAL_REQUIREMENTS.md`).
- Health checks include lag metrics (events waiting to be persisted).

## 9. Implementation roadmap
1. Establish `dq_metadata` module with models and registry interface.
2. Connect upload pipeline, profiling workers, and rule engine to emit metadata events and profiling context snapshots.
3. Extend admin actions to log into metadata audit stream.
4. Build metadata queries and dashboards for governance teams, including profiling transparency views.
5. Integrate retention enforcement and compliance tagging.

## 10. Open questions
- Single metadata store vs. hybrid approach (PostgreSQL + data lake)?
- Need for real-time streaming (Kafka/Event Hub) vs. batch ingestion?
- How to mask sensitive metadata in multi-tenant dashboards?
- Should audit events feed directly into corporate SIEM or via intermediate service?
