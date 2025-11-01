# dq_config Module

## Purpose
- Manages how rule and mapping configurations are loaded, validated, versioned, and promoted.
- Bridges the gap between human-friendly templates (Excel/JSON) and runtime models.

## Primary files
- `loader.py`: reads configuration files and converts them into Python models.
- `registry.py`: tracks active and historical configurations.
- `serializers.py`: moves data between APIs, databases, and storage formats.
- `validators.py`: checks for missing fields, duplicates, and expression errors.

## When to interact
- During tenant onboarding or rule updates.
- While designing approval workflows or testing configuration changes in sandbox environments.

