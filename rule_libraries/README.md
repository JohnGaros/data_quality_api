# Rule Libraries

Author and store rule templates outside `configs/` to keep environment settings separate from governance-managed rule catalogs.

- `validation_rules/`: Validation rule templates (YAML/JSON/Excel).
- `profiling_rules/`: Profiling expectations (YAML/JSON/Excel).
- `cleansing_rules/`: Cleansing rule templates (YAML/JSON/Excel).
- Mapping templates (when present) that align tenant columns to logical fields.

`rule_libraries` is the **authoring layer**: it parses YAML/JSON/Excel files into Pydantic rule models, performs linting/validation, and normalizes everything into canonical JSON before handing off to the registry layer (`dq_contracts` / Postgres).

Load via `rule_libraries.loader.load_<type>_rules`. `canonical_json`/`to_canonical_json` ensures that authoring format does not affect the resulting JSON stored in the registry or returned by APIs.

### YAML example

```yaml
- rule_id: dq-billing-net-balance
  name: Net amount must equal gross minus tax
  dataset_type: billing
  expression: NetAmount == GrossAmount - TaxAmount
  severity: hard
  description: Prevents invoices where net totals drift from the gross/tax components.
```
