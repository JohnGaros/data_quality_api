# dq_api Module

## Purpose
- Exposes the platform through RESTful endpoints built with FastAPI.
- Acts as the entry point for uploads, configuration changes, reporting, and metadata queries.

## Layout
- `routes/`: endpoint definitions grouped by business function.
- `services/`: shared business logic (job orchestration, notifications, reporting).
- `dependencies.py`: dependency injection wiring for FastAPI.
- `middlewares.py`: request logging, authentication, and timing hooks.
- `settings.py`: environment-driven configuration.
- `app_factory.py`: builds the FastAPI application instance.

## Notes for PMs and supervisors
- This module defines the customer-facing contract; changes must stay aligned with `docs/API_CONTRACTS.md`.
- Coordinate with security and metadata teams when adding or modifying endpoints.

