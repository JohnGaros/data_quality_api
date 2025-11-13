# Data Quality Assessment API (DQ API)

## What this project is about
- Central service that checks customer data files against shared business rules.
- Supports multiple customers (tenants) with different file layouts.
- Keeps full audit history so governance and compliance teams have evidence when needed.
- Designed to handle both direct file uploads and future externalised blob uploads (event, webhook, or polling trigger still pending a final decision).

## How the repo is organised
- `docs/` — plain-language specs and guides for product, security, and operations.
- `src/` — application code split into clear modules (API, rule engine, admin, metadata, etc.).
- `configs/` — sample configuration files, rule templates, and environment settings.
- `infra/` — deployment assets for Azure, Kubernetes, and CI/CD pipelines.
- `tests/` — automated checks to prove the platform works as expected.
- `scripts/` — helper scripts for local setup, data seeding, and maintenance.

### dq_profiling module
- `src/dq_profiling/models/` contains Pydantic models for profiling jobs, results, and per-field snapshots so profiling metadata stays consistent across the API and metadata layers.
- `src/dq_profiling/engine/` hosts the `ProfilingEngine` that computes dataset statistics plus the `ProfilingContextBuilder` that converts snapshots into rule-engine-ready contexts.
- `src/dq_profiling/api/` keeps placeholder routers for future profiling-specific endpoints (e.g., proactive profiling or reruns independent of validation).
- `dq_core.engine` uses these interfaces instead of rolling its own helpers, keeping profiling responsibilities encapsulated.

## Who should read this
- Product managers tracking scope and delivery.
- Technical leads coordinating build tasks.
- Compliance or governance partners reviewing controls.

## How to get started
1. Read the Business Requirements Document (`docs/BRD.md`) for the big picture.
2. Review functional and non-functional requirements to understand what must be built.
3. Follow the docs in `infra/` and `scripts/` when you are ready to run or deploy the service.
4. If you are evaluating decoupled uploads, review `configs/external_upload.example.yaml` and the notes in `docs/ARCHITECTURE_FILE_STRUCTURE.md` for integration guidance.
