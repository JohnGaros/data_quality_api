# dq_core.report

## Purpose
- Shapes validation results into clear summaries and exportable formats.
- Supports downstream consumers who need CSV, JSON, or dashboard-ready data.

## Components
- `validation_report.py`: core report structure (counts, failures, metadata).
- `exporters.py`: helpers for generating files or API payloads.

## Practical guidance
- Keep report changes backward compatible, or document version bumps for stakeholders.
- Align report fields with the metadata layer so lineage remains intact.

