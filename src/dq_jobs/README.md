# dq_jobs Module (planned)

Registry and API-facing models for JobDefinitions/Checkpoints.

- Captures how a tenant wants to run a data quality job against an existing `DataContract`.
- References `DataContractRef`, `DatasetContract`, and `ActionProfileRef` objects; never embeds raw rules or schemas.
- Stores trigger semantics (manual, scheduled, external event) plus metadata like severity thresholds, idempotency scopes, and lifecycle state.
- Used by `dq_api` job managers and external orchestrators to fetch consistent execution plans before invoking cleansing/profiling/validation pipelines.
