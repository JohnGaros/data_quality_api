"""Placeholder routes for registering externally uploaded files.

This module will expose endpoints that accept Azure Blob references once the
organisation finalises the upload orchestration mechanism (event, webhook, or polling).
For now it serves as a marker so routing and dependency wiring stay modular.
"""

# TODO: Implement FastAPI router that receives blob metadata (URI, ETag, tenant context)
#       and enqueues validation jobs when the decoupled upload design is approved.
