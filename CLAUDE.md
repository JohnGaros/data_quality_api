# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

Wemetrix Data Quality & Governance Platform — a contract-driven, multi-tenant data quality assessment platform that validates customer datasets against shared business rules. The platform uses explicit **data contracts** as the single source of truth for schemas, validation rules, cleansing logic, infra profiles, and governance policies.

**Key architectural principle:** Contract-Driven Architecture (CDA) — all engines consume versioned DataContracts + orthogonal libraries (rule_libraries, schema_libraries, infra_libraries, governance_libraries, action_libraries) + the semantic catalog (dq_catalog). No ad-hoc config files.

## Essential Commands

### Testing
```bash
# Run all tests
pytest

# Run unit tests only
pytest tests/unit/

# Run integration tests
pytest tests/integration/

# Run specific test file
pytest tests/unit/test_cleansing_engine.py

# Run with verbose output
pytest -v

# Run with coverage
pytest --cov=src --cov-report=html
```

### Code Quality
```bash
# Format code with black (line length 88)
black src/ tests/

# Lint with ruff
ruff check src/ tests/

# Type checking with mypy
mypy src/
```

### Local Development
```bash
# Initialize project structure
bash scripts/init_structure.sh

# Seed catalog data from catalog_libraries/
python scripts/seed_catalog.py

# Verify catalog refactor
python scripts/verify_catalog_refactor.py

# Run FastAPI application (from dq_api module)
# uvicorn dq_api.main:app --reload
```

## Planning System

This project uses a hierarchical planning system (Project → Milestones → Epics → Features) to track progress and enable fast context restoration after `/clear` operations.

### After /clear - ALWAYS Run This First

**Most important command after /clear:**

```bash
/planning-resume
```

This restores your work context in < 10 seconds by loading:
- Active feature checkpoint (< 100 lines total)
- Current phase and next task
- Minimal architecture context

**Do NOT manually re-read full architecture docs after /clear.** The resume command provides sufficient context to continue working.

### Tracking Progress

**Update checkpoint after completing work:**

```bash
# Complete a task
/planning-checkpoint --complete-task "Implement save_profiling_snapshot()"

# Move to next phase
/planning-checkpoint --next-phase

# Add blocker
/planning-checkpoint --add-blocker "Waiting for API contract approval"

# Complete feature
/planning-checkpoint --complete-feature
```

**View progress:**

```bash
# Show current feature status
/planning-status

# View project-wide dashboard
/planning-progress
```

### Checkpoint Files

Every feature has a `.checkpoint` file (YAML) in its directory that tracks:
- Feature status (not_started, in_progress, completed, blocked)
- Current phase and progress within phase
- Time spent per phase (automatic tracking)
- Blockers and notes

**Important:**
- Checkpoint files are gitignored (developer-local state)
- NEVER edit .checkpoint files manually - always use `/planning-checkpoint` commands
- Checkpoint updates are atomic (temp file → rename) to prevent corruption

### Hierarchical Structure

```
specs/
├── PROJECT_ROADMAP.md              # Overall project progress
├── milestones/
│   ├── M1_MVP_FOUNDATION/          # Current phase
│   │   ├── MILESTONE.md
│   │   └── epics/
│   │       ├── E1_CORE_VALIDATION/
│   │       │   ├── EPIC.md
│   │       │   └── features/
│   │       │       └── e2e_file_testing/
│   │       │           ├── IMPLEMENTATION.md
│   │       │           ├── TASKS.md
│   │       │           └── .checkpoint      # Progress state
│   │       └── E2_METADATA_LINEAGE/
│   ├── M2_SECURITY_COMPLIANCE/
│   └── M3_SCALE_OPERATIONS/
```

### Current Milestones

**M1: MVP Foundation** (Target: 2025-12-30) - In Progress
- E1: Core Validation (e2e_file_testing, core_rule_engine, api_upload_endpoints)
- E2: Metadata & Lineage (metadata_registry, audit_trail)

**M2: Security & Compliance** (Target: 2026-01-31) - Not Started
- E3: RBAC & GDPR (azure_ad_integration, gdpr_compliance, storage_retention)

**M3: Scale & Operations** (Target: 2026-02-28) - Not Started
- E4: Operations (tenant_management, observability, ci_cd_pipelines, azure_blob_storage)

See `specs/README.md` for complete planning system documentation.

## Architecture Overview

### Core Design Patterns

**1. Contract-Driven Everything**
- **DataContracts** define dataset schemas, rule bindings, catalog mappings, and references to orthogonal profiles
- Contracts stored as canonical JSON in Postgres JSONB, exposed via `dq_contracts.ContractRegistry`
- Engines (cleansing, profiling, validation) consume materialized contract bundles
- All authoring happens in YAML/JSON/Excel within libraries; canonical JSON is the only runtime format

**2. Orthogonal Libraries + Semantic Catalog**
- `rule_libraries/`: validation, cleansing, profiling rule templates (YAML/JSON/Excel → canonical JSON)
- `schema_libraries/`: reusable schemas, taxonomies, code lists
- `infra_libraries/`: storage/compute/retention profiles
- `governance_libraries/`: PII classifications, retention policies, access controls
- `action_libraries/`: post-job behaviors (notifications, lineage, webhooks)
- `catalog_libraries/`: **authoring layer for the semantic catalog** — YAML definitions for canonical entities/attributes
- `dq_catalog`: runtime registry for semantic entities/attributes/relationships; contracts map producer fields to catalog attributes

**3. Registry Pattern**
- `dq_contracts`: DataContract + DatasetContract + RuleTemplate + RuleBinding registry
- `dq_actions`: ActionProfile registry (planned)
- `dq_jobs`: JobDefinition/Checkpoint registry (planned)
- `dq_metadata`: Job lineage, profiling snapshots, audit events, compliance tags

**4. Execution Flow**
```
External Trigger/API → JobDefinition lookup → Contract resolution → Cleansing (optional) → Profiling → Validation → Action execution → Metadata recording
```

### Key Module Responsibilities

| Module | Directory | Purpose |
|--------|-----------|---------|
| **API Layer** | `src/dq_api/` | FastAPI routes, job orchestration, RBAC wiring |
| **Contracts** | `src/dq_contracts/` | Contract registry, canonical JSON persistence |
| **Catalog (Runtime)** | `src/dq_catalog/` | Semantic catalog registry — loads YAML from catalog_libraries/, provides models/loader/repository |
| **Catalog (Authoring)** | `catalog_libraries/` | YAML authoring layer for canonical entities/attributes — source of truth for semantic catalog |
| **Cleansing** | `src/dq_cleansing/` | Policy-driven transformations, chaining to profiling/validation |
| **Profiling** | `src/dq_profiling/` | ProfilingEngine, context builder, statistics exports |
| **Validation** | `src/dq_core/` | Rule engine, evaluator, profiling-driven validation |
| **Metadata** | `src/dq_metadata/` | Lineage, audit events, profiling snapshots, compliance tags |
| **Integration** | `src/dq_integration/` | Azure Blob, notifications, Power Platform, action executors |
| **Security** | `src/dq_security/` | Azure AD auth, RBAC, Key Vault, audit logging |
| **Actions** | `src/dq_actions/` | ActionProfile registry (planned) |
| **Jobs** | `src/dq_jobs/` | JobDefinition registry (planned) |
| **SDK/Context** | `src/dq_sdk/` | DQContext facade for notebooks/CLI/tests |
| **Stores** | `src/dq_stores/` | Pluggable persistence (Postgres, Blob, filesystem) |
| **Engine Abstraction** | `src/dq_engine/` | Backend-agnostic execution (Pandas now, Spark future) |
| **Data Docs** | `src/dq_docs/` | HTML/markdown rendering for contracts/jobs/runs |

### Multi-Tenancy & Environment Scoping

All contracts, jobs, metadata, and action profiles are scoped by:
- `tenant_id`: logical customer isolation
- `environment`: `dev`, `test`, `prod`

**Never mix tenants in the same storage container, queue, or query without explicit tenant filtering.**

## Critical Development Guidelines

### Working with Contracts

**DO:**
- Read contracts from `dq_contracts.ContractRegistry` using tenant + environment + dataset_type
- Use `to_canonical_json()` from `dq_contracts.serialization` for all persistence/API responses
- Include `contract_id`, `dataset_contract_id`, and `rule_binding_id` in all job metadata
- Reference catalog entities/attributes via `catalog_entity_ids` and `catalog_attribute_id`
- Author new catalog entities/attributes in `catalog_libraries/*.yaml` following the append-only versioning pattern
- Run `python scripts/seed_catalog.py` after modifying catalog_libraries/ to load into repository

**DON'T:**
- Create ad-hoc config files outside the library/contract system
- Hard-code schemas, rules, or thresholds in engine code
- Mix authoring formats at runtime (always canonical JSON after loading)

### Working with Engines

**Cleansing:**
- Cleansing is policy-driven and optional; job manager decides whether to invoke
- Outputs: cleansed dataset URI + rejection set + transformation metrics
- Profiling/validation consume cleansed dataset, not raw upload
- Link cleansing job ID in validation job metadata for lineage

**Profiling:**
- `ProfilingEngine` produces snapshots (per-field stats + overrides)
- `ProfilingContextBuilder` normalizes snapshots for rule engine consumption
- Profiling snapshots include: counts, min/max/mean/stddev, frequent values, distributions
- Each job records `profiling_context_id` for metadata traceability

**Validation:**
- Rule engine executes rule bindings from contract within profiling-driven context
- Profiling context can override default thresholds dynamically
- Validation results reference cleansing job ID if cleansing occurred

### Metadata & Lineage

**Required metadata for every job:**
- `job_id`, `tenant_id`, `environment`, `submission_source`
- `ingestion_mode`: `direct` or `external_reference`
- `blob_uri`, `blob_etag` (if external upload)
- `config_version` (contract version applied)
- `profiling_context_id`
- `cleansing_job_id` (if cleansing occurred)

**Audit trail requirements:**
- All privileged actions (contract changes, job definitions, action profiles) logged to `metadata_audit_events`
- Immutable history: no updates to audit/rule_version entries; create new versions
- Compliance tags (PII, GDPR, retention) drive encryption, access controls, and evidence packs

### Security & GDPR

**Authentication & RBAC:**
- Azure AD (OAuth 2.0 / OpenID Connect) via `dq_security/auth_provider.py`
- Tenant + environment claims validated on every API call
- RBAC middleware enforces role-based access in `dq_api`

**GDPR Compliance:**
- Governance profiles capture: classification, lawful basis, data subject rights
- Metadata compliance tags track: `gdpr_classification`, `lawful_basis`, `is_special_category`, `data_subject_rights`
- Retention policies enforced before deletion; decisions logged
- Audit events support: access requests, rectification, erasure, restriction, portability, objection
- Breach investigation: metadata exports provide lineage + audit trail

**Secret Management:**
- Azure Key Vault for all secrets (DB credentials, API keys, tokens)
- Configuration patterns in `infra/azure/keyvault-*`

### Actions & JobDefinitions

**ActionProfiles:**
- Authored in `action_libraries/` (YAML/JSON/Excel → canonical JSON)
- Stored in `dq_actions` registry (Postgres JSONB)
- Referenced by JobDefinitions via `ActionProfileRef`
- Executed post-job: `on_success`, `on_failure`, `on_anomaly`
- Types: `STORE_RESULTS`, `SEND_NOTIFICATION`, `EMIT_LINEAGE`, `CALL_WEBHOOK`, `OPEN_TICKET`

**JobDefinitions:**
- Tenant-scoped execution plans stored in `dq_jobs`
- Reference: `DataContract` + `ActionProfiles`
- Trigger types: `MANUAL`, `SCHEDULED`, `EXTERNAL_EVENT`
- External orchestrators (Airflow, ADF) call `/jobs/run/{job_definition_id}`
- Platform resolves contract, runs cleansing/profiling/validation, executes actions

**Non-Goals:**
- Actions/JobDefinitions never redefine contracts, rules, schemas, infra, or governance
- Platform is NOT a generic ETL orchestrator

## Testing Patterns

### Test-Driven Development (TDD) Approach

This project follows a **pragmatic TDD approach** — use test-first development where it adds the most value, but remain flexible when strict TDD would slow down progress.

**Use TDD when:**
- Implementing core business logic (validation rules, cleansing policies, profiling algorithms)
- Building new registries or engines with clear contracts
- Handling GDPR/compliance requirements where correctness is critical
- The requirements are well-defined and stable
- Working with complex domain logic that benefits from test-first design clarity

**Skip strict TDD when:**
- Doing exploratory work or spikes to understand requirements
- Refactoring existing code that already has good test coverage
- Working on UI/API routing layers where feedback is more visual
- The requirements are still being clarified or are likely to change
- Making simple, obvious changes to well-understood code

**Why this approach fits the platform:**
- Multi-tenancy and GDPR compliance are high-stakes (bugs = data breaches)
- Contract-driven architecture provides clear boundaries ideal for test-first design
- Complex domain logic (rule evaluation, profiling context building) benefits from TDD discipline
- Integration points benefit from test-first thinking about failure modes

### Test Types

**Unit tests** (`tests/unit/`):
- Test individual functions/classes in isolation
- Mock external dependencies (DB, blob storage, Azure AD)
- Fast execution, no I/O

**Integration tests** (`tests/integration/`):
- End-to-end flows: upload → contract resolution → cleansing → profiling → validation
- Use test databases/containers (clean after each run)
- Verify module interactions

**Regression tests** (`tests/regression/`):
- Guard against previously fixed issues
- Use `dq_tests/` harness when implemented

**Action/JobDefinition tests:**
- Assert canonical JSON round-trips
- Verify registry lookup and job manager wiring
- Simulate post-job action execution

## Common Pitfalls

1. **Don't bypass the contract registry** — always fetch contracts via `ContractRegistry`, never read YAML/JSON directly in engines
2. **Profiling context is mandatory** — validation jobs must reference `profiling_context_id` even if no overrides applied
3. **Tenant isolation** — all queries/storage must filter by `tenant_id` + `environment`
4. **Canonical JSON everywhere** — use `to_canonical_json()` for all persistence/API responses; never serialize Pydantic models directly without normalization
5. **Cleansing lineage** — when cleansing runs, validation metadata must reference `cleansing_job_id`
6. **GDPR tags required** — all datasets processing personal data must have compliance tags with `gdpr_classification`, `lawful_basis`
7. **Immutable audit trail** — never UPDATE audit/rule_version entries; always INSERT new versions
8. **Catalog versioning is append-only** — never change the semantic meaning of an existing `catalog_entity_id` or `catalog_attribute_id`; create new versioned IDs (e.g., `customer_email_v2`) and mark old ones as deprecated

## File Organization Conventions

- Models: `*/models.py` or `*/models/*.py` (Pydantic, SQLAlchemy)
- Registries: `*/registry.py` (high-level CRUD coordination)
- Repositories: `*/repository.py` (storage abstraction, DB/filesystem/blob)
- Loaders: `*/loader.py` (YAML/JSON/Excel → Pydantic + canonical JSON)
- Serialization: `*/serialization.py` (canonical JSON normalization)
- Engines: `*/engine/*.py` (execution logic)
- APIs: `*/api/*.py` or `*/routes/*.py` (FastAPI routers)

## Documentation References

- **Architecture:** `docs/ARCHITECTURE.md` — comprehensive component overview
- **Contract-Driven Architecture:** `docs/CONTRACT_DRIVEN_ARCHITECTURE.md` — CDA principles and patterns
- **Actions & JobDefinitions:** `docs/ACTIONS_AND_JOB_DEFINITIONS.md` — post-job orchestration
- **Metadata Layer:** `docs/METADATA_LAYER_SPEC.md` — lineage, audit, compliance
- **Security:** `docs/SECURITY_GUIDE.md` — auth, RBAC, Key Vault, GDPR
- **API Contracts:** `docs/API_CONTRACTS.md` — REST endpoint specifications
- **Business Requirements:** `docs/BRD.md` — product context and scope
- **File Structure:** `docs/ARCHITECTURE_FILE_STRUCTURE.md` — detailed directory breakdown

## Repository Context

- **Main branch:** `main` (PRs target this branch)
- **Current branch:** `claude` (check branch before committing)
- **Python version:** 3.10+
- **Code style:** Black (line length 88), Ruff, Mypy strict mode
- **Dependencies:** FastAPI, Pydantic, pytest (see `pyproject.toml`)

### Git Remotes

This repository has two remotes:

| Remote | Platform | URL |
|--------|----------|-----|
| `origin` | GitHub | https://github.com/JohnGaros/data_quality_api.git |
| `secondary` | Azure DevOps | https://dev.azure.com/WeMetrix/... |

**Push commands:**
- GitHub: `git push origin <branch>`
- Azure DevOps: `git push secondary <branch>`
- Both: `git push origin <branch> && git push secondary <branch>`

See `.claude/skills/git-push.md` for the full git-push skill with intent mapping.

## Commit Strategy

**IMPORTANT: Claude should proactively commit work without waiting for user prompts.**

### When to Commit

Commit after completing any of the following:

1. **Completing a logical unit of work** — a function, class, test, or config change that works independently
2. **Finishing a task from the todo list** — each completed task should be committed
3. **Before switching context** — if moving to a different file/feature, commit current work first
4. **After fixing a bug** — each bug fix is a separate commit
5. **After adding/updating tests** — test changes get their own commit
6. **Before running potentially destructive operations** — commit as a checkpoint
7. **When a phase milestone is reached** — completing a phase in a feature deserves a commit

### Commit Frequency Guidelines

- **Aim for small, focused commits** — one logical change per commit
- **Don't batch unrelated changes** — separate commits for separate concerns
- **Commit working code** — ensure tests pass before committing (run `pytest` for affected areas)
- **Never go more than 30 minutes of work without committing** — if working on something large, find natural breakpoints

### Commit Message Format

```
<type>(<scope>): <short description>

<optional body explaining why, not what>

🤖 Generated with [Claude Code](https://claude.com/claude-code)

Co-Authored-By: Claude <noreply@anthropic.com>
```

**Types:** `feat`, `fix`, `refactor`, `test`, `docs`, `chore`, `style`

**Examples:**
- `feat(catalog): add PostgresCatalogStore implementation`
- `fix(validation): handle null values in profiling context`
- `test(cleansing): add unit tests for rejection set generation`
- `refactor(contracts): extract serialization to separate module`

### Self-Check Before Committing

Before each commit, Claude should verify:
- [ ] Code compiles/parses without errors
- [ ] Related tests pass (run `pytest tests/unit/test_<module>.py` if applicable)
- [ ] No debug prints or temporary code left behind
- [ ] Commit message accurately describes the change

### Proactive Commit Behavior

Claude should:
- **Announce intent to commit** before doing so: "I've completed X, committing this change now."
- **Not ask permission** for routine commits — just commit and inform
- **Group related micro-changes** — if fixing typos in 3 files, one commit is fine
- **Separate unrelated changes** — a bug fix and a new feature are separate commits

## When Making Changes

1. **Read relevant docs first** — especially `ARCHITECTURE.md` and module-specific READMEs
2. **Check existing tests** — understand current patterns before adding new code
3. **Maintain contract-driven discipline** — if adding config, it belongs in a library or contract
4. **Update canonical JSON** — if changing models, update `to_canonical_json()` and tests
5. **Preserve tenant isolation** — all new endpoints/queries must filter by tenant + environment
6. **Document GDPR impact** — if handling personal data, update compliance tags and governance profiles
7. **Test lineage** — verify metadata linkage (job → cleansing → profiling → validation)
