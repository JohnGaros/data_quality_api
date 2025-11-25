# dq_sdk — Runtime Context Facade

`dq_sdk` hosts the `DQContext` runtime facade used by notebooks, ad-hoc scripts, orchestration adapters (Airflow/ADF), and CLI/test tools. It orchestrates cleansing → profiling → validation by reading configuration from DataContracts + orthogonal libraries + the semantic catalog; it does **not** store or override configuration.

## Goals

- Provide a Pythonic entrypoint for contract-driven jobs scoped by tenant/environment.
- Resolve contracts/job definitions and delegate to engines/registries (`dq_contracts`, `dq_jobs`, `dq_cleansing`, `dq_profiling`, `dq_core`, `dq_metadata`, `dq_integration`).
- Stay import-safe while underlying registries mature (clear `NotImplementedError` stubs with doc references).

## Usage (pseudo-code)

```python
from dq_sdk import DQContext

ctx = DQContext(tenant="tenant-a", env="dev")
result = ctx.run_validation_on_file(dataset_type="billing", local_path="/tmp/file.csv")
print(result.status, result.details)
```

Job definition execution and dry-run APIs are stubbed until the corresponding registries and adapters are available; see `docs/CONTEXT_FACADE.md` for details.
