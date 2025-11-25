# Non-Functional Requirements — Wemetrix Data Quality & Governance Platform

## 1. Why this document exists

- Sets clear quality targets beyond features.
- Helps future agents design infrastructure, tests, and SLAs correctly.
- Keeps expectations simple and visible for supervisors.

## 2. What is in scope

- Cross-cutting qualities that affect performance, security, reliability, and operability.
- Requirements that influence architecture, hosting, tooling, and support plans.

Out of scope:

- Detailed feature behavior (captured in `FUNCTIONAL_REQUIREMENTS.md`).
- Specific vendor contracts or pricing agreements.

## 3. Quality themes and requirements

> **Related documents:** For business context see `docs/BRD.md`. For architecture see `docs/ARCHITECTURE.md`. For metadata and security details see `docs/METADATA_LAYER_SPEC.md` and `docs/SECURITY_GUIDE.md`.

### 3.1 Performance and throughput

1. The platform must ensure that validation jobs for typical datasets (up to 50 MB Excel/CSV) complete within 5 minutes during normal load.
2. The platform must ensure that API endpoints respond within 2 seconds for contract/catalog metadata reads and writes under normal load.
3. The platform must handle at least 20 concurrent validation jobs and associated cleansing/profiling steps without missed SLAs.
4. The platform must queue additional jobs and expose estimated wait times when load exceeds capacity.
5. The execution engine abstraction (`dq_engine`) must allow swapping or scaling to alternate backends (e.g., Spark/SQL) for larger workloads without changing contracts or rules.

### 3.2 Scalability and elasticity

1. The platform must scale horizontally for API nodes, cleansing/profiling/validation workers, and metadata backends without code changes.
2. The deployment pipeline must allow scaling rules (manual or auto) defined per environment.
3. Storage and contract/rule/metadata repositories must support growth to at least 5 years of customer history and associated lineage/audit records.
4. Store interfaces (`dq_stores`) must allow switching or augmenting persistence (Postgres first, Blob/filesystem for large artifacts) without refactoring registries or APIs.

### 3.3 Availability and resilience

1. The production API must meet 99.5% monthly uptime once released.
2. The platform must survive the loss of a single worker or node without data loss, and must continue processing queued jobs once capacity is restored.
3. Components must restart automatically after failures, with retries logged and visible to operators.
4. Planned maintenance windows must support blue/green or rolling deployments to avoid global downtime.
5. Post-job actions (notifications, webhooks, exports) must fail gracefully without corrupting primary job metadata; failures must be logged and surfaced for remediation.

### 3.4 Security and compliance

1. All data in transit must use TLS 1.2 or higher; REST endpoints must reject plain HTTP.
2. Sensitive data at rest (uploads, reports, tokens, contract payloads, metadata exports) must be encrypted using enterprise-approved standards.
3. Access control must follow least privilege with role-based scopes and audit trails, as defined in `docs/RBAC_MODEL.md`.
4. The platform must align with corporate compliance baselines (e.g., SOC 2, GDPR) where applicable, and must support GDPR-specific tagging and policy enforcement as described in `docs/METADATA_LAYER_SPEC.md`, `docs/SECURITY_GUIDE.md`, and `governance_libraries/README.md`.
5. Secrets management must integrate with Azure Key Vault or an equivalent secure store.
6. Governance profiles from contracts (PII classification, retention, access) must propagate to storage, action execution, and metadata, ensuring tenant/environment isolation.

### 3.5 Data integrity and retention

1. Validation input files and results must be stored with checksum verification to detect corruption and to support idempotent job submission.
2. Retention schedules must be configurable per tenant; default retention targets are 180 days for raw uploads and 365 days for reports, unless overridden by tenant-specific governance/GDPR policies.
3. Archived data and metadata (including contracts, job histories, and compliance tags) must remain retrievable within 24 hours for audit purposes.

### 3.6 Observability and supportability

1. The platform must expose structured logs for each cleansing/profiling/validation job, tagged by tenant, job ID, JobDefinition ID (where applicable), and status.
2. Metrics must include job duration, success/failure counts, queue depth, API latency, and action execution success/failure, and must be queryable per tenant/environment.
3. Alerts must trigger for SLA breaches, repeated job failures, job orchestration errors, and security anomalies.
4. Support staff must have dashboards or queries to trace an upload or triggered JobDefinition from submission to report delivery and any post-job actions executed.
5. Data Docs generation (contract/job/run views) must be auditable and reproducible for evidence packs, with metadata linking outputs to source versions.

### 3.7 Maintainability and change management

1. The codebase must follow automated linting and testing gates before deployment (unit, integration, and, when available, regression tests).
2. Infrastructure must support dev, test, and prod environments with configuration-as-code (e.g., IaC in `infra/`).
3. Configuration and contract changes must be version-controlled with rollback capability through registries (`dq_contracts`, `dq_jobs`, `dq_actions`) and the Store abstraction.
4. Upgrades to rule templates, data contracts, schemas, governance/infra profiles, execution engines, or action types must be backwards compatible or explicitly flagged for migration steps and documented in lifecycle metadata.

### 3.8 Disaster recovery and business continuity

1. Backups of configurations, contracts, rules, governance/infra profiles, JobDefinitions, ActionProfiles, and reports must run at least daily and be stored in a separate region.
2. Recovery Time Objective (RTO) is 4 hours; Recovery Point Objective (RPO) is 1 hour for critical data and metadata.
3. DR procedures must be documented and tested at least once per year.

### 3.9 Integration readiness

1. APIs must respect rate limits and provide clear error responses to prevent partner retries from overloading the system.
2. Webhooks or notification endpoints (including those triggered via ActionProfiles) must include retry policies with exponential backoff.
3. External integrations (Azure Blob, Power Platform, notifications, webhooks, external orchestrators) must fail gracefully without blocking core cleansing/profiling/validation flows.
4. Execution engines and stores must be replaceable or extendable without impacting API contracts or contract definitions, enabling future cloud service choices.

## 4. Acceptance checkpoints

- Monitoring dashboards and alerting rules exist for each SLA above, including job latency, concurrency, queue depth, and action execution metrics.
- Load tests demonstrate performance and scalability targets before production launch, with representative tenant and dataset mixes.
- Security reviews confirm encryption, access controls, logging, and GDPR tagging behaviors meet policy and regulatory expectations.
- Disaster recovery playbooks are executed in a non-production drill and verify RTO/RPO targets for contracts, jobs, metadata, and reports.

## 5. Open questions to resolve later

- Final target numbers for high-volume customers (peak workload sizing).
- Specific compliance audits required in each region (e.g., additional GDPR supervisory authority expectations).
- Ownership model for 24/7 support and on-call rotations.
- Whether retention defaults vary by customer tier and regulatory profile.
