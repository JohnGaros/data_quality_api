# API Services

## Purpose
- Centralises business logic that multiple routes share.
- Keeps controllers thin while ensuring consistent behaviour across the API.

## Key components
- `job_manager.py`: orchestrates validation job lifecycle (queueing, monitoring).
- `report_service.py`: prepares validation reports and download links.
- `notification_service.py`: sends emails or webhooks when important events occur.

## Guidance
- When adding new workflows, extend these services so they remain the single source of truth.
- Log significant actions through the metadata layer for auditability.

