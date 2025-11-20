# Profiling Rule Templates

Profiling rules capture expectations derived from profiling metrics. Author them in YAML/JSON/Excel; YAML is recommended for readability and comments.

## Fields
- `rule_id`, `name`, `dataset_type`
- `field` (optional): target column
- `profile_metric`: e.g., `null_ratio`, `stddev`, `max`, `distinct_count`
- `comparison`: one of `<`, `<=`, `>`, `>=`, `==`
- `threshold`: numeric threshold
- `tolerance` (optional): band around the threshold
- `description`, `active_from`, optional `active_to`, `tags`

## Example (YAML)
```yaml
rule_id: billing-amount-null-threshold
name: Amount null ratio should not exceed 2%
dataset_type: billing
field: Amount
profile_metric: null_ratio
comparison: "<="
threshold: 0.02
description: >
  Flags datasets where the Amount field has too many nulls.
active_from: 2024-06-01
```

## Workflow
1. Draft profiling expectations here.
2. Load via `dq_config.loader.load_profiling_rules` (or `load_rules_from_file`, which infers the type from this folder).
3. Profiling → Pydantic `ProfilingRuleTemplate` → canonical JSON → APIs / metadata / engines.
