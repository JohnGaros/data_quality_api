# Cleansing Rule Templates

Store versioned cleansing rule templates in YAML, JSON, or Excel. YAML is preferred for readability and inline comments.

## Fields
- `rule_id`, `name`, `dataset_type`, `version`
- `transformations`: ordered steps containing `type`, `target_fields`, `parameters`, `severity`, and optional `condition`
- Optional metadata: `description`, `active_from`

Recommended conventions:

1. Use semantic versioning (e.g., `2024.06.01`) to align with promotion workflows.
2. Maintain one folder per tenant or domain when governance requires isolation.
3. Keep accompanying approval evidence (sign-off PDFs, change requests) alongside the template or in metadata references.
4. Regenerate checksum files after edits so automated pipelines can detect unapproved changes.

## Example (YAML)
```yaml
rule_id: billing-standardise
name: Billing standardisation
dataset_type: billing
version: 2024.06.01
description: >
  Normalises currency formatting, fills missing customer identifiers,
  and deduplicates invoices before validation.
active_from: 2024-06-01
transformations:
  - type: standardize
    target_fields: ["Currency"]
    parameters:
      format: ISO-4217
  - type: fill_missing
    target_fields: ["CustomerId"]
    parameters:
      default: UNKNOWN
    severity: soft
  - type: deduplicate
    target_fields: ["InvoiceNumber"]
    parameters:
      keys: ["InvoiceNumber"]
    severity: hard
```

Excel equivalents arrange each transformation in rows with columns such as `type`, `target_fields`, `parameters`, and `severity` so governance reviewers can comment inline before exporting to JSON for ingestion. Load via `rule_libraries.loader.load_cleansing_rules` or `load_rules_from_file` (type inferred from this folder).
