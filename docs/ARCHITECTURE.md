# System Architecture — Data Quality Assessment API

## 1. High-level view
- **Goal:** Validate customer data files against shared business rules while maintaining audit-ready lineage.
- **Interfaces:** FastAPI-based REST layer (`src/dq_api/`), Azure Blob Storage for file persistence, Azure AD for authentication, and optional external upload orchestrators.
- **Tenancy:** All services operate in a multi-tenant context; configuration and metadata are scoped per tenant.

## 2. Core components
- **API Layer (`dq_api/`):** Routes for uploads, validation status, configuration management, tenants, and admin tooling. Future `external_uploads` endpoint will accept blob references from external upload services.
- **Rule Engine (`dq_core/engine/`):** Builds profiling-driven validation contexts, executes rules, and emits metadata events.
- **Configuration Management (`dq_config/`):** Loads, validates, and versions rule libraries plus mapping templates.
- **Metadata Layer (`dq_metadata/`):** Persists job lineage, profiling context snapshots, rule versions, and audit events. Provides querying interfaces used by dashboards and compliance exports.
- **Integrations (`dq_integration/`):** Adapters for Azure Blob Storage, Power Platform, and notifications. `azure_blob/external_triggers.py` is reserved for event/webhook/polling helpers once orchestration decisions are final.
- **Security (`dq_security/`):** Handles Azure AD auth, RBAC middleware, secret management via Key Vault, and audit logging.

## 3. Upload pathways
- **Direct uploads (current):** Clients submit files via `/uploads`. Job manager stores raw files, triggers profiling, runs validations, and records results.
- **Decoupled uploads (future):** External service writes to Azure Blob and signals the DQ API by event, webhook, or polling (decision pending). The payload contains blob URI, ETag, tenant metadata, and optional profiling overrides. The API enqueues the job through `external_trigger_service.py` once implemented.
- **Metadata impact:** Every job records `ingestion_mode`, blob references, and trigger metadata so auditors can trace the file’s origin.

## 4. Data & control flow (summary)
1. **Ingestion:** Either direct upload or external trigger registers a validation job.
2. **Profiling:** Workers analyse the dataset to produce metrics that drive dynamic thresholds.
3. **Validation:** Rule engine executes all active rules inside the profiling-driven context.
4. **Reporting:** Results flow to report services for download/export and to notification channels.
5. **Lineage:** Metadata registry links blob assets, rule versions, profiling context, and outcomes for every run.

Refer to workflow diagrams in `docs/diagrams/*.mmd` for sequence details (`upload_validation_flow`, `external_upload_trigger`, `config_promotion_flow`).

## 5. Governance & observability
- **Audit readiness:** Every configuration change, upload event, and rule execution is logged with correlation IDs.
- **Compliance tooling:** Metadata exports support evidence packs and dashboards; external ingestion views surface blob-specific lineage.
- **Monitoring:** Health endpoints, structured logging, and future telemetry hooks (e.g., queue lag) feed platform observability.

## 6. Pending decisions & next steps
- **Upload orchestration:** Need to confirm whether Event Grid, direct webhook callbacks, or polling will be used for external uploads. Placeholder services/configs (`external_uploads.py`, `external_trigger_service.py`, `external_upload.example.yaml`) remain ready.
- **Profiling pipeline hardening:** Profiling workers must be wired to emit context snapshots and thresholds before production launch.
- **Integration roadmap:** Once orchestration is chosen, implement Azure event handlers or schedulers in `azure_blob/external_triggers.py` and update API contracts accordingly.

For a detailed file-by-file breakdown, see `docs/ARCHITECTURE_FILE_STRUCTURE.md`. Business and functional requirements live in `docs/BRD.md` and `docs/FUNCTIONAL_REQUIREMENTS.md`.
