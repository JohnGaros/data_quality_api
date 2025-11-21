# dq_catalog Module

Semantic data catalog (canonical entities/attributes/relationships) that contracts map into.

- `models.py`: Pydantic models for `CatalogEntity`, `CatalogAttribute`, and `CatalogRelationship`.
- Future: repository/API/loader stubs to persist and query catalog entries from Postgres.

Contracts reference catalog entity/attribute IDs so producer-specific feeds can be aligned to a shared semantic layer.
