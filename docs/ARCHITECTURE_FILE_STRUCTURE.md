# 🧭 Data Quality Assessment API — File Structure Breakdown

## 1. Overview

This document explains the organization logic behind the project’s folder and file structure, including the new enterprise security and Azure deployment components.
It describes what each directory and file is for, how they interact, and how the design supports scalability, modularity, and compliance with enterprise cloud security standards.

---

## 2. Design Principles

| Principle                   | Description                                                                                       |
| --------------------------- | ------------------------------------------------------------------------------------------------- |
| Separation of Concerns      | Each layer (core engine, API, admin, integrations, security) is isolated and modular.             |
| Extensibility               | Future modules (DSL parser, testing, Azure extensions) can be added without refactoring the core. |
| Multi-Tenant Readiness      | Configurations, rules, and customer data are isolated per tenant.                                 |
| API-First Design            | Core functionality is exposed via REST endpoints using FastAPI.                                   |
| Cloud-Native Deployment     | Infrastructure optimized for Azure App Services and Kubernetes (AKS).                             |
| Enterprise Security         | Integration with Azure Active Directory, Key Vault, and RBAC enforcement.                         |
| Documentation & Testability | Dedicated folders for technical docs and test suites ensure maintainability.                      |

---

## 3. Root-Level Structure

```text
data_quality_api/
├── src/                # Application source code
├── configs/            # Configuration files and rule libraries
├── scripts/            # Utility scripts (run, seed, migrate)
├── infra/              # Deployment, containers, CI/CD
├── docs/               # Documentation (architecture, guides)
├── tests/              # Automated test suites
├── requirements.txt    # Python dependencies
├── pyproject.toml      # Optional (for Poetry builds)
├── .env.example        # Environment variable template
├── .gitignore          # Git exclusions
└── README.md           # Project overview and setup
```

**Logic:**

- `src/` is the core codebase — designed as a modular Python package.
- `configs/` holds environment-specific configuration files (rule definitions, logging, etc.).
- `scripts/` provides developer and deployment utilities.
- `infra/` contains all infrastructure-related manifests (containers, pipelines, etc.).
- `docs/` houses architectural documentation and developer guides.
- `tests/` organizes unit, integration, and regression test suites.

---

## 4. `src/` Directory — Application Modules

```text
src/
├── dq_core/           # Core rule engine and models
├── dq_api/            # REST API layer (FastAPI)
├── dq_config/         # Rule and mapping configuration management
├── dq_admin/          # System and tenant administration
├── dq_metadata/       # Governance metadata layer
├── dq_integration/    # External integrations (Azure, Power Platform)
├── dq_security/       # Enterprise security and authorization
├── dq_dsl/            # Rule DSL (future)
├── dq_tests/          # Rule regression and test harness (future)
└── main.py            # FastAPI entrypoint
```

### 4.1 `dq_core/` — Core Validation Engine

**Purpose:** Contains the business logic and data models for rule execution.

```text
dq_core/
├── models/
│   ├── logical_field.py
│   ├── field_mapping.py
│   ├── data_quality_rule.py
│   ├── customer_profile.py
│   └── dq_config.py
├── engine/
│   ├── rule_engine.py
│   ├── evaluator.py
│   └── helpers.py
└── report/
	├── validation_report.py
	└── exporters.py
```

- **models/**: Pydantic data models for rules, logical fields, mappings, and configs.
- **engine/**: Core logic for evaluating rules and building derived fields.
- **report/**: Classes and utilities for structuring and exporting validation reports.

**Example Responsibilities:**

- `rule_engine.py`: Executes all active rules for a given customer and dataset.
- `evaluator.py`: Safely computes arithmetic and logical expressions (cross-file support).
- `validation_report.py`: Defines Pydantic models for report serialization.
- `exporters.py`: Exports results as JSON, CSV, or Power BI feed.

---

### 4.2 `dq_api/` — REST API Layer

**Purpose:** Exposes core functionality through REST endpoints (FastAPI). Organized by user role and functional domain.

```text
dq_api/
├── routes/
│   ├── uploads.py
│   ├── validation.py
│   ├── rules.py
│   ├── tenants.py
│   ├── auth.py
│   └── health.py
├── services/
│   ├── job_manager.py
│   ├── report_service.py
│   └── notification_service.py
├── dependencies.py
├── schemas.py
├── middlewares.py
├── settings.py
└── app_factory.py
```

- **routes/**: HTTP endpoints grouped by functionality and user role.
- **services/**: Business logic for async jobs, report access, and notifications.
- **middlewares.py**: Logging, timing, and authentication hooks.
- **settings.py**: Environment configuration (loaded from `.env`).
- **app_factory.py**: Constructs the FastAPI application.

**Examples:**

- `/upload/` → File upload and validation trigger (Uploader role)
- `/config/` → CRUD for rules and mappings (Configurator role)
- `/admin/` → Tenant and system management (Admin role)

---

### 4.3 `dq_config/` — Configuration Management

**Purpose:** Manages parsing, validation, and versioning of configuration artifacts such as rule definitions and mappings.

```text
dq_config/
├── loader.py
├── registry.py
├── serializers.py
└── validators.py
```

- **loader.py**: Parses Excel or JSON-based Functional Design Requirements (FDR) files into Python models.
- **registry.py**: Central repository of active rules and configurations (supports versioning).
- **serializers.py**: Converts Pydantic models to/from database or API formats.
- **validators.py**: Checks rule consistency, duplicate IDs, and schema mismatches.

---

### 4.4 `dq_admin/` — Administrative Layer

**Purpose:** Provides system-level management for users, tenants, roles, and audit trails.

```text
dq_admin/
├── rbac.py
├── tenant_manager.py
├── audit_log.py
└── user_manager.py
```

- **rbac.py**: Implements role-based access control (Uploader, Configurator, Admin).
- **tenant_manager.py**: Handles tenant onboarding, configuration isolation, and metadata.
- **audit_log.py**: Records user actions, rule changes, and validation runs.
- **user_manager.py**: Manages API users and authentication credentials.

---

### 4.5 `dq_metadata/` — Metadata & Governance Layer

**Purpose:** Centralizes governance metadata for datasets, validation jobs, rule versions, and audit events.

```text
dq_metadata/
├── __init__.py
├── models.py
├── registry.py
├── lineage.py
├── compliance.py
└── events.py
```

- **models.py**: Defines Pydantic models for data assets, job lineage, rule versions, audit events, and compliance tags.
- **registry.py**: Provides a service interface to persist metadata and expose lookup/query helpers.
- **lineage.py**: Builds relationships between uploads, rules, reports, and downstream exports.
- **compliance.py**: Implements retention and policy enforcement checks before actions complete.
- **events.py**: Shares standardized metadata event payloads across API, engine, and admin modules.

This layer underpins governance by supporting audit evidence, compliance tagging, and traceability dashboards.

---

### 4.6 `dq_integration/` — External Integrations

**Purpose:** Manages connectivity with external platforms, such as Azure Blob Storage and Microsoft Power Platform.

```text
dq_integration/
├── azure_blob/
│   ├── blob_client.py
│   ├── blob_storage_config.py
│   └── blob_job_adapter.py
├── power_platform/
│   ├── powerapps_connector.py
│   ├── powerbi_exporter.py
│   └── msflow_hooks.py
└── notifications/
	├── email_notifier.py
	├── webhook_notifier.py
	└── ms_teams_notifier.py
```

- **azure_blob/**: Handles file storage, retrieval, and event-driven validations using Azure Blob containers.
- **power_platform/**: Enables integration with PowerApps, Power BI, and Power Automate (MS Flow).
- **notifications/**: Sends alerts and reports via email, webhooks, or MS Teams.

---

### 4.7 `dq_dsl/` — Domain-Specific Language (Future Enhancement)

### 4.8 `dq_security/` — Enterprise Security Layer

**Purpose:** Centralized module for identity, authorization, secret management, and audit logging — ensuring compliance with enterprise security requirements on Azure.

```text
dq_security/
├── __init__.py
├── auth_provider.py          # Integrates with Azure AD (OAuth2 / OpenID Connect)
├── rbac_middleware.py        # Middleware enforcing role-based access control
├── keyvault_client.py        # Securely retrieves secrets from Azure Key Vault
├── encryption_utils.py       # Data encryption/decryption utilities
└── audit_logger.py           # Streams audit logs to Azure Monitor or Sentinel
```

| Component           | Responsibility                                                           |
| ------------------- | ------------------------------------------------------------------------ |
| auth_provider.py    | Handles authentication tokens and Azure Active Directory integration.    |
| rbac_middleware.py  | Enforces RBAC policies (Uploader, Configurator, Admin) at the API layer. |
| keyvault_client.py  | Provides secure access to secrets using Managed Identity.                |
| encryption_utils.py | Ensures data encryption at rest and in transit.                          |
| audit_logger.py     | Sends user activity and system logs to Azure Monitor.                    |

This layer is critical for ensuring Zero Trust compliance, multi-tenant isolation, and secure cloud operation.

---

### 4.9 `dq_tests/` — Testing Framework (Future)

**Purpose:** Automated regression testing for rules and configurations.

```text
dq_tests/
├── test_cases/
│   ├── rule_regression.yaml
│   └── integration_tests.yaml
├── generator.py
├── runner.py
└── reports/
```

- **generator.py**: Generates synthetic datasets to test rule behavior.
- **runner.py**: Executes regression tests and compares outcomes.
- **test_cases/**: YAML-based test definitions for reproducibility.
- **reports/**: Stores test results for validation and audit purposes.

---

### 4.10 `main.py` — API Entrypoint

**Purpose:** Bootstraps the FastAPI app, loads configuration, and starts the API service.

**Responsibilities:**

- Initialize environment and dependencies
- Mount all API routes
- Start the ASGI server

---

## 5. Supporting Directories

### `configs/`

Holds environment-specific and rule-specific configuration files.

```text
configs/
├── example_dq_config.json
├── logging.yaml
├── settings.env
└── rules/
```

- `example_dq_config.json`: Example configuration file following the DQConfig schema.
- `logging.yaml`: Logging configuration (used by API and engine).
- `settings.env`: Environment variables for local development.
- `rules/`: Folder for versioned rule libraries or FDR exports.

---

### `scripts/`

Utility and administrative scripts.

```text
scripts/
├── run_local.sh
├── seed_demo_data.py
└── migrate_db.py
```

- `run_local.sh`: Starts the local development server.
- `seed_demo_data.py`: Seeds demo tenants and rules for testing.
- `migrate_db.py`: Runs database migrations and schema sync.

---

### `infra/`

Infrastructure and deployment automation for Docker, Kubernetes, CI/CD, and Azure.

```text
infra/
├── Dockerfile
├── docker-compose.yaml
├── k8s/
│   ├── api-deployment.yaml
│   ├── api-service.yaml
│   ├── postgres-deployment.yaml
│   └── storage-secrets.yaml
├── azure/
│   ├── keyvault-config.yaml      # Key Vault and secret reference definitions
│   ├── api_management.yaml       # Azure API Management configuration
│   ├── app_gateway_waf.yaml      # Application Gateway + WAF setup
│   ├── monitor_diagnostics.yaml  # Azure Monitor / Log Analytics integration
│   └── network_rules.yaml        # Network Security Group and VNet rules
└── ci_cd/
	├── github-actions.yaml
	├── tests.yml
	└── build_and_push.yaml
```

| Subfolder | Purpose                                                                      |
| --------- | ---------------------------------------------------------------------------- |
| k8s/      | Manifests for AKS deployment of API, DB, and secret mounts.                  |
| azure/    | Enterprise-grade security and networking configuration for Azure deployment. |
| ci_cd/    | Continuous integration and deployment workflows.                             |

---

### `docs/`

Documentation hub for system architecture, configuration, and security governance.

```text
docs/
├── API_SPEC.md
├── ARCHITECTURE.md
├── ARCHITECTURE_FILE_STRUCTURE.md   # (this document)
├── CONFIG_GUIDE.md
├── INTEGRATION_GUIDE.md
├── ROADMAP.md
├── SECURITY_GUIDE.md               # Security framework and Azure integration guide
└── RBAC_MODEL.md                   # Role definitions and access control policies
```

| Document                       | Description                                                                         |
| ------------------------------ | ----------------------------------------------------------------------------------- |
| SECURITY_GUIDE.md              | Details authentication, Key Vault usage, encryption, and monitoring setup in Azure. |
| RBAC_MODEL.md                  | Defines role permissions (Uploader, Configurator, Admin) and enforcement logic.     |
| ARCHITECTURE_FILE_STRUCTURE.md | Documents this file structure and its rationale.                                    |
| INTEGRATION_GUIDE.md           | Describes Power Platform and Blob Storage connectors.                               |

---

### `tests/`

Test suite following standard Python pytest conventions.

```text
tests/
├── unit/
├── integration/
├── regression/
└── conftest.py
```

- **unit/**: Unit tests for isolated functions and classes.
- **integration/**: Tests API endpoints, database, and blob interactions.
- **regression/**: Tests for consistent rule behavior across versions.
- **conftest.py**: Shared pytest fixtures and configuration.

---

## 6. Future Evolution

## 6. Security and Azure Integration Summary

| Layer            | Mechanism                    | Location                                                          |
| ---------------- | ---------------------------- | ----------------------------------------------------------------- |
| Authentication   | Azure AD / OpenID Connect    | dq_security/auth_provider.py                                      |
| Authorization    | Central RBAC middleware      | dq_security/rbac_middleware.py                                    |
| Secrets          | Azure Key Vault              | dq_security/keyvault_client.py, infra/azure/keyvault-config.yaml  |
| Encryption       | At-rest & in-transit         | dq_security/encryption_utils.py, infra/azure/app_gateway_waf.yaml |
| Audit Logging    | Azure Monitor / Sentinel     | dq_security/audit_logger.py, infra/azure/monitor_diagnostics.yaml |
| Network Security | API Management + VNets + WAF | infra/azure/                                                      |
| Documentation    | Security & RBAC details      | docs/SECURITY_GUIDE.md, docs/RBAC_MODEL.md                        |

---

## 7. Future Evolution

| Phase   | Focus                   | Relevant Directories                       |
| ------- | ----------------------- | ------------------------------------------ |
| Phase 1 | Core Engine + API       | dq_core/, dq_api/, dq_config/              |
| Phase 2 | Admin, Reporting, RBAC  | dq_admin/, dq_security/                    |
| Phase 3 | DSL & Testing           | dq_dsl/, dq_tests/                         |
| Phase 4 | Cloud Integration       | dq_integration/azure_blob/, infra/azure/   |
| Phase 5 | Governance & Compliance | docs/SECURITY_GUIDE.md, docs/RBAC_MODEL.md |

---

## 7. Summary

## 8. Summary

- End-to-end enterprise security and compliance alignment for Azure.
- Modular, scalable architecture supporting rule management, API integration, and multi-tenancy.
- Dedicated documentation and infrastructure layers for security and cloud deployment.
- Foundation for future expansions such as DSL, testing frameworks, and ML-based rule optimization.
