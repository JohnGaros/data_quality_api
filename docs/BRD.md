# Business Requirements Document — Wemetrix Data Quality & Governance Platform

## 1. Executive summary

- Build an enterprise-ready, multi-tenant platform that uses explicit data contracts and a semantic data catalogue to cleanse and validate customer datasets against centralized business rules.
- Provide consistent, auditable data-quality and governance outcomes across multiple tenants with minimal manual oversight.
- Enable data/contract/catalog stewards and admins to manage rule libraries, contracts, mappings, and governance metadata without developer intervention.

## 2. Business objectives

1. Standardize how customer data cleansing, quality validation, and governance are measured and reported using contract-driven, catalog-backed definitions.
2. Reduce turnaround time for onboarding new customers or schema changes by reusing contract templates, rule libraries, and catalog mappings instead of one-off configurations.
3. Deliver transparent audit trails and compliance evidence for regulators and internal governance teams.
4. Support future workflow automation and analytics integrations without major rework by exposing contracts, catalog, and metadata through stable APIs.
5. Provide governed rule libraries and cleansing frameworks that can evolve independently from individual feeds, tenants, or infrastructure profiles.

## 3. Scope

### 3.1 In scope

- REST API for file uploads, cleansing jobs, validation jobs, reporting, contract and catalog management, and metadata access.
- Reusable JobDefinitions/Checkpoints that reference DataContracts and ActionProfiles for tenant- and environment-scoped execution plans.
- Action Library for reusable post-job behaviours (notifications, webhooks, lineage, exports) authored in `action_libraries/` and resolved via `src/dq_actions`.
- Runtime SDK/context façade (`src/dq_sdk`) for notebooks, CLI tools, and orchestrator adapters to run contract-driven jobs.
- Admin tooling for tenant management, RBAC, approvals, and retention settings.
- Contract registry and semantic catalogue integration that capture how producer-specific feeds map into canonical entities/attributes.
- Metadata layer that captures lineage, audit events, and compliance tags.
- Data Docs exports (HTML/markdown) summarising contracts, JobDefinitions, and job runs for auditors and onboarding teams.
- Documentation, test scaffolding, and deployment assets needed for launch.

### 3.2 Out of scope (initial release)

- Advanced rule DSL editing experience (future enhancement).
- Real-time dashboards or BI visualizations beyond exportable reports.
- Fully automated integrations with third-party workflow systems (to be defined later).

### 3.3 Pending decisions

- **Upload orchestration pattern:** Whether external uploads are triggered via Event Grid, direct webhooks, or polling remains under evaluation. `docs/ARCHITECTURE.md` (sections 3 and 9) and `configs/external_upload.example.yaml` capture the current options and placeholders (`dq_api/routes/external_uploads.py`, `dq_api/services/external_trigger_service.py`).
- **Initial ActionProfile catalogue:** The first set of supported action types (notifications, lineage events, webhooks, ticketing, storage exports) will be finalised during MVP design. See `docs/ACTIONS_AND_JOB_DEFINITIONS.md` for the target model.
- **JobDefinition scheduling boundaries:** Final responsibility split between external orchestrators (e.g., Airflow/ADF) and the platform’s `/jobs/run/{job_definition_id}` API is documented in `docs/ARCHITECTURE.md` and will be confirmed before production rollout.

## 4. Stakeholders and roles

| Group              | Representative roles                     | Primary interests                                 |
| ------------------ | ---------------------------------------- | ------------------------------------------------- |
| Business owners    | Data governance lead, compliance manager | Ensure policy adherence and audit readiness.      |
| Product leadership | Platform supervisor, project sponsor     | Delivery milestones, feature completeness, ROI.   |
| Operations         | System administrators                    | Stable operations, tenant onboarding, monitoring. |
| Configuration team | Data stewards, configurators             | Flexible rule management, sandbox testing.        |
| End users          | Data submitters, external partners       | Clear validation feedback, fast turnaround.       |

## 5. Core data quality & governance requirements

The Wemetrix platform treats **data contracts** and a **semantic data catalogue** as the ground truth for how each producer feed participates in the overall data model. Cleansing, profiling, validation, infra, and governance flows are all driven from these contracts instead of one-off configurations.

### 5.1 Contract and catalogue centricity

1. **Contract for every feed:** The platform must ensure that every onboarded dataset has a registered `DataContract` that:
   - References reusable rule sets, schemas, infra profiles, and governance profiles from the authoring libraries (`rule_libraries/`, `schema_libraries/`, `infra_libraries/`, `governance_libraries/`).
   - Maps producer-specific columns and files into canonical catalogue entities/attributes (e.g., `Customer.email`, `Transaction.amount`) managed by `src/dq_catalog`.
2. **Versioned, promotable contracts:** The platform must version all DataContracts and support promotion across environments (dev/test/prod), with lifecycle metadata (status, owners, approvals, promotions) captured for audit, as outlined in `docs/ARCHITECTURE.md` and `docs/CONTRACT_DRIVEN_ARCHITECTURE.md`.
3. **Catalogue as semantic source of truth:** The platform must treat the semantic catalogue (`src/dq_catalog`) as the single reference for business meaning so that rules and governance policies authored against catalogue attributes/entities can be reused across tenants and feeds.

### 5.2 Data cleansing requirements

4. **Mandatory pre-validation cleansing (when required):** The platform must cleanse incoming datasets (duplicate removal, format standardisation, missing-value handling, perimeter restriction) whenever tenant or dataset policies require it so profiling and validation run against trusted inputs, as described in the cleansing flows in `docs/ARCHITECTURE.md`.
5. **Policy-driven orchestration:** The platform must allow business owners to define cleansing triggers per dataset type (e.g., “always cleanse credit applications,” “only cleanse when null-rate exceeds threshold”) without redeploying code, using contract and library references rather than hard-coded flags.
6. **Audit-grade transparency:** The platform must produce cleansing job metrics that show what changed (records cleansed, rejects, transformation deltas) and link them to the originating upload and contract so auditors can trace corrective actions end-to-end.
7. **Business continuity:** The platform must halt downstream processing when cleansing fails, notify stakeholders with actionable diagnostics, and support resumable reruns so poor-quality data never reaches profiling/validation unnoticed.

### 5.3 Validation, profiling, and reporting

8. **Contract-backed execution:** The platform must execute validation and profiling jobs against the materialised contract bundle (schema + rules + catalogue mappings + infra/gov profiles) resolved by the registry at runtime, not against ad-hoc configuration files.
9. **Reusable rule libraries:** The platform must make rule libraries for validation, profiling, and cleansing reusable across tenants and contracts, with severity, thresholds, and activation windows managed via bindings and profiles rather than duplicated per feed.
10. **Contract-aware reporting:** The platform must expose clear, contract-aware reports and APIs (per job, per tenant, per dataset/contract) that show which rules fired, which catalogue attributes were affected, and how cleansing/profiling influenced outcomes, as reflected in `docs/reference/DQ_RULES.md` and `docs/reference/METADATA_PILLARS.md`.

### 5.4 Governance, metadata, and automation

11. **Governance profiles enforced everywhere:** The platform must reference governance profiles (PII classifications, retention, access policies) from contracts and enforce them consistently across cleansing, validation, storage, and access flows.
12. **End-to-end lineage:** The platform must capture end-to-end lineage in `src/dq_metadata` (see `docs/METADATA_LAYER_SPEC.md`): uploads, contracts, catalogue mappings, cleansing jobs, profiling snapshots, validation jobs, rule versions, infra/governance profiles, job definitions, action profiles, and user actions.
13. **Automation-friendly workflows:** The platform must support automation-friendly workflows (idempotent uploads, scriptable APIs, reruns) so contracts, catalogue entries, rule libraries, JobDefinitions, ActionProfiles, and Data Docs can be managed through CI/CD and self-service tools rather than manual operations. The runtime SDK (`DQContext`) should provide a programmatic entrypoint for scripts and orchestrators.

## 6. Glossary

| Term                   | Definition                                                                                                                                                                                                                                 |
| ---------------------- | ------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------ |
| **DataContract**       | Canonical, versioned description of how a producer feed participates in the platform, including dataset schemas, rule bindings, infra and governance profile references, and catalogue mappings. Modelled in `src/dq_contracts/models.py`. |
| **DatasetContract**    | Dataset-level portion of a DataContract that defines columns, types, constraints, and relationships for a specific dataset.                                                                                                                |
| **Catalogue**          | Semantic layer (`src/dq_catalog`) that defines canonical entities (Customer, Account, Transaction) and attributes (`Customer.email`, `Transaction.amount`) used to align producer schemas and reusable rules/governance.                   |
| **Cleansing**          | Policy-driven transformations that normalise, enrich, or quarantine data before profiling/validation (`src/dq_cleansing`).                                                                                                                 |
| **Profiling**          | Computation of statistics and distributions over datasets (null rates, histograms, distinct counts, etc.) to drive adaptive rules and monitoring (`src/dq_profiling`).                                                                     |
| **Validation**         | Evaluation of rules against datasets within a profiling-driven context, implemented by the rule engine in `src/dq_core`.                                                                                                                   |
| **Rule Library**       | Authoring source for validation, cleansing, and profiling rules stored under `rule_libraries/` and normalised into canonical JSON.                                                                                                         |
| **Infra Profile**      | Declarative description of storage/compute/retention expectations for a dataset (`infra_libraries/`).                                                                                                                                      |
| **Governance Profile** | Policy bundle describing PII/GDPR classification, lawful basis, retention, and access rules for datasets and attributes (`governance_libraries/`).                                                                                         |
| **ActionProfile**      | Reusable bundle of post-job behaviours (notifications, lineage events, webhooks, tickets) authored in `action_libraries/` and resolved at runtime via `src/dq_actions` (see `docs/ACTIONS_AND_JOB_DEFINITIONS.md`).                        |
| **JobDefinition**      | Tenant-scoped execution plan that references a DataContract and ActionProfiles to describe how/when to run cleansing/profiling/validation (`src/dq_jobs`).                                                                                 |
| **DQContext**          | Runtime SDK/context façade (`src/dq_sdk`) that orchestrates contract-driven jobs for notebooks, scripts, and orchestrators without introducing new configuration.                                                                          |
| **Store**              | Pluggable persistence abstraction (`src/dq_stores/`) backing registries for contracts, jobs, actions, and metadata (Postgres today; Blob/filesystem later).                                                                                |
| **Execution Engine**   | Backend-agnostic execution layer (`src/dq_engine/`) that runs cleansing/profiling/validation on different backends (Pandas now; Spark/SQL later) selected via infra/contract hints.                                                       |
| **Data Docs**          | Human-readable, tenant/environment-scoped documentation (HTML/markdown) of contracts, JobDefinitions, and runs generated by `src/dq_docs` for auditors and onboarding.                                                                     |

## 7. Example user/system flows

These flows provide context for how requirements in sections 5 and 6 manifest in end-to-end usage. See `docs/ARCHITECTURE.md` and `docs/ACTIONS_AND_JOB_DEFINITIONS.md` for matching diagrams.

### 7.1 Tenant onboarding and feed registration

1. **Catalog & contract design:** Data/contract stewards define or reuse catalogue entities/attributes in `dq_catalog` and author DataContracts for new feeds (`docs/CONTRACT_DRIVEN_ARCHITECTURE.md`).
2. **Rule & profile selection:** Stewards select or author rule templates in `rule_libraries/` and governance/infra profiles in `governance_libraries/` and `infra_libraries/`.
3. **Contract registration:** Contracts, schemas, and bindings are normalised to canonical JSON and registered via `dq_contracts` APIs.
4. **JobDefinition creation:** A JobDefinition is created in `dq_jobs` linking the new DataContract, dataset type, and ActionProfiles for success/failure/anomaly notifications.
5. **Verification:** Test uploads run through the pipeline (cleansing → profiling → validation) to confirm contract behaviour before promotion to higher environments.

### 7.2 Validation job execution (triggered by external orchestrator)

1. **Trigger:** An external orchestrator (e.g., Airflow, ADF) writes a dataset to Azure Blob and calls `POST /jobs/run/{job_definition_id}` on `dq_api`, passing the tenant, environment, and blob URI.
2. **Job resolution:** `dq_api` resolves the JobDefinition in `dq_jobs`, then resolves the referenced DataContract bundle (schema, rules, catalogue mappings, infra/gov profiles) from `dq_contracts`.
3. **Cleansing & profiling:** `dq_cleansing` and `dq_profiling` execute according to contract and tenant policies, emitting lineage and snapshots into `dq_metadata`.
4. **Validation:** `dq_core` runs validation rules using profiling contexts and contract bindings.
5. **Actions & reporting:** `dq_actions` resolves the ActionProfiles attached to the JobDefinition; `dq_integration` executes the corresponding notifications/webhooks/lineage events, and `dq_metadata` records action outcomes and job results for audit.

### 7.3 Audit evidence and compliance export

1. **Evidence request:** A governance or audit stakeholder requests evidence for a given tenant, dataset, time window, or incident.
2. **Metadata query:** Using APIs backed by `dq_metadata` (see `docs/METADATA_LAYER_SPEC.md`), the platform retrieves contracts, job runs, rules executed, cleansing/profiling outcomes, action executions, and governance profiles in force.
3. **Report packaging:** The platform must be able to generate an evidence pack (e.g., downloadable report, signed export) that shows “who changed what, when, and why,” which rules ran, which catalogue attributes they applied to, and which policy profiles governed the runs. Data Docs (see `docs/DATA_DOCS_STRATEGY.md`) should provide human-readable contract/job/run summaries suitable for auditors.
4. **Delivery:** Evidence packs are delivered via secure channels (download or export), and access is logged for compliance.

## 8. Non-functional requirements summary

- Performance, scalability, availability, security, retention, observability, maintainability, DR, and integration expectations per `docs/NON_FUNCTIONAL_REQUIREMENTS.md`.
- Metadata layer must align with overall SLAs and retention targets.

## 9. Governance, audit, and GDPR compliance

- Metadata layer specification (`docs/METADATA_LAYER_SPEC.md`) dictates capture of data assets, jobs, rule versions, audit events, and compliance tags, including GDPR-specific fields (classification, lawful basis, supported data subject rights, special category flags).
- The platform must provide immutable audit trails for configuration changes and privileged actions so that GDPR accountability and audit obligations can be met.
- The platform must be able to generate evidence packs on demand for regulators or internal audits, including information needed for GDPR records of processing, data subject request handling, and breach investigations.
- The platform must support retention policies configurable per tenant with enforcement checkpoints that respect GDPR storage limitation and erasure requirements.

## 10. Dependencies and integrations

- Azure Active Directory for authentication and RBAC enforcement.
- Azure Key Vault (or equivalent) for secret management.
- Storage services (Azure Blob or compatible) for file retention and report distribution.
- Corporate SIEM/GRC tooling for consuming metadata exports (future integration design).

## 11. Assumptions

- Stakeholders can supply canonical dataset definitions and mapping templates during onboarding.
- Network and platform resources for load testing, monitoring, and DR drills are available.
- Compliance requirements (e.g., GDPR, SOC 2) align with existing corporate policies and tooling.
- Future UI/admin experiences will consume the same API contracts defined here.

## 12. Risks and mitigations

| Risk                                                | Impact | Mitigation                                                                           |
| --------------------------------------------------- | ------ | ------------------------------------------------------------------------------------ |
| Incomplete metadata capture reduces audit readiness | High   | Enforce registry integration in every workflow, automated tests for metadata events. |
| Rule complexity exceeds current engine capabilities | Medium | Prioritize rule catalog definition, schedule iterative enhancements.                 |
| Tenant onboarding bottlenecks                       | Medium | Provide clear mapping templates and sandbox validation tools.                        |
| Performance degradation under peak loads            | Medium | Implement load tests, autoscaling strategies, and queue monitoring.                  |
| Compliance scope changes mid-project                | Medium | Maintain open questions log, design metadata layer for extensibility.                |

## 13. Success metrics and KPIs

| Metric                         | Target                                                                             | How measured                                                                                                                                                          | Reported via                                                                     |
| ------------------------------ | ---------------------------------------------------------------------------------- | --------------------------------------------------------------------------------------------------------------------------------------------------------------------- | -------------------------------------------------------------------------------- |
| **Validation job latency**     | ≥95% of validation jobs complete within the SLA (≤5 minutes for typical datasets). | Measure time from job submission in `dq_api` to validation completion recorded in `dq_metadata`.                                                                      | SLA dashboards and periodic reports built on `dq_metadata` job duration metrics. |
| **Rule change audit coverage** | 100% of rule changes captured with approval metadata and immutable audit records.  | Count rule/version changes in `dq_contracts` and governance libraries and verify that each has associated lifecycle + approval metadata in `dq_metadata`.             | Governance compliance reports and internal audit checks.                         |
| **Onboarding efficiency**      | At least 40% reduction in manual onboarding effort compared to the legacy process. | Track elapsed time and number of manual steps from initial dataset registration to first successful production run, using contract/job metadata and operational logs. | Product/operations review dashboards and post-onboarding retrospectives.         |
| **Compliance findings**        | Zero critical compliance findings during pilot audit.                              | Record and classify audit findings related to data quality/governance; measure number and severity per audit cycle.                                                   | Audit reports and compliance review meetings.                                    |

All metrics must be traceable to concrete data artifacts (contracts, jobs, metadata records, and actions) so that engineers and auditors can reproduce calculations.

## 14. High-level timeline (subject to refinement)

1. **Discovery & design (current):** Finalize specs, metadata design, and API contracts.
2. **MVP build:** Implement core validation pipeline, contract registry and semantic catalogue integration, and metadata registry foundation.
3. **Integration & hardening:** Connect security, retention, monitoring; run load and DR tests.
4. **Pilot rollout:** Onboard initial tenants, collect feedback, close gaps.
5. **General availability:** Broader deployment, finalize playbooks, hand over to operations.

## 15. Open questions

- Final infrastructure footprint (managed services vs. self-hosted components).
- Level of automation required for compliance evidence exports (manual trigger vs. scheduled).
- Scope of metadata access for external auditors (read-only API vs. curated reports).
- Governance ownership model post-launch (which team maintains metadata rules and policies).
- Selection of the external upload orchestration mechanism (event vs. webhook vs. polling) and corresponding SLAs.
