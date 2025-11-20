# Rule Libraries

Author and store rule templates outside `configs/` to keep environment settings separate from governance-managed rule catalogs.

- `validation_rules/`: Validation rule templates (YAML/JSON/Excel).
- `profiling_rules/`: Profiling expectations (YAML/JSON/Excel).
- `cleansing_rules/`: Cleansing rule templates (YAML/JSON/Excel).

Load via `dq_config.loader.load_<type>_rules` or `load_rules_from_file` (which infers rule type from these folder names).
