# dq_admin Module

## Purpose
- Handles tenant onboarding, role assignments, and user lifecycle tasks.
- Works with the metadata layer to log all privileged actions.

## Key components
- `tenant_manager.py`: create, update, or suspend customer tenants.
- `user_manager.py`: manage platform users and API tokens.
- `rbac.py`: defines role-based permissions (Uploader, Configurator, Admin).
- `audit_log.py`: captures admin activity for compliance reporting.

## When to engage
- During tenant setup or when modifying access policies.
- While preparing governance reports that require admin action history.

