# Governance Libraries

Author governance profiles (PII classifications, GDPR-related tags, retention, access policies, legal tags) in YAML/JSON/Excel.

- Profiles are referenced by data contracts via `GovernanceProfileRef`.
- Canonical JSON is persisted in the registry for auditability and enforcement by engines and downstream systems, including GDPR obligations (lawful basis tracking, data subject rights support, special category data handling).

Future loaders/validators will ensure policy structure and tagging consistency across tenants and environments, and validate that GDPR-specific fields (lawful basis, supported rights, retention rules) are populated where required.
