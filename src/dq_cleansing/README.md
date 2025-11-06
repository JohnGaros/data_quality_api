# dq_cleansing module

This package manages the governance, execution, and reporting flows for data cleansing rules.

Key components:

- `models/`: Pydantic models describing cleansing rules, jobs, and execution results.
- `engine/`: Transformation engine that applies ordered steps to datasets and tracks metrics.
- `report/`: Structures for summarising cleansing outcomes and exporting run artefacts.

The module mirrors the layout of the validation engine so cleansing rules can be versioned, approved, and executed independently while still chaining into the validation pipeline when configured.
