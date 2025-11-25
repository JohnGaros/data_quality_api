# Functional Requirements — Wemetrix Data Quality & Governance Platform

## 1. Why this document exists

- Gives us a shared checklist of what the system must do.
- Uses plain language so non-engineers and future agents can read it fast.
- Links each requirement to the user roles described in the project brief.

> **Related documents:** For business context see `docs/BRD.md`. For architecture and module structure see `docs/ARCHITECTURE.md` and `docs/ARCHITECTURE_FILE_STRUCTURE.md`. For contract-driven rationale see `docs/CONTRACT_DRIVEN_ARCHITECTURE.md`. For actions and job orchestration see `docs/ACTIONS_AND_JOB_DEFINITIONS.md`.

## 2. What is in scope

- Features that let people upload data, validate it, review results, and manage rules.
- Contract and catalogue operations that keep the platform’s ground truth (DataContracts, catalogue mappings, profiles) current.
- Configuration, administration, and auditing tasks that keep the platform running in a multi-tenant, GDPR-aware environment.
- Everything needed for day-one operations of the API and the supporting UI or scripts.

Out of scope for now:

- Custom analytics dashboards, advanced rule DSL editors, and automated workflow integrations (captured later in integration specs).

## 3. Key user roles (recap)

- **Uploader:** Sends files and needs quick yes/no plus error details.
- **Configurator:** Designs and maintains rules and field mappings.
- **Admin:** Oversees tenants, users, security, and operational health.

## 4. Functional areas and requirements

### 4.1 File intake and validation (Uploader focus)

1. The platform must accept Excel and CSV uploads via REST API and future UI, whether provided as direct file payloads or as immutable blob references supplied after an external upload completes (`/uploads`, `/jobs/run/{job_definition_id}`; see `docs/API_CONTRACTS.md`), supporting both direct and decoupled orchestrator-driven ingestion.
2. The Uploader must see immediate confirmation that the file (or external reference) was received and queued.
3. The platform must link each upload or triggered job to the correct customer tenant, environment, and DataContract/JobDefinition, regardless of the ingestion path.
4. The validation engine must build a profiling-driven validation context using the upload's profiling snapshot, then run all active rules inside that context.
5. The platform must store original files or immutable references securely for later review, reruns, or audit (with retention policies enforced per tenant).
6. The Uploader must be able to poll or receive status updates (pending, running, completed, failed) for their jobs.
7. When validation finishes, the platform must provide pass/fail outcome plus summary counts of issues and call out any profiling-driven threshold adjustments that influenced results.
8. The Uploader must be able to download a detailed error report highlighting failed rows and rules, scoped by tenant and dataset/contract.

_Profiling-driven example:_ If profiling shows a tenant's historical null rate for `PaymentAmount` stays below 2%, the profiling-driven validation context tightens the warning threshold to 3% for the next run so sudden spikes surface as soft alerts before hard failures occur. The same profiling logic applies whether the dataset arrived through direct upload or via an external blob reference.

#### dq_profiling module scope

- `dq_profiling/models/` defines profiling job payloads, job status enums, and profiling snapshots so API endpoints and metadata events stay consistent.
- `dq_profiling/engine/profiler.py` turns cleansed datasets into profiling snapshots, computing per-field statistics (count, distinct count, null count), descriptive metrics (min, max, mean, standard deviation), top-N frequent values, and distribution summaries (numeric histograms or categorical value counts). `context_builder.py` converts those snapshots plus overrides into validation-ready contexts.
- `dq_profiling/api/` reserves routing hooks for independent profiling requests (e.g., proactive profiling without full validation).
- `dq_profiling/report/` packages profiling job results into human-readable summaries or CSV exports so Uploaders, Configurators, and auditors can inspect profiling signals—including the new statistics, frequent values, and distributions—without parsing raw datasets.
- `dq_core` components consume the profiling contexts exclusively through the dq_profiling interfaces to enforce separation of concerns.

### 4.2 Data cleansing orchestration (Uploader & Configurator focus)

1. The platform must automatically cleanse incoming data before profiling and validation when policies require it, while letting tenants enable/disable specific cleansing pipelines per dataset type (driven by contracts and JobDefinitions).
2. Cleansing rules must be stored in the rule authoring layer (`rule_libraries/cleansing_rules`) with their own versioning, activation status, and approval workflow.
3. The Configurator must import or edit cleansing rule templates (Excel/JSON/YAML) through API endpoints parallel to validation rule management.
4. Cleansing jobs must support queueing, retry, and status polling semantics equivalent to validation jobs for Uploader visibility.
5. When chaining is enabled, the job manager must automatically trigger validation using the cleansed dataset and link the resulting job IDs in metadata.
6. The platform must persist cleansing outputs (transformed datasets, rejected records, execution metrics) so reports, evidence packs, and downstream exports can access them.
7. The Configurator must run sandbox cleansing tests against sample datasets without impacting production tenants.
8. Metadata and audit logs must capture cleansing job lineage, applied rule versions, and before/after metrics for SLA tracking (see `docs/METADATA_LAYER_SPEC.md`).

### 4.3 Rule, contract, and configuration management (Configurator focus)

1. The Configurator must be able to view the active rule library across validation, profiling, and cleansing families (sourced from `rule_libraries/`), including rule name, category, severity, and status.
2. The Configurator must upload or edit rule definitions using structured templates (Excel/JSON/YAML) through API endpoints and persist them as contract-aware rule templates in the registry layer (`src/dq_contracts`).
3. The platform must validate new configurations or contract changes before activation (missing fields, duplicate IDs, invalid expressions or bindings).
4. The Configurator must manage logical fields and dataset schemas via DataContracts, mapping them to customer-specific columns or calculated formulas, while referencing canonical schemas from `schema_libraries/` and entities/attributes from `dq_catalog`.
5. The platform must track versions of rules, logical fields, mappings, profiles, and DataContracts with timestamps and authorship, and expose that history via metadata and audit endpoints.
6. The Configurator must test new configurations or contract revisions in a sandbox tenant/environment before requesting promotion.
7. The platform must support soft rules (warnings) and hard rules (blocking) with clear labels in results.
8. The Configurator must request approval for production promotion; the platform must log approval decisions and tie them to contract lifecycle metadata and governance policies.

### 4.4 Administration and tenant operations (Admin focus)

1. The Admin must create, update, suspend, or delete customer tenants.
2. The platform must support multi-tenant isolation for data, rules, logs, and metadata.
3. The Admin must manage user accounts, roles, and API tokens with expiration dates.
4. The platform must expose metrics on validation throughput, cleansing throughput, success rates, and queue health.
5. The Admin must configure storage retention policies for uploads, cleansed outputs, reports, and audit logs, consistent with governance profiles and GDPR requirements.
6. The platform must provide audit trails of key actions (uploads, cleansing runs, rule changes, approvals, admin actions) via `dq_metadata` and `dq_security` components.
7. The Admin must be able to trigger revalidation of prior uploads when configurations or contracts change, with traceable links in metadata.
8. The platform must integrate with enterprise authentication (e.g., Azure AD) for SSO where available.

### 4.5 Reporting and downstream access (All roles)

1. The platform must allow users to fetch validation, cleansing, and profiling reports via API filtered by date, tenant, status, dataset/contract, and job definition where relevant.
2. Reports must include per-rule statistics, affected records, and total counts for both cleansing and validation phases, and must indicate which catalogue attributes and governance profiles were in force.
3. The platform must offer export formats (JSON, CSV) for downstream tools and evidence packs.
4. The platform must notify relevant users (via configured ActionProfiles: email/webhook/Teams/Slack) when critical cleansing or validation failures occur, with opt-in control at tenant/JobDefinition level.
5. The platform must generate Data Docs (HTML/markdown) for contracts, JobDefinitions, and specific runs, scoped by tenant/environment, to support audits and onboarding (see `docs/DATA_DOCS_STRATEGY.md`).

### 4.6 Job orchestration, actions, and SDK (Configurator & Admin focus)

1. The platform must support JobDefinitions/Checkpoints that reference DataContracts (and optional DatasetContracts) plus ActionProfiles, scoped per tenant/environment, with triggers via API, external orchestrator calls, or scheduled workflows.
2. ActionProfiles from the Action Library must be reusable across JobDefinitions and allow different behaviours per environment (e.g., DEV vs PROD notifications/webhooks/tickets).
3. A runtime SDK/context façade (`DQContext`) must expose programmatic methods to run contract-driven validations, execute JobDefinitions, and retrieve metadata/reports for notebooks, CLI tools, and orchestrator adapters.
4. Job and action lifecycle changes (creation, promotion, retirement) must be captured in metadata and respect approvals/promotion policies.

### 4.7 Platform-wide requirements

1. Every requirement above must be accessible through documented REST endpoints, CLI tooling, or workflows as described in `docs/API_CONTRACTS.md`.
2. Operations must be scriptable for automation (CLI or service accounts), including contract registration, rule/library sync, JobDefinition management, ActionProfile management, and Data Docs generation.
3. The platform must guard against duplicate uploads or job submissions by using idempotent job identifiers and checksums.
4. The platform must handle batch uploads, processing each file separately but under a single job or correlation reference.
5. The platform must log and surface cleansing and validation errors when rule execution fails (e.g., malformed expressions) and must provide actionable diagnostics for Configurators and Admins.
6. The metadata layer must capture lineage for every cleansing and validation job, including source assets, rule versions, governance/infra profiles, JobDefinitions, ActionProfiles, and generated reports.
7. Metadata endpoints must allow authorized users to query audit trails, compliance tags (including GDPR fields), and evidence packs on demand.
8. Registries for contracts, jobs, actions, and metadata must rely on pluggable Store interfaces (Postgres today; Blob/filesystem later) so persistence backends can evolve without changing business logic (see `docs/STORES_AND_PERSISTENCE.md`).
9. Cleansing, profiling, and validation must use an execution engine abstraction (`dq_engine`) so multiple backends (Pandas now; Spark/SQL later) can be introduced via contract/infra profile hints without rewriting contracts or rules.

## 5. Acceptance checkpoints

- We can demonstrate a sample tenant setup, contract registration (including catalogue mappings and governance/infra profiles), rule load from `rule_libraries/`, and file validation end-to-end.
- We can demonstrate at least one end-to-end JobDefinition run that uses an ActionProfile to send notifications and record action outcomes in metadata.
- Each role has at least one happy path and one exception path covered by automated tests (Uploader, Configurator, Admin, Governance/Audit).
- Documentation and API references reflect all required endpoints and parameters, including contract, catalogue, JobDefinition, and ActionProfile operations.

## 6. Open questions to resolve later

- Exact SLA targets for validation turnaround times.
- Whether upload notifications are synchronous (webhook) or asynchronous (email queue).
- How fine-grained the approval workflow needs to be (single approver vs. multi-step).
- Retention timelines for historical reports vs. raw uploads and how they align with per-tenant governance/GDPR requirements.
- Precise boundaries between external orchestrators and platform job managers for scheduling and triggering JobDefinitions.
