# dq_core Module

## Purpose
- Provides the validation engine and core data models that power the platform.
- Evaluates rules, builds reports, and ensures business logic is applied consistently.

## Structure
- `models/`: Pydantic definitions for rules, logical fields, mappings, and customer profiles.
- `engine/`: Rule evaluation logic, expression helpers, and runtime orchestration.
- `report/`: Classes that shape validation results and export formats.

## Why it matters
- Any change here affects how data quality is judged; coordinate closely with stakeholders.
- Extensive testing is required when adjusting rule execution or report calculations.

