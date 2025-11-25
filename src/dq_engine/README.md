# dq_engine — Execution Engine Abstraction

`dq_engine` defines backend-agnostic interfaces so cleansing, profiling, and validation can run on different execution backends (Pandas now; Spark/SQL later) without changing orchestration or introducing new configuration sources.

## Components

- `base.py` — `ExecutionEngine` interface and `DatasetHandle` protocol.
- `pandas_engine.py` — Default pandas-backed implementation (stubbed operations with TODOs to delegate to `dq_cleansing`, `dq_profiling`, `dq_core`, and `dq_integration`).
- `spark_engine.py` — Placeholder for future Spark/SQL backends selected via infra profiles.

## Usage (today)

```python
from dq_engine.pandas_engine import PandasExecutionEngine
from dq_cleansing.engine.cleansing_engine import CleansingEngine

engine = PandasExecutionEngine()
cleansing = CleansingEngine(execution_engine=engine)  # defaults to pandas if omitted
```

Backend choice is expected to be driven by DataContracts and infra profiles; engines themselves do not store configuration or tenant/env context. See `docs/EXECUTION_ENGINES.md` for design notes and roadmap.
