# Draft: Semantic Model Authoring

**Created:** 2025-12-03

**Status:** PROMOTED

**Origin:** standalone

**Promoted To:** `specs/milestones/M1_MVP_FOUNDATION/epics/E0_CATALOG_FOUNDATION/features/semantic_model_authoring/`

## Problem Statement

The platform needs a well-designed semantic data catalog that maps raw data fields to business meaning across the data pipeline layers (bronze → silver → gold). Currently:

- Catalog authoring is done via YAML files in `catalog_libraries/`
- The existing `customer_domain.yaml` example doesn't reflect the actual business domains
- No structured approach exists for deriving catalog entities from real datasets
- The primary use case is **advanced search** — users need to find data assets by domain, tenant, layer, or storage type

**Who benefits:**

- Data engineers mapping ingested files to semantic meaning
- Analysts tracing KPIs back to source fields
- Data stewards governing field-level lineage
- Platform operators searching for assets across tenants and layers

## Proposed Approach

### Organizing Principle: Domain-First for Search Optimization

**Revision (2025-12-04):** After analyzing real datasets and considering search as the primary use case, the catalog structure has been revised from layer-first to **domain-first**.

**Rationale:** Users most commonly search by business domain ("find all billing data") rather than by layer ("find all bronze data"). Domain-first organization optimizes for the most frequent query patterns while still supporting layer/tenant filtering.

### Catalog Directory Structure

```
catalog_libraries/
├── {domain}/
│   ├── DOMAIN.yaml                    # Domain definition, owner, description
│   ├── {subdomain}/                   # Optional grouping (can be omitted)
│   │   ├── SUBDOMAIN.yaml             # Subdomain definition
│   │   ├── bronze/
│   │   │   ├── {tenant}/
│   │   │   │   └── {asset}.yaml       # Tenant-specific bronze assets
│   │   │   └── _shared/               # Cross-tenant bronze schemas
│   │   │       └── {asset}.yaml
│   │   ├── silver/
│   │   │   ├── {tenant}/
│   │   │   │   └── {asset}.yaml       # Tenant-specific silver assets
│   │   │   └── _unified/              # Merged cross-tenant silver
│   │   │       └── {asset}.yaml
│   │   └── gold/
│   │       ├── {tenant}/              # Tenant-specific gold (legacy)
│   │       │   └── {asset}.yaml
│   │       └── {asset}.yaml           # Unified gold assets
│   └── {layer}/                       # If no subdomain needed
│       └── ...
```

### Key Conventions

| Convention | Description |
|------------|-------------|
| `_shared/` | Cross-tenant bronze schemas (canonical field definitions) |
| `_unified/` | Merged silver assets combining multiple tenant sources |
| `{tenant}/` | Tenant-isolated assets (e.g., `ng/`, `kordelos/`, `heron/`) |
| Subdomains | Optional — use only when domain has natural subdivisions |
| Filenames | Do not include layer (cannot control bronze filenames) |

### Entity ID Convention

Path becomes entity ID with dots:

```
{domain}.{subdomain?}.{layer}.{tenant|_shared|_unified}.{asset}
```

**Examples:**
- `billing.energy.bronze.heron.billing_export`
- `billing.energy.silver._unified.validated_billing`
- `collections.dunning.gold.dunning_cube`
- `risk.scoring.silver.ng.default_profile`
- `master_data.gold.customer` (no subdomain)

### Search Query Patterns

| Query | Path/ID Pattern |
|-------|-----------------|
| All billing data | `billing.**` or `billing.*` |
| All bronze billing | `billing.*.bronze.**` |
| All NG tenant assets | `**.ng.**` |
| All unified silver | `**.silver._unified.**` |
| Risk scoring (any layer) | `risk.scoring.**` |

### Why Domain-First Works Better

| Concern | Layer-First | Domain-First |
|---------|-------------|--------------|
| "Find all billing" | `bronze/billing/** + silver/billing/** + gold/billing/**` | `billing/**` |
| "Find NG bronze" | `bronze/**/ng/**` | `**/bronze/ng/**` |
| Adding new domain | Create files in 3 directories | Create 1 domain directory |
| Lineage visibility | Scattered across layers | `domain/` shows full journey |

## Key Questions

- [x] What are the primary business domains? → Energy billing, collections, risk, master data
- [x] How should catalog be organized? → **Domain-first** (revised from layer-first)
- [x] What bronze sources are ingested? → Energy billing (Heron, NG), dunnings, accounting (Kordelos)
- [x] What is the gold layer focus? → Scoring cubes, dunning analytics, settlement tracking
- [x] What specific entities exist at each layer? → See "Revised Entity Structure" below
- [x] How do bronze entities transform into silver entities? → Documented with derivation metadata
- [x] What KPIs and model features define the gold layer? → DSO, aging buckets, risk scores, dunning efficiency
- [x] Should subdomains be required? → **No**, optional for domains with natural subdivisions
- [x] How to handle tenant-specific gold assets? → Allow `gold/{tenant}/` for legacy/non-ideal structures
- [x] Should filenames include layer? → **No**, cannot control bronze filenames

## Revised Entity Structure (2025-12-04)

Based on analysis of actual datasets in `examples/datasets/`, the entity structure has been revised to reflect the **energy/utilities credit risk** domain rather than generic accounting.

### Concrete Catalog Structure

```
catalog_libraries/
├── billing/
│   ├── DOMAIN.yaml
│   ├── energy/                        # Subdomain: energy billing
│   │   ├── SUBDOMAIN.yaml
│   │   ├── bronze/
│   │   │   ├── heron/
│   │   │   │   ├── billing_export.yaml
│   │   │   │   └── payments.yaml
│   │   │   └── ng/
│   │   │       └── ledger.yaml
│   │   ├── silver/
│   │   │   └── _unified/
│   │   │       └── validated_billing.yaml
│   │   └── gold/
│   │       └── billing_summary.yaml
│   └── traditional/                   # Subdomain: traditional AR
│       ├── SUBDOMAIN.yaml
│       ├── bronze/
│       │   └── kordelos/
│       │       ├── ar_balances.yaml
│       │       ├── checks.yaml
│       │       └── sales_journal.yaml
│       └── silver/
│           └── _unified/
│               └── ar_validated.yaml
├── collections/
│   ├── DOMAIN.yaml
│   ├── dunning/
│   │   ├── bronze/
│   │   │   └── ng/
│   │   │       └── dunnings_raw.yaml
│   │   ├── silver/
│   │   │   └── ng/
│   │   │       └── dunning_21day.yaml
│   │   └── gold/
│   │       └── dunning_cube.yaml
│   └── settlements/
│       ├── bronze/
│       │   └── ng/
│       │       └── settlements_raw.yaml
│       └── gold/
│           └── settlement_cube.yaml
├── risk/
│   ├── DOMAIN.yaml
│   ├── scoring/
│   │   ├── silver/
│   │   │   └── ng/
│   │   │       ├── default_profile.yaml
│   │   │       └── ml_probabilities.yaml
│   │   └── gold/
│   │       ├── ng/                    # Tenant-specific gold (legacy)
│   │       │   └── account_extras.yaml
│   │       └── scoring_cube.yaml
│   └── survival/
│       └── silver/
│           └── ng/
│               └── survival_predictions.yaml
└── master_data/
    ├── DOMAIN.yaml
    ├── bronze/
    │   └── _shared/
    │       └── customer_import.yaml
    ├── silver/
    │   └── _unified/
    │       └── account_entity.yaml
    └── gold/
        ├── customer.yaml
        ├── account_entities.yaml
        └── address.yaml
```

### Bronze Layer — Raw Ingestion by Tenant

**billing/energy/bronze/heron/billing_export.yaml:**
| Entity ID | Key Attributes | Source |
|-----------|----------------|--------|
| `billing.energy.bronze.heron.billing_export` | customer_name (Επωνυμία), tax_id (ΑΦΜ), contract_account, supply_number, invoice_date, amount_eur, consumption_kwh | heron_sample_billing.csv |

**billing/energy/bronze/heron/payments.yaml:**
| Entity ID | Key Attributes | Source |
|-----------|----------------|--------|
| `billing.energy.bronze.heron.payments` | business_partner_id, contract_account, payment_date, payment_type, amount | heron_sample_payments.csv |

**billing/energy/bronze/ng/ledger.yaml:**
| Entity ID | Key Attributes | Source |
|-----------|----------------|--------|
| `billing.energy.bronze.ng.ledger` | transaction_date, transaction_id, account_entities_key, amount, posting_key, invoice_energy, invoice_energy_kwh | ng_ledger table |

**collections/dunning/bronze/ng/dunnings_raw.yaml:**
| Entity ID | Key Attributes | Source |
|-----------|----------------|--------|
| `collections.dunning.bronze.ng.dunnings_raw` | account_entities_key, action, action_date, dunning_execution, past_due, success | ng_dunnings_raw table |

**billing/traditional/bronze/kordelos/*.yaml:**
| Entity ID | Key Attributes | Source |
|-----------|----------------|--------|
| `billing.traditional.bronze.kordelos.ar_balances` | customer_id, balance_date, amount | ΟΡΙΣΤΙΚΑ ΥΠΟΛΟΙΠΑ ΠΕΛΑΤΩΝ.xlsx |
| `billing.traditional.bronze.kordelos.checks` | check_number, amount, date, status | ΕΠΙΤΑΓΕΣ.xlsx |
| `billing.traditional.bronze.kordelos.sales_journal` | transaction_code, totals | ΗΜΕΡΟΛΟΓΙΟ ΠΩΛΗΣΕΩΝ.xlsx |

### Silver Layer — Cleansed & Enriched

**risk/scoring/silver/ng/default_profile.yaml:**
| Entity ID | Key Attributes | Derived From |
|-----------|----------------|--------------|
| `risk.scoring.silver.ng.default_profile` | account_entities_key, supply_status, risk_level, balance, past_due_balance, oldest_past_due_days, moving_avg_credit_12m | ng326_default table |

**risk/scoring/silver/ng/ml_probabilities.yaml:**
| Entity ID | Key Attributes | Derived From |
|-----------|----------------|--------------|
| `risk.scoring.silver.ng.ml_probabilities` | account_entities_key, snapshot_date, prob_of_disconnection, prob_of_termination, prob_to_pay_settlement, prob_to_answer_call | ng_4_probabilities table |

**risk/survival/silver/ng/survival_predictions.yaml:**
| Entity ID | Key Attributes | Derived From |
|-----------|----------------|--------------|
| `risk.survival.silver.ng.survival_predictions` | account_entities_key, expected_survival_months, survival_prob_3m, survival_prob_6m, survival_prob_12m, survival_prob_24m | ng326_survival_predictions table |

**collections/dunning/silver/ng/dunning_21day.yaml:**
| Entity ID | Key Attributes | Derived From |
|-----------|----------------|--------------|
| `collections.dunning.silver.ng.dunning_21day` | account_entities_key, due_date, pay_first_response_delay, dunning_efficiency, paid_amount | Derived from dunnings_raw + payments |

### Gold Layer — Analytics Cubes

**master_data/gold/customer.yaml:**
| Entity ID | Key Attributes | Business Definition |
|-----------|----------------|---------------------|
| `master_data.gold.customer` | customer_key, name, vat_number, payment_terms, first_transaction_date, last_transaction_date | Master customer record |

**master_data/gold/account_entities.yaml:**
| Entity ID | Key Attributes | Business Definition |
|-----------|----------------|---------------------|
| `master_data.gold.account_entities` | account_entities_key, customer_id, customer_key, first_transaction_date, payment_terms | Account-level analysis unit |

**risk/scoring/gold/scoring_cube.yaml:**
| Entity ID | Key Attributes | Business Definition |
|-----------|----------------|---------------------|
| `risk.scoring.gold.scoring_cube` | account_entities_key, snapshot_date, balance, dso, risk_level, aging buckets (0-30, 30-60, ..., 365+), settlement metrics, dunning efficiency | Full credit scoring materialized view |

**collections/dunning/gold/dunning_cube.yaml:**
| Entity ID | Key Attributes | Business Definition |
|-----------|----------------|---------------------|
| `collections.dunning.gold.dunning_cube` | dunning_id, action, action_date, amount, dunning_efficiency, total_profit, balance_before, balance_after | Dunning action ROI analysis |

**collections/settlements/gold/settlement_cube.yaml:**
| Entity ID | Key Attributes | Business Definition |
|-----------|----------------|---------------------|
| `collections.settlements.gold.settlement_cube` | settlement_id, total_amount, recovered_amount, recovered_amount_perc, status, installments | Settlement success tracking |

**risk/scoring/gold/ng/account_extras.yaml (tenant-specific legacy):**
| Entity ID | Key Attributes | Notes |
|-----------|----------------|-------|
| `risk.scoring.gold.ng.account_extras` | account_entities_key, class, region, supply_status, tariff_type, customer_category | Tenant-specific gold (non-ideal design) |

### Storage Metadata (in asset YAML)

Storage location is metadata on each asset, not part of the path:

```yaml
# billing/energy/bronze/heron/billing_export.yaml
entity_id: "billing.energy.bronze.heron.billing_export"
domain: "billing"
subdomain: "energy"
layer: "bronze"
tenant: "heron"
storage:
  type: "blob"
  container: "heron-bronze"
  path_pattern: "billing/*.csv"
  format: "csv"
  encoding: "utf-8"
field_mappings:
  customer_name: "Επωνυμία"
  tax_id: "ΑΦΜ"
  contract_account: "Contract Account"
```

### Cross-Cutting Concerns

**Audit attributes** (defined as reusable patterns, not separate entities):
| Attribute Pattern | Purpose |
|-------------------|---------|
| `_source_system` | Origin system identifier |
| `_source_file` | Bronze file/batch reference |
| `_ingested_at` | Timestamp of bronze ingestion |
| `_processed_at` | Timestamp of silver/gold processing |
| `migration_id` | ETL batch identifier |
| `migration_remarks` | ETL notes |
| `migration_date` | ETL timestamp |

**Cross-references** are tracked via relationships in entity definitions:
```yaml
relationships:
  - type: "derived_from"
    target: "billing.energy.bronze.ng.ledger"
  - type: "joins_to"
    target: "master_data.gold.customer"
    join_key: "customer_id"
```

## Research Notes

### Existing Code Analysis

| Component   | Location                       | Status                                                         |
| ----------- | ------------------------------ | -------------------------------------------------------------- |
| Models      | `src/dq_catalog/models.py`     | Complete: CatalogEntity, CatalogAttribute, CatalogRelationship |
| YAML Loader | `src/dq_catalog/loader.py`     | Complete: loads from `catalog_libraries/`                      |
| Repository  | `src/dq_catalog/repository.py` | Complete: in-memory with attribute index                       |
| GET API     | `src/dq_api/routes/catalog.py` | Complete: list/get entities                                    |
| POST API    | `src/dq_api/routes/catalog.py` | Basic: lacks validation, audit trail                           |
| Seeding     | `scripts/seed_catalog.py`      | Complete: loads directory into repository                      |

### Current Gaps

1. **No version management** — POST overwrites; doesn't enforce append-only versioning
2. **No validation on create** — Can create entities with duplicate attribute IDs
3. **No deprecation workflow** — Fields exist but no API support
4. **No relationship management** — CatalogRelationship model not exposed
5. **No audit trail** — Who changed what when?
6. **No bulk import** — Excel/CSV for business users

### Dependencies

- Contracts reference catalog entities via `catalog_entity_ids` and `catalog_attribute_id`
- Validation rules should map to catalog attributes for lineage
- Governance profiles (PII, GDPR) attach to catalog attributes

## Technical Considerations

### Architecture Impact

- Restructuring `catalog_libraries/` from domain-centric to layer-centric
- Existing `customer_domain.yaml` will be replaced/reorganized
- No code changes needed — just YAML reorganization

### Dataset Analysis Approach

Example datasets added to:

```
examples/datasets/
├── bronze/
│   ├── accounting/    # AR, AP, GL exports
│   ├── crm/           # Contact records
│   └── erp/           # Orders, inventory
├── ddl/
│   └── postgres/      # Silver/gold table DDL
├── silver/
└── gold/
```

### Next Steps

1. User adds example datasets to `examples/datasets/`
2. Analyze fields and propose entity/attribute definitions
3. Draft YAML catalog files organized by layer
4. Validate against contract and rule requirements

## Promotion Criteria

Before promoting to epic/feature, verify:

- [x] Problem clearly defined
- [x] Approach validated (layer-first organization)
- [x] Key questions answered
- [x] Target epic/feature identified → E0_CATALOG_FOUNDATION
- [x] Dependencies understood
- [ ] No blocking concerns → Need sample data to validate entity definitions

## Brainstorm Session Summary

### Session: 2025-12-03 (Initial)

**Key Insights:**

1. Layer-first organization (bronze/silver/gold) matches team communication patterns
2. Bronze covers 4 source types: accounting, CRM, ERP, custom flat files
3. Gold layer focuses on credit risk KPIs + customer metrics
4. 23 total entities defined across layers (11 bronze, 7 silver, 5 gold)
5. Cross-cutting concerns (identifiers, audit) handled separately

**Decisions Made:**

- Catalog structure: `catalog_libraries/bronze|silver|gold/` not domain-first
- Entity naming: `<layer>.<domain>_<entity>` (e.g., `bronze.ar_aging`)
- Audit attributes: prefixed with `_` (e.g., `_source_system`, `_ingested_at`)

**Action Items:**

- [x] Add sample datasets to `examples/datasets/bronze/`
- [ ] ~~Draft accounting.yaml with ar_aging entity~~ (superseded by domain-first)
- [ ] ~~Draft kpis.yaml with customer_dso entity~~ (superseded by domain-first)
- [ ] Validate contract → catalog entity reference workflow

**Files Explored:**

- `src/dq_catalog/models.py` — CatalogEntity, CatalogAttribute models
- `src/dq_catalog/loader.py` — YAML loading from catalog_libraries/
- `src/dq_catalog/repository.py` — In-memory repository with attribute index
- `catalog_libraries/customer_domain.yaml` — Existing example (to be replaced)

---

### Session: 2025-12-04 (Revision)

**Key Insights:**

1. **Domain-first organization** optimizes for advanced search (primary use case)
2. Actual data is **energy/utilities credit risk**, not generic accounting
3. Real tenants: NG (natural gas), Heron (energy billing), Kordelos (traditional AR)
4. Bronze has Greek field names requiring canonical mappings
5. Tenant-specific gold assets exist (legacy design) — accommodate with `gold/{tenant}/`
6. Storage type should be **metadata**, not path component

**Major Revision: Layer-First → Domain-First**

The organizing principle changed from layer-first to domain-first based on:
- Search queries most commonly start with domain ("find billing data")
- Lineage is clearer when domain directory shows bronze → silver → gold journey
- Adding new domains requires fewer file changes

**Decisions Made:**

| Decision | Rationale |
|----------|-----------|
| Domain at top level | Optimizes most common search pattern |
| Subdomains optional | Not all domains need subdivision |
| `_shared/` for cross-tenant bronze | Canonical schemas for validation |
| `_unified/` for merged silver | Clear naming for cross-tenant merge |
| `gold/{tenant}/` allowed | Accommodate legacy tenant-specific gold |
| Storage as metadata | Decouples physical from logical |
| Filenames exclude layer | Cannot control bronze filenames |

**Entity ID Convention:**

```
{domain}.{subdomain?}.{layer}.{tenant|_shared|_unified}.{asset}
```

Examples:
- `billing.energy.bronze.heron.billing_export`
- `risk.scoring.silver.ng.default_profile`
- `collections.dunning.gold.dunning_cube`
- `master_data.gold.customer`

**Domains Identified:**

| Domain | Subdomains | Description |
|--------|------------|-------------|
| `billing` | `energy`, `traditional` | Invoice and consumption data |
| `collections` | `dunning`, `settlements` | Debt collection activities |
| `risk` | `scoring`, `survival` | Credit risk and predictions |
| `master_data` | — | Customer, account, address |

**Action Items:**

- [ ] Update IMPLEMENTATION.md with domain-first structure
- [ ] Update TASKS.md with revised entity list
- [ ] Create DOMAIN.yaml template
- [ ] Draft first domain: `billing/energy/` with Heron and NG entities
- [ ] Update `src/dq_catalog/loader.py` if needed for new structure

**Files Explored:**

- `examples/datasets/bronze/heron/heron_sample_billing.csv` — Greek field names
- `examples/datasets/bronze/heron/heron_sample_payments.csv` — Payment transactions
- `examples/datasets/bronze/natural_gas/ng_dunnings_raw.sql` — Dunning DDL
- `examples/datasets/gold/ng_scoring_cube.sql` — Complex materialized view
- `examples/datasets/silver/ng326_default.sql` — Risk scoring silver
- `examples/datasets/silver/ng_4_probabilities.sql` — ML predictions
- `examples/datasets/gold/we_customer.sql`, `we_account_entities.sql` — Master data

## Session History

| Date       | Activity         | Outcome                                                           |
| ---------- | ---------------- | ----------------------------------------------------------------- |
| 2025-12-03 | Created          | Initial brainstorm on semantic model authoring                    |
| 2025-12-03 | Refined          | Decided on layer-first organization (bronze/silver/gold)          |
| 2025-12-03 | Setup            | Created `examples/datasets/` structure for sample data            |
| 2025-12-03 | Entity design    | Drafted full entity structure for bronze/silver/gold layers       |
| 2025-12-03 | Session saved    | Brainstorm session summary added                                  |
| 2025-12-04 | Sample data      | Analyzed actual datasets: Heron, NG, Kordelos                     |
| 2025-12-04 | **Major revision** | Changed from layer-first to **domain-first** for search optimization |
| 2025-12-04 | Entities revised | Mapped real data to new domain structure                          |
| 2025-12-04 | Session saved    | Updated draft with domain-first approach                          |
| 2025-12-05 | **Domain expansion** | Expanded from 4 to 8 domains based on new sample data analysis |
| 2025-12-05 | Session saved    | Updated draft with 8-domain structure                             |

---

### Session: 2025-12-05 (Domain Expansion)

**Key Insights:**

1. **payments** is semantically distinct from billing (money IN vs charges OUT) — should be top-level domain
2. **ledger** may be ingested as ledger format at bronze layer — should be top-level domain
3. **balance** is critical for balance reconciliation validation rule — new domain
4. **mitigants** (guarantees, collateral) need dedicated tracking — new domain
5. **risk → kpis**: Platform calculates many KPIs beyond risk; calculated balance is also a KPI
6. **checks** are a payment instrument — use generic `instruments` subdomain under payments
7. New tenants discovered: helpe, mrhealth_jordan, terna_energy (deferred to Phase 2)

**Major Revision: 4 Domains → 8 Domains**

The domain structure expanded from 4 to 8 domains based on analysis of new sample datasets and semantic separation of concerns:

| Previous (4 domains) | Revised (8 domains) |
|---------------------|---------------------|
| billing | billing (invoices only) |
| — | payments (new - money received) |
| — | ledger (new - unified transactions) |
| — | balance (new - point-in-time snapshots) |
| collections | collections (unchanged) |
| — | mitigants (new - guarantees, collateral) |
| risk | kpis (renamed - broader scope) |
| master_data | master_data (expanded with supply_number) |

**Decisions Made:**

| Decision | Rationale |
|----------|-----------|
| payments as top-level domain | Semantically distinct from billing (money IN vs charges OUT) |
| ledger as top-level domain | May be ingested as ledger format at bronze layer |
| balance as new domain | Critical for balance reconciliation validation rule |
| mitigants as new domain | Guarantees and credit risk instruments need dedicated tracking |
| payments/instruments subdomain | More generic than "checks" — could include other payment instruments |
| risk → kpis | Platform calculates many KPIs beyond risk; calculated balance is also a KPI |
| Phase 1: heron + ng only | Core tenants first; helpe, mrhealth_jordan, terna_energy in Phase 2 |

**Balance Reconciliation Rule:**

A critical validation rule the platform will implement:

```
For every identity subject (customer/account/meter):
ending_balance = starting_balance + SUM(billing) - SUM(payments)
```

| Layer | Purpose |
|-------|---------|
| bronze | Raw balance snapshots from source systems |
| silver | Calculated balance = starting_balance + ledger transactions |
| gold | Reconciled balance with variance analysis |

**Final 8-Domain Structure:**

```
catalog_libraries/
├── billing/          # Charges TO customer (invoices, debits)
├── payments/         # Money FROM customer (credits, instruments)
├── ledger/           # Unified transaction history (double-entry)
├── balance/          # Point-in-time balance snapshots
├── collections/      # Debt collection (dunning, settlements)
├── mitigants/        # Credit risk mitigation (guarantees, collateral)
├── kpis/             # Calculated metrics & model predictions
└── master_data/      # Reference entities (customer, account, supply_number, address)
```

**Entity Count Summary (Phase 1 - heron + ng):**

| Domain | Subdomains | Bronze | Silver | Gold | Total |
|--------|------------|--------|--------|------|-------|
| billing | energy | 2 | 1 | 1 | 4 |
| payments | cash, instruments | 2 | 1 | 0 | 3 |
| ledger | energy | 2 | 1 | 0 | 3 |
| balance | energy | 1 | 1 | 1 | 3 |
| collections | dunning, settlements | 4 | 1 | 2 | 7 |
| mitigants | guarantees | 1 | 1 | 0 | 2 |
| kpis | scoring, survival | 0 | 3 | 2 | 5 |
| master_data | customer, account, supply_number, address | 5 | 1 | 3 | 9 |
| **Total** | 12 | 17 | 10 | 9 | **~36** |

**Files Analyzed:**

Bronze CSV:
- `heron/heron_sample_billing.csv` (invoices)
- `heron/heron_sample_payments.csv` (payments)
- `heron/Settlements till 01.04.2024_corrected.csv` (settlements)
- `natural_gas/b2c_transactions.csv` (ledger - 277MB)
- `natural_gas/b2b_transactions.csv` (ledger)
- `natural_gas/b2c_dunning.csv` (dunning)
- `natural_gas/b2c_supply_number.csv` (master data)
- `natural_gas/b2b_supply_number.csv` (master data)

Bronze Excel (Phase 2):
- `kordelos/ar_balances` (balance)
- `kordelos/checks` (instruments)
- `kordelos/sales_journal` (ledger)
- `mrhealth_jordan/*` (ledger, payments, balance)
- `helpe/*` (snapshot, customer, mitigants)
- `terna_energy/*` (ledger)

Silver/Gold SQL:
- `ng_ledger.sql` (ledger)
- `ng326_default.sql` (kpis - default profile)
- `ng_4_probabilities.sql` (kpis - ML predictions)
- `ng_scoring_cube.sql` (kpis - credit scoring)
- `ng_dunning_cube.sql` (collections)
- `ng_settlement_cube.sql` (collections)
- `we_customer.sql`, `we_account_entities.sql` (master_data)

**Action Items:**

- [ ] Update IMPLEMENTATION.md with 8-domain structure
- [ ] Update TASKS.md with revised entity counts (~36 entities)
- [ ] Update entity ID convention for new domains
- [ ] Phase 2: Add helpe, mrhealth_jordan, terna_energy, kordelos tenants

---

<!--
Status: Draft updated with 8-domain structure (2025-12-05)
Next: Update IMPLEMENTATION.md and TASKS.md to match new structure
-->
