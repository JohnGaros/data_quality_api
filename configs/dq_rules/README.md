# Rule Templates Folder

## What lives here
- Example rule libraries and mapping templates used to validate customer data.
- Files are usually Excel or JSON so configuration teams can edit them without coding.

## Why it matters
- These templates drive the behaviour of the validation engine.
- Version control in this folder helps us track what changed, when, and by whom.

## How to use
- Create drafts in a sandbox branch.
- Coordinate approvals with the governance team before promoting changes to production.
- Link each file to the corresponding tenant and configuration version in the metadata layer.

## Example template (JSON)
```json
{
  "rule_id": "dq-billing-net-balance",
  "name": "Net amount must equal gross minus tax",
  "dataset_type": "billing",
  "expression": "NetAmount == GrossAmount - TaxAmount",
  "severity": "hard",
  "description": "Prevents invoices where net totals drift from the gross/tax components.",
  "active_from": "2024-06-01"
}
```

Excel-based templates typically contain the same fields in tabular form (columns for `rule_id`, `expression`, `severity`, etc.) so they can be exported to JSON before promotion.
