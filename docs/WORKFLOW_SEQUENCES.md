# End-to-End Workflow Sequences

## 1. Purpose
- Show how the major parts of the Data Quality Assessment API work together.
- Provide non-technical stakeholders with clear narratives of critical flows.
- Link to the Mermaid diagrams that visualise each sequence.

Diagrams are stored under `docs/diagrams/` to keep visuals organised.

## 2. Cleansing job lifecycle
1. **Configurator or scheduler** submits a cleansing job through the API, specifying tenant, dataset type, and cleansing rule version; metadata layer records the request.
2. **Cleansing job manager** resolves the source dataset (raw upload or latest approved dataset) and builds an ordered transformation plan.
3. **Cleansing engine** executes each transformation step (standardise, deduplicate, enrich), logging before/after metrics and rejected records.
4. **Output writer** stores the cleansed dataset and staged rejection set; metadata links storage locations and transformation metrics to the job.
5. **Metadata registry** publishes lineage, audit events, and readiness indicators so downstream services can observe SLA health.
6. **Notifications service** informs stakeholders of completion or failure; reports include cleansing metrics and download links where applicable.

**Triggers:** Manual API requests, scheduler-based reruns (e.g., nightly refresh), or automatic chaining from an upload event that is flagged as “cleansing required.” Each trigger supplies the job reason so auditors can distinguish proactive reruns from reactive remediation.

**Inputs:** Tenant context, dataset classification, cleansing rule version, optional profiling hints, and storage pointers to the source dataset. Optional overrides include transformation allowlists/denylists and thresholds for duplicate/conflict detection.

**Outputs:** Cleaned dataset URI, rejection dataset URI, transformation metrics (records touched, duplicates removed, nulls imputed), and metadata describing the applied cleansing rule version plus execution timings. Outputs are versioned so validation jobs can pin the exact cleansing state.

**Error handling:** Failures (e.g., schema mismatch, transformation defect, storage outage) are bubbled to the job manager, which marks the job failed, records the stack trace and offending transformation, retries idempotent stages when safe, and emits notifications. Partial outputs are tagged as unusable to prevent downstream profiling from reading incomplete cleansed data.

Diagram: `docs/diagrams/cleansing_job_flow.mmd`.

## 3. Chained cleansing → validation sequence
1. **Uploader** submits files via API or UI; metadata layer records the submission and indicates that cleansing is required for the dataset type.
2. **Cleansing job manager** launches the cleansing job, monitors completion, and, on success, pins the cleansed dataset URI plus applied rule version.
3. **Job manager** instantiates the validation job using the cleansed dataset as input, carrying over tenant context, profiling preferences, and job linkage IDs.
4. **Validation engine** builds or reuses the profiling-driven validation context, runs rules against the cleansed dataset, and streams results to the report builder.
5. **Reporting layer** merges cleansing and validation outputs so users see a unified view (records cleansed, rules failed, overall status).
6. **Metadata registry** finalises lineage entries showing raw upload → cleansing job → validation job, enabling reruns or targeted investigations.
7. **Notifications** emit aggregated updates with references to both job IDs for traceability.

Diagram: `docs/diagrams/cleansing_validation_chain.mmd`.

### dq_profiling module role
- `dq_profiling/engine/profiler.py` runs immediately after cleansing (or raw ingestion when cleansing is disabled) to build profiling snapshots tied to each job ID.
- `dq_profiling/engine/context_builder.py` converts those snapshots plus any overrides into the profiling-driven validation context consumed by `dq_core.engine.RuleEngine`.
- `dq_profiling/models/` emits structured job/result payloads so the metadata layer can link profiling context IDs with both cleansing and validation jobs.
- Future REST handlers in `dq_profiling/api/` will expose submission/status endpoints should profiling need to be invoked independently from validation.

## 4. Upload, validate, and report
1. **Uploader** submits files via API or UI; metadata layer records submission.
2. **Job manager** stores the files, queues a validation job, assigns configuration version, and triggers dataset profiling.
3. **Profiling workers** produce a snapshot of field statistics that becomes the profiling-driven validation context seed.
4. **Rule engine** pulls configuration plus the profiling-driven validation context, runs rules, and streams results to report builder.
5. **Report service** saves summary and detailed outputs; metadata updated with lineage and profiling adjustments.
6. **Notifications** inform Uploader of completion; user fetches report if needed.

See `docs/diagrams/upload_validation_flow.mmd` for the flow diagram.

## 5. Decoupled upload hand-off (future scenario)
1. **External upload service** writes files to Azure Blob Storage and records metadata (tenant, dataset type, checksum).
2. **Trigger mechanism (event/webhook/polling — decision pending)** notifies the Data Quality Assessment API with a blob reference and integrity metadata.
3. **External uploads endpoint** in the DQ API validates the reference, queues a validation job, and captures ingestion mode details.
4. **Rule engine** pulls the blob via Azure adapters, assembles the profiling-driven validation context, and runs validations as usual.
5. **Metadata registry** stores lineage linking the blob URI, trigger type, profiling context, and resulting reports.
6. **Notifications** inform stakeholders using the same channels as direct uploads; retry policies depend on the chosen trigger.

Diagram: `docs/diagrams/external_upload_trigger.mmd`.

## 6. Configuration promotion lifecycle
1. **Configurator** edits rule templates and uploads draft configuration.
2. **Validation** step checks for schema errors, runs sandbox tests, and refreshes the profiling baseline used to build profiling-driven validation contexts.
3. **Configurator** submits change for approval; metadata logs pending status.
4. **Admin** reviews, approves, and promotes configuration to production tenants.
5. **Metadata** records rule version, approval chain, effective dates, and the profiling baselines linked to each configuration.
6. **Uplinks** notify relevant users of configuration activation.

Diagram: `docs/diagrams/config_promotion_flow.mmd`.

## 7. Audit and compliance reporting
1. **Admin** or auditor requests compliance evidence package.
2. **Metadata registry** gathers lineage, audit events, and configuration history.
3. **Export service** generates files (JSON/CSV/PDF) and stores them securely.
4. **Notification** shares download link with authorised roles.
5. **Audit trail** logs who accessed the evidence and when.

Diagram: `docs/diagrams/compliance_reporting_flow.mmd`.

## 8. Future enhancements
- Add workflows for integration triggers (Power Platform, webhooks) once designed.
- Include incident response flow after the security runbook is complete.
- Update diagrams as stakeholder decisions (approvals, retention tiers) are finalised.
