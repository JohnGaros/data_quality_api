# Notification Adapters

## Purpose
- Sends alerts and status updates to people and systems when validation jobs finish or issues arise.

## Modules
- `email_notifier.py`: handles email templates and delivery.
- `webhook_notifier.py`: posts JSON payloads to external services.
- `ms_teams_notifier.py`: integrates with Microsoft Teams channels.

## How to use
- Choose the adapter that matches the stakeholder’s preferred communication channel.
- Configure notification preferences via API endpoints (`/notifications/...`) for fine-grained control.

