# End-to-End Workflow Sequences

## 1. Purpose
- Show how the major parts of the Data Quality Assessment API work together.
- Provide non-technical stakeholders with clear narratives of critical flows.
- Link to the Mermaid diagrams that visualise each sequence.

Diagrams are stored under `docs/diagrams/` to keep visuals organised.

## 2. Upload, validate, and report
1. **Uploader** submits files via API or UI; metadata layer records submission.
2. **Job manager** stores the files, queues a validation job, and assigns configuration version.
3. **Rule engine** pulls configuration, runs rules, and streams results to report builder.
4. **Report service** saves summary and detailed outputs; metadata updated with lineage.
5. **Notifications** inform Uploader of completion; user fetches report if needed.

See `docs/diagrams/upload_validation_flow.mmd` for the flow diagram.

## 3. Configuration promotion lifecycle
1. **Configurator** edits rule templates and uploads draft configuration.
2. **Validation** step checks for schema errors and runs sandbox tests.
3. **Configurator** submits change for approval; metadata logs pending status.
4. **Admin** reviews, approves, and promotes configuration to production tenants.
5. **Metadata** records rule version, approval chain, and effective dates.
6. **Uplinks** notify relevant users of configuration activation.

Diagram: `docs/diagrams/config_promotion_flow.mmd`.

## 4. Audit and compliance reporting
1. **Admin** or auditor requests compliance evidence package.
2. **Metadata registry** gathers lineage, audit events, and configuration history.
3. **Export service** generates files (JSON/CSV/PDF) and stores them securely.
4. **Notification** shares download link with authorised roles.
5. **Audit trail** logs who accessed the evidence and when.

Diagram: `docs/diagrams/compliance_reporting_flow.mmd`.

## 5. Future enhancements
- Add workflows for integration triggers (Power Platform, webhooks) once designed.
- Include incident response flow after the security runbook is complete.
- Update diagrams as stakeholder decisions (approvals, retention tiers) are finalised.
