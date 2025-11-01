# dq_security Module

## Purpose
- Implements enterprise security patterns for the platform.
- Integrates with Azure Active Directory, Key Vault, and logging pipelines.

## Key files
- `auth_provider.py`: handles authentication and token validation.
- `rbac_middleware.py`: enforces role-based access on API requests.
- `keyvault_client.py`: retrieves secrets securely.
- `encryption_utils.py`: shared helpers for protecting data at rest.
- `audit_logger.py`: forwards security events to monitoring systems.

## Guidance
- Coordinate changes here with security architects and compliance leads.
- Ensure new endpoints or services leverage these helpers rather than rolling their own security checks.

