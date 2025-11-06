# Cleansing Rule Templates

Store versioned cleansing rule templates in JSON or Excel format. Each template should align with the canonical structure defined in `docs/DATA_MODEL_REFERENCE.md`:

- `rule_id`, `name`, `dataset_type`, `version`
- `transformations`: ordered steps containing `type`, `target_fields`, `parameters`, `severity`, and optional `condition`

Recommended conventions:

1. Use semantic versioning (e.g., `2024.06.01`) to align with promotion workflows.
2. Maintain one folder per tenant or domain when governance requires isolation.
3. Keep accompanying approval evidence (sign-off PDFs, change requests) alongside the template or in metadata references.
4. Regenerate checksum files after edits so automated pipelines can detect unapproved changes.

## Example template (JSON)
```json
{
  "rule_id": "cln-billing-standardise",
  "name": "Billing currency and customer cleanup",
  "dataset_type": "billing",
  "version": "2024.06.01",
  "transformations": [
    {
      "type": "standardize",
      "target_fields": ["Currency"],
      "parameters": {"format": "ISO-4217"}
    },
    {
      "type": "fill_missing",
      "target_fields": ["CustomerId"],
      "parameters": {"default": "UNKNOWN"}
    }
  ]
}
```

Excel equivalents arrange each transformation in rows with columns such as `type`, `target_fields`, `parameters`, and `severity` so governance reviewers can comment inline before exporting to JSON for ingestion.
