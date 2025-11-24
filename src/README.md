# Source Code Overview

## Purpose

- Contains all runtime code for the Data Quality Assessment API.
- Organised into modular packages so teams can work independently.

## Module summary

- `dq_api/`: REST endpoints and supporting services.
- `dq_core/`: Validation engine, rule models, and reporting utilities.
- `rule_libraries/`: Authoring layer for validation/profiling/cleansing rule templates authored in YAML/JSON/Excel.
- `dq_contracts/`: Registry layer for contract and rule models persisted as canonical JSON.
- `dq_catalog/`: Semantic catalog of entities/attributes that contracts map into.
- `dq_admin/`: Tenant, user, and RBAC management helpers.
- `dq_metadata/`: Governance metadata capture and lineage utilities.
- `dq_integration/`: Connectors for Azure storage, Power Platform, and notifications.
- `dq_security/`: Authentication, key management, and audit logging.
- `dq_tests/`: Framework for rule regression testing (future expansion).
- `dq_dsl/`: Early work on the rule domain-specific language.
- `test_data/`: Sample files used for development and automated tests.

## Guidance for non-technical readers

- Skim package `README` files for more detail before diving into code.
- Use this structure to plan which team or agent owns each workstream.
