# dq_integration.actions (planned)

Runtime executors for ActionProfiles referenced by JobDefinitions.

- Maps `ActionType` values (notifications, lineage, webhooks, tickets, storage exports, etc.) to concrete adapters implemented elsewhere in `dq_integration`.
- Provides an ActionExecutor interface that receives job metadata/results plus action parameters and emits success/failure details back to `dq_metadata`.
- Ensures post-job side effects are executed consistently after cleansing/profiling/validation complete, without duplicating logic per action consumer.
