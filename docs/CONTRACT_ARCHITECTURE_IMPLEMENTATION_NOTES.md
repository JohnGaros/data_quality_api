# Contract Architecture Implementation Notes

## Discovery summary
- **Existing separation of concerns:** `dq_core` owns the validation engine and already depends on `dq_profiling` contexts (`rule_engine.RuleEngine.build_context`). Rule authoring lives in `rule_libraries` (YAML/JSON/Excel loaders), and cleansing orchestration (`dq_cleansing`) is scaffolded but intentionally decoupled so new data sources can plug in without rewriting engines. Legacy `dq_config` wrappers have been removed in favour of direct `rule_libraries` + `dq_contracts` flows.
- **Metadata hooks:** `dq_metadata.models` enumerates governance artifacts (data assets, validation jobs, rule versions, audit events, compliance tags). `MetadataRegistry` wraps `IMetadataRepository` (currently `FileMetadataRepository`) and is the natural home for recording contract IDs, dataset schemas, and rule bindings once they are first-class citizens.
- **API/service orchestration:** `dq_api.services.job_manager` (stubbed) and related FastAPI routers route uploads, cleansing jobs, and reporting. RBAC and audit logging responsibilities flow through `dq_security` and `dq_admin`, so the contract API surface must enforce tenant and role scope from day one.
- **Rule & config inputs:** Templates in `rule_libraries/validation_rules`, `rule_libraries/profiling_rules`, and `rule_libraries/cleansing_rules` plus logical field references in `docs/DATA_MODEL_REFERENCE.md` already look like implicit contracts. YAML is now a first-class authoring format (alongside JSON/Excel) for validation, cleansing, and profiling rules; loaders in `rule_libraries` normalise all formats into Pydantic models and canonical JSON so engines and metadata consumers can depend on a unified schema-versioned contract.
- **Engine integration gap:** Neither the validation nor cleansing engine currently consumes a structured dataset schema; they expect downstream services to pre-select active rules. The data contract layer must supply dataset contracts (schema + constraints) alongside rule bindings so engines can resolve executable rules without bespoke configuration plumbing.

## Where the data contract layer fits
- **New module (`src/dq_contracts/`):** Houses Pydantic models for `DataContract`, `DatasetContract`, `ColumnContract`, `RuleTemplate`, and `RuleBinding`, plus loader/serializer utilities. These models reference logical field keys from `dq_core.models.logical_field` and rule identifiers from existing rule libraries.
- **Registry + repository:** A Postgres-backed contract registry (SQLAlchemy models + repository) persists contract YAML/JSON, dataset schemas, rule templates, and bindings. This registry provides APIs for CRUD, search, versioning, and environment promotion while enforcing tenant/environment scoping.
- **Loader + sync pipeline:** YAML contracts in `configs/contracts/` will flow through a loader → validator → serializer pipeline and land in Postgres via the ContractRegistry. The same layer can export DB-backed contracts back to YAML for change control.
- **Engine adapters:** Validation (`dq_core.engine`), cleansing (`dq_cleansing.engine`), and profiling contexts will request dataset/rule definitions from the ContractRegistry instead of any legacy config loaders.
- **API exposure:** New FastAPI routes (`/contracts`, `/datasets`, `/rule-templates`) plus supporting services/RBAC will orchestrate contract lifecycle operations (register, search, promote, deploy). Metadata entries (e.g., `ValidationJobMetadata`, `RuleVersionMetadata`) will be extended to include contract and binding identifiers for lineage.

## TODO checklist
1. **Modeling:** Implement `src/dq_contracts/models.py` (enums, Pydantic models, versioning fields) and update architecture docs to mention the module.
2. **Persistence:** Design SQL schema + migration files for contracts, datasets, columns, rule templates, and bindings. Implement repository + registry services mirroring `dq_metadata` patterns but targeting Postgres.
3. **Rule template catalog:** Normalize cleansing/validation/profiling templates into shared structures and expose catalog APIs through the registry.
4. **Loader & sync:** Build YAML loader, validators, serializers, and CLI sync script; add sample contracts under `configs/contracts/`.
5. **Engine integration:** Adapt validation, cleansing, and profiling engines plus job managers to consume dataset/rule definitions from the ContractRegistry (with feature flag for backward compatibility).
6. **API layer:** Add `/contracts`, `/datasets`, `/rule-templates` routes, schemas, and services with RBAC and metadata/audit hooks.
7. **Streaming hooks (optional):** Stub schema registry clients + models for future Confluent/Azure integrations and link to dataset contracts.
8. **Testing & docs:** Expand unit/integration tests across models, loaders, registry, and API flows; update architecture/reference docs to explain the contract-driven architecture end-to-end.
