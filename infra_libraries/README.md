# Infra Libraries

Author reusable infrastructure profiles (storage, compute, retention, deployment hints) in YAML/JSON/Excel.

- Profiles are referenced by data contracts via `InfraProfileRef`.
- Profiles are intended to be stored as canonical JSON in the registry and used by IaC/deployment pipelines.

Loaders/validators are planned; keep authoring declarative so platform teams can manage infra policies independently of rule/contract authoring.
