# dq_core.models

## Purpose

- Defines the structured data objects used throughout the platform (rules, logical fields, mappings, customers).

## Highlights

- Pydantic models enforce consistent validation across API, engine, and storage layers.
- Changes here ripple into configuration files and APIs, so review carefully.

## Usage tips

- Add fields only after confirming they are reflected in configuration templates and metadata tracking.
- Keep model descriptions updated to help non-technical reviewers understand what each field means.
