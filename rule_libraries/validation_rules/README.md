# Validation Rule Templates

Author validation rules as YAML, JSON, or Excel. YAML is preferred for readability and inline comments; Excel remains supported for tabular entry and import.

## Fields
- `rule_id`, `name`, `dataset_type`
- `expression`: boolean expression evaluated by the validation engine
- `severity`: `hard` or `soft`
- `description`, `active_from`, optional `active_to`, `tags`

## Example (YAML)
```yaml
rule_id: dq-billing-net-balance
name: Net amount must equal gross minus tax
dataset_type: billing
expression: NetAmount == GrossAmount - TaxAmount
severity: hard
description: >
  Prevents invoices where net totals drift from the gross/tax components.
active_from: 2024-06-01
```

## Workflow
1. Draft rules in this folder (`*.yaml` / `*.json` / `*.xlsx`).
2. Load via `rule_libraries.loader.load_validation_rules` (or `load_rules_from_file`, which can infer rule type from this path).
3. Validation → Pydantic `ValidationRuleTemplate` → canonical JSON → APIs / Postgres JSONB / engines.
