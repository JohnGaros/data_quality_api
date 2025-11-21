# dq_contracts Module

## Purpose

- Defines the data contract models that describe datasets, columns, rule templates, and bindings.
- Acts as the registry layer for persisting canonical JSON representations to Postgres JSONB and exposing them to APIs and engines.

## Key files

- `models.py`: Pydantic models for `DataContract`, `DatasetContract`, `ColumnContract`, `RuleTemplate`, `RuleBinding`, and lifecycle metadata.
- `serialization.py`: Provides `to_canonical_json` so the same JSON structure is used for DB persistence, API responses, and downstream services.
- `registry.py`: Stub showing how contracts, rule templates, and bindings can be normalised and written to JSONB-backed tables (inject your DB writer).
- `__init__.py`: Convenience exports for other modules.

## Notes

- File/YAML/Excel authoring lives in `rule_libraries/`; this module consumes those models and stores/exposes canonical JSON.
- Extend `ContractRegistry` with your database implementation when wiring Postgres persistence.
