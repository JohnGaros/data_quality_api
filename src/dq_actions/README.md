# dq_actions Module (planned)

Runtime registry and models for ActionProfiles loaded from `action_libraries/`.

- Stores canonical JSON ActionProfiles in Postgres JSONB (tenant + environment scoped).
- Exposes Pydantic models such as `ActionType`, `ActionConfig`, `ActionProfile`, and `ActionProfileRef`.
- Provides lookup helpers so `dq_api` job managers and `dq_integration` executors can resolve which actions to run after a job completes.
- Mirrors patterns used in `dq_contracts` (authoring → loaders → canonical JSON → registry/repository).
