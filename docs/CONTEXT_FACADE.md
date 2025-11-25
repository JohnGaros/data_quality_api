# Runtime SDK & Context Facade (`dq_sdk`)

`DQContext` is a thin runtime facade that orchestrates contract-driven cleansing → profiling → validation flows. It is intended for notebooks, ad-hoc scripts, CLI tools, tests, and orchestration adapters (Airflow/ADF). The context reads configuration from the canonical sources — **DataContracts + orthogonal libraries + semantic catalog** — and never introduces new configuration.

## Goals

- Provide a Pythonic entrypoint for running contract-driven jobs without re-implementing orchestration in every consumer.
- Resolve contracts/job definitions for a given tenant + environment and pass that metadata into the engines.
- Offer a consistent sequence: upload (via infra profiles) → cleansing → profiling → validation → metadata recording.
- Remain safe to import even while `dq_jobs`, blob adapters, and metadata registries are still under development.

## Non-goals

- Persisting or overriding rules, schemas, infra, or governance outside the contract/library/catalog sources.
- Becoming a fifth orthogonal library; it is a runtime SDK, not a configuration store.
- Bypassing registries/approvals — wiring intentionally routes through `dq_contracts`, `dq_jobs`, `dq_metadata`, and `dq_integration` once available.

## Current shape (early stub)

The initial implementation in `src/dq_sdk/context.py` exposes:

- `run_validation_on_file(dataset_type, local_path, job_definition_id=None, extra_metadata=None)` — orchestrates the end-to-end flow for local files.
- `run_job_definition(job_definition_id, batch_ref, extra_metadata=None)` — executes a JobDefinition/Checkpoint by ID.
- `list_contracts(dataset_type=None)` and `list_job_definitions(tags=None)` — discovery helpers.
- `dry_run_job(...)` — reserved for sandboxed/dry-run execution once engines support it.

Where underlying registries or adapters are not yet implemented, methods raise `NotImplementedError` with doc references (e.g., `docs/CONTRACT_DRIVEN_ARCHITECTURE.md`, `docs/ACTIONS_AND_JOB_DEFINITIONS.md`).

## Usage patterns (pseudo-code)

```python
from dq_sdk import DQContext

# Notebook / ad-hoc validation against a local file
ctx = DQContext(tenant="tenant-a", env="dev")
result = ctx.run_validation_on_file(
    dataset_type="billing",
    local_path="/tmp/billing.csv",
    extra_metadata={"notebook": "exploration"},
)
print(result.status, result.details)

# Airflow/ADF operator invoking a JobDefinition
ctx = DQContext(tenant="tenant-a", env="prod")
result = ctx.run_job_definition(
    job_definition_id="jobdef-billing-daily",
    batch_ref={"blob_uri": "https://storage/.../billing_2024-04-30.csv"},
)
if result.status != "succeeded":
    raise RuntimeError("DQ job failed")

# CLI / test harness discovery
contracts = ctx.list_contracts(dataset_type="payments")
jobs = ctx.list_job_definitions(tags=["daily"])
```

## Implementation notes

- Import-friendly: optional imports guard against missing modules so the SDK can evolve independently.
- Multi-tenant: every method is scoped by the `tenant` and `env` provided at instantiation.
- Lineage-first: metadata hooks are stubbed now but are expected to write to `dq_metadata` with contract/job IDs once the repository is wired.

Refer to `docs/ARCHITECTURE.md#2.6-runtime-sdk--context-facade` for architectural positioning and to `docs/ACTIONS_AND_JOB_DEFINITIONS.md` for how JobDefinitions link to actions and contracts.
