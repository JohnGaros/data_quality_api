# API Routes

## Purpose
- Holds the FastAPI endpoint definitions that users call.
- Organised by feature set so teams can find related routes quickly.

## Typical files
- `uploads.py`: file submission and job status queries.
- `external_uploads.py`: placeholder for accepting blob references from external upload orchestrators once the decision lands.
- `rules.py`: configuration operations for rule libraries (validation, profiling, cleansing namespaces).
- `tenants.py`: tenant management endpoints.
- `auth.py`: authentication helpers.
- `health.py`: lightweight health check for monitoring.

## Tips
- Keep route names and responses in sync with `docs/API_CONTRACTS.md`.
- Add docstrings and examples to help non-technical reviewers follow the flow.
