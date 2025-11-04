# Functional Requirements — Data Quality Assessment API

## 1. Why this document exists
- Gives us a shared checklist of what the system must do.
- Uses plain language so non-engineers and future agents can read it fast.
- Links each requirement to the user roles described in the project brief.

## 2. What is in scope
- Features that let people upload data, validate it, review results, and manage rules.
- Configuration, administration, and auditing tasks that keep the platform running.
- Everything needed for day-one operations of the API and the supporting UI or scripts.

Out of scope for now:
- Custom analytics dashboards, advanced rule DSL editors, and automated workflow integrations (captured later in integration specs).

## 3. Key user roles (recap)
- **Uploader:** Sends files and needs quick yes/no plus error details.
- **Configurator:** Designs and maintains rules and field mappings.
- **Admin:** Oversees tenants, users, security, and operational health.

## 4. Functional areas and requirements

### 4.1 File intake and validation (Uploader focus)
1. System must accept Excel and CSV uploads via REST API and future UI, whether provided as direct file payloads or as immutable blob references supplied after an external upload completes.
2. Uploader must see immediate confirmation that the file (or external reference) was received and queued.
3. System must link each upload to the correct customer tenant and configuration version, regardless of the ingestion path.
4. Validation engine must build a profiling-driven validation context using the upload's profiling snapshot, then run all active rules inside that context.
5. System must store the original file securely for later review or reruns.
6. Uploader must be able to poll or receive status updates (pending, running, completed, failed).
7. When validation finishes, system must provide pass/fail outcome plus summary counts of issues and call out any profiling-driven threshold adjustments that influenced results.
8. Uploader must be able to download a detailed error report highlighting failed rows and rules.

*Profiling-driven example:* If profiling shows a tenant's historical null rate for `PaymentAmount` stays below 2%, the profiling-driven validation context tightens the warning threshold to 3% for the next run so sudden spikes surface as soft alerts before hard failures occur. The same profiling logic applies whether the dataset arrived through direct upload or via an external blob reference.
### 4.2 Rule and configuration management (Configurator focus)
9. Configurator must be able to view the active rule library, including rule name, category, severity, and status.
10. Configurator must upload or edit rule definitions using structured templates (Excel/JSON) through API endpoints.
11. System must validate new configurations before activation (missing fields, duplicate IDs, invalid expressions).
12. Configurator must manage logical fields and map them to customer-specific columns or calculated formulas.
13. System must track versions of rules, logical fields, and mappings with timestamps and authorship.
14. Configurator must test new configurations in a sandbox tenant before requesting promotion.
15. System must support soft rules (warnings) and hard rules (blocking) with clear labels in results.
16. Configurator must request approval for production promotion; system logs approval decisions.

### 4.3 Administration and tenant operations (Admin focus)
17. Admin must create, update, suspend, or delete customer tenants.
18. System must support multi-tenant isolation for data, rules, and logs.
19. Admin must manage user accounts, roles, and API tokens with expiration dates.
20. System must expose metrics on validation throughput, success rates, and queue health.
21. Admin must configure storage retention policies for uploads, reports, and audit logs.
22. System must provide audit trails of key actions (uploads, rule changes, approvals, admin actions).
23. Admin must trigger revalidation of prior uploads when configurations change, with traceable links.
24. System must integrate with enterprise authentication (e.g., Azure AD) for SSO where available.

### 4.4 Reporting and downstream access (All roles)
25. System must allow users to fetch validation reports via API filtered by date, tenant, or status.
26. Reports must include per-rule statistics, affected records, and total counts.
27. System must offer export formats (JSON, CSV) for downstream tools.
28. System must notify relevant users (email/webhook) when critical validations fail, with opt-in control.

### 4.5 Platform-wide requirements
29. Every requirement above must be accessible through documented REST endpoints.
30. Operations must be scriptable for automation (CLI or service accounts).
31. System must guard against duplicate uploads by using idempotent job identifiers.
32. System must handle batch uploads, processing each file separately but under a single job reference.
33. System must log and surface validation errors when rule execution fails (e.g., malformed expressions).
34. Metadata layer must capture lineage for every validation job, including source assets, rule versions, and generated reports.
35. Metadata endpoints must allow authorized users to query audit trails, compliance tags, and evidence packs on demand.

## 5. Acceptance checkpoints
- We can demonstrate a sample tenant setup, rule load, and file validation end-to-end.
- Each role has at least one happy path and one exception path covered by automated tests.
- Documentation and API references reflect all required endpoints and parameters.

## 6. Open questions to resolve later
- Exact SLA targets for validation turnaround times.
- Whether upload notifications are synchronous (webhook) or asynchronous (email queue).
- How fine-grained the approval workflow needs to be (single approver vs. multi-step).
- Retention timelines for historical reports vs. raw uploads.
