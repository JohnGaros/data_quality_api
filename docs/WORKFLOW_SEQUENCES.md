# End-to-End Workflow Sequences

## 1. Purpose
- Show how the major parts of the Data Quality Assessment API work together.
- Provide non-technical stakeholders with clear narratives of critical flows.
- Link to the Mermaid diagrams that visualise each sequence.

Diagrams are stored under `docs/diagrams/` to keep visuals organised.

## 2. Upload, validate, and report
1. **Uploader** submits files via API or UI; metadata layer records submission.
2. **Job manager** stores the files, queues a validation job, assigns configuration version, and triggers dataset profiling.
3. **Profiling workers** produce a snapshot of field statistics that becomes the profiling-driven validation context seed.
4. **Rule engine** pulls configuration plus the profiling-driven validation context, runs rules, and streams results to report builder.
5. **Report service** saves summary and detailed outputs; metadata updated with lineage and profiling adjustments.
6. **Notifications** inform Uploader of completion; user fetches report if needed.

See `docs/diagrams/upload_validation_flow.mmd` for the flow diagram.

## 3. Decoupled upload hand-off (future scenario)
1. **External upload service** writes files to Azure Blob Storage and records metadata (tenant, dataset type, checksum).
2. **Trigger mechanism (event/webhook/polling — decision pending)** notifies the Data Quality Assessment API with a blob reference and integrity metadata.
3. **External uploads endpoint** in the DQ API validates the reference, queues a validation job, and captures ingestion mode details.
4. **Rule engine** pulls the blob via Azure adapters, assembles the profiling-driven validation context, and runs validations as usual.
5. **Metadata registry** stores lineage linking the blob URI, trigger type, profiling context, and resulting reports.
6. **Notifications** inform stakeholders using the same channels as direct uploads; retry policies depend on the chosen trigger.

Diagram: `docs/diagrams/external_upload_trigger.mmd`.

## 4. Configuration promotion lifecycle
1. **Configurator** edits rule templates and uploads draft configuration.
2. **Validation** step checks for schema errors, runs sandbox tests, and refreshes the profiling baseline used to build profiling-driven validation contexts.
3. **Configurator** submits change for approval; metadata logs pending status.
4. **Admin** reviews, approves, and promotes configuration to production tenants.
5. **Metadata** records rule version, approval chain, effective dates, and the profiling baselines linked to each configuration.
6. **Uplinks** notify relevant users of configuration activation.

Diagram: `docs/diagrams/config_promotion_flow.mmd`.

## 5. Audit and compliance reporting
1. **Admin** or auditor requests compliance evidence package.
2. **Metadata registry** gathers lineage, audit events, and configuration history.
3. **Export service** generates files (JSON/CSV/PDF) and stores them securely.
4. **Notification** shares download link with authorised roles.
5. **Audit trail** logs who accessed the evidence and when.

Diagram: `docs/diagrams/compliance_reporting_flow.mmd`.

## 6. Future enhancements
- Add workflows for integration triggers (Power Platform, webhooks) once designed.
- Include incident response flow after the security runbook is complete.
- Update diagrams as stakeholder decisions (approvals, retention tiers) are finalised.
