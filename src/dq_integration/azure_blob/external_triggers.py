"""Helpers for wiring Azure Blob events and polling into validation workflows.

This module will encapsulate Event Grid handlers, webhook adapters, or polling loops
once the programme selects the preferred orchestration pattern for decoupled uploads.
"""

# Future ideas:
# - `def handle_event_grid_notification(event: dict) -> None`
# - `def poll_for_ready_blobs(interval_seconds: int) -> None`
# - Shared utilities for normalising blob metadata sent to the DQ API.
