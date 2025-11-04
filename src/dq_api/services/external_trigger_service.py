"""Coordinator for validation jobs started from external upload triggers.

Future responsibilities:
    - Validate blob metadata supplied by events, webhooks, or polling jobs.
    - Fetch upload context (tenant, config version) from storage adapters.
    - Enqueue profiling-driven validation jobs with appropriate correlation IDs.

Implementation is deferred until the programme chooses an orchestration model.
"""


class ExternalTriggerService:
    """Skeleton interface reserved for future decoupled upload flows."""

    def register_blob(self, blob_uri: str, *, tenant_id: str, etag: str, metadata: dict) -> None:
        """Validate and enqueue a blob-backed validation job.

        Args:
            blob_uri: Azure Blob Storage URL pointing to the uploaded file.
            tenant_id: Tenant identifier aligned with configuration context.
            etag: Integrity token supplied by storage to detect duplicates.
            metadata: Additional trigger metadata (source system, trigger type, etc.).

        Raises:
            NotImplementedError: Until the orchestration mechanism is finalised.
        """
        raise NotImplementedError(
            "External upload orchestration (event/webhook/polling) is pending. "
            "Implementation will be added once the decision is made."
        )
