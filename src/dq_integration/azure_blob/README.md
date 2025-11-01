# Azure Blob Integration

## Purpose
- Manages file storage and retrieval in Azure Blob Storage.
- Supports features like secure upload archives, report downloads, and event-driven processing.

## Components
- `blob_client.py`: wraps Azure SDK calls with project defaults.
- `blob_storage_config.py`: central configuration (containers, retention policies).
- `blob_job_adapter.py`: links validation jobs with stored artifacts.

## Guidance
- Work with cloud administrators to configure containers, permissions, and retention.
- Ensure metadata (checksums, URIs) is recorded in the `dq_metadata` layer for lineage.

