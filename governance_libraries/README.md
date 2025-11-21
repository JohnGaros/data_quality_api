# Governance Libraries

Author governance profiles (PII classifications, retention, access policies, legal tags) in YAML/JSON/Excel.

- Profiles are referenced by data contracts via `GovernanceProfileRef`.
- Canonical JSON is persisted in the registry for auditability and enforcement by engines and downstream systems.

Future loaders/validators will ensure policy structure and tagging consistency across tenants and environments.
