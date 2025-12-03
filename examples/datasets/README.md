# Example Datasets for Catalog Design

This directory contains example datasets used to inform the semantic data catalog design.

## Directory Structure

```
datasets/
├── bronze/                  # Raw ingestion layer (customer-provided files)
│   ├── accounting/          # GL, AP, AR, journal entries
│   ├── crm/                 # Contacts, interactions, campaigns
│   └── erp/                 # Orders, inventory, master data
├── ddl/
│   └── postgres/            # DDL for silver/gold layer tables
├── silver/                  # (Optional) Cleansed/enriched samples
└── gold/                    # (Optional) Reporting-ready samples
```

## What to Add

### Bronze Layer (Flat Files)

- Excel (.xlsx) or CSV exports from source systems
- Can be anonymized/synthetic data
- Include headers — column names are critical for catalog mapping

**Examples:**

- `accounting/ar_aging.csv` — Accounts Receivable aging report
- `accounting/gl_journal.xlsx` — General Ledger journal entries
- `crm/contacts.csv` — Customer contact records
- `erp/sales_orders.csv` — Sales order history

### DDL (Postgres)

- `CREATE TABLE` statements for silver and gold layer schemas
- Include column comments if available
- Can be exported via `pg_dump --schema-only`

**Examples:**

- `postgres/silver_customer.sql` — Unified customer table DDL
- `postgres/gold_credit_kpis.sql` — Credit KPI view/table DDL

## Notes

| File                        | Source System | Business Domain | Notes |
| --------------------------- | ------------- | --------------- | ----- |
| _Add rows as you add files_ |               |                 |       |

## Usage

Once populated, run catalog analysis to generate draft YAML definitions:

```bash
# Future: python scripts/analyze_datasets.py
```
