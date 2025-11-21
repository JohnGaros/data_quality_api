# dq_metadata Module

## Purpose
- Captures governance metadata: data assets, validation jobs, rule versions, audit events, and compliance tags.
- Provides APIs for querying lineage and producing evidence packs for auditors.

## Key files
- `models.py`: Pydantic models describing each metadata entity.
- `registry.py`: service layer for storing and retrieving metadata (pluggable backend).
- `lineage.py`: helpers to connect jobs, rules, and datasets.
- `compliance.py`: retention and classification utilities.
- `events.py`: standard event payloads emitted by other modules.

## Notes
- Any workflow that affects customers or compliance should emit metadata through this module.
- Coordinate with governance stakeholders when extending classifications or evidence outputs.
