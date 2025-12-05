# Semantic Model Authoring Implementation Guide

**Version:** 3.0
**Last Updated:** 2025-12-05
**Status:** Ready for Implementation

## Quick Reference

### What are we building?

A **domain-first** semantic catalog structure that maps raw data fields to business meaning across the data pipeline layers (bronze/silver/gold). The structure is optimized for advanced search — the primary use case.

**Key change in v3.0:** Expanded from 4 domains to **8 domains** based on semantic separation of concerns:

| Domain | Purpose |
|--------|---------|
| `billing` | Charges TO customer (invoices, debits) |
| `payments` | Money FROM customer (credits, instruments) |
| `ledger` | Unified transaction history (double-entry) |
| `balance` | Point-in-time balance snapshots |
| `collections` | Debt collection (dunning, settlements) |
| `mitigants` | Credit risk mitigation (guarantees, collateral) |
| `kpis` | Calculated metrics & model predictions |
| `master_data` | Reference entities (customer, account, supply_number, address) |

### Where do catalog files go?

```
catalog_libraries/
├── billing/
│   ├── DOMAIN.yaml
│   └── energy/
│       ├── SUBDOMAIN.yaml
│       ├── bronze/
│       │   ├── heron/
│       │   │   └── invoices.yaml
│       │   └── ng/
│       │       └── invoices.yaml
│       ├── silver/_unified/
│       │   └── validated_billing.yaml
│       └── gold/
│           └── billing_summary.yaml
├── payments/
│   ├── DOMAIN.yaml
│   ├── cash/
│   │   ├── bronze/heron/payments.yaml
│   │   └── silver/_unified/validated_payments.yaml
│   └── instruments/
│       └── bronze/heron/checks.yaml
├── ledger/
│   ├── DOMAIN.yaml
│   └── energy/
│       ├── bronze/ng/transactions.yaml
│       └── silver/_unified/unified_ledger.yaml
├── balance/
│   ├── DOMAIN.yaml
│   └── energy/
│       ├── bronze/ng/balance_snapshot.yaml
│       ├── silver/_unified/calculated_balance.yaml
│       └── gold/reconciled_balance.yaml
├── collections/
│   ├── DOMAIN.yaml
│   ├── dunning/
│   │   ├── bronze/ng/
│   │   │   ├── dunnings_raw.yaml
│   │   │   └── dunning_actions.yaml
│   │   ├── silver/ng/dunning_21day.yaml
│   │   └── gold/dunning_cube.yaml
│   └── settlements/
│       ├── bronze/
│       │   ├── heron/settlements.yaml
│       │   └── ng/settlements_raw.yaml
│       └── gold/settlement_cube.yaml
├── mitigants/
│   ├── DOMAIN.yaml
│   └── guarantees/
│       ├── bronze/ng/guarantees.yaml
│       └── silver/_unified/validated_guarantees.yaml
├── kpis/
│   ├── DOMAIN.yaml
│   ├── scoring/
│   │   ├── silver/ng/
│   │   │   ├── default_profile.yaml
│   │   │   └── ml_probabilities.yaml
│   │   └── gold/scoring_cube.yaml
│   └── survival/
│       ├── silver/ng/survival_predictions.yaml
│       └── gold/survival_cube.yaml
└── master_data/
    ├── DOMAIN.yaml
    ├── bronze/_shared/
    │   ├── customer_import.yaml
    │   ├── account_import.yaml
    │   └── supply_number_import.yaml
    ├── bronze/
    │   ├── heron/customers.yaml
    │   └── ng/
    │       ├── b2c_supply_number.yaml
    │       └── b2b_supply_number.yaml
    ├── silver/_unified/
    │   └── account_entity.yaml
    └── gold/
        ├── customer.yaml
        ├── account_entities.yaml
        └── address.yaml
```

### Key Conventions

| Convention | Purpose |
|------------|---------|
| `_shared/` | Cross-tenant bronze schemas (canonical field definitions) |
| `_unified/` | Merged silver assets combining multiple tenant sources |
| `{tenant}/` | Tenant-isolated assets (e.g., `ng/`, `heron/`) |
| Subdomains | Optional — only use when domain has natural subdivisions |
| Filenames | Do not include layer (cannot control bronze filenames) |

### How are entities named?

Path becomes entity ID with dots:

```
{domain}.{subdomain?}.{layer}.{tenant|_shared|_unified}.{asset}
```

**Examples:**
- `billing.energy.bronze.heron.invoices`
- `payments.cash.silver._unified.validated_payments`
- `ledger.energy.bronze.ng.transactions`
- `balance.energy.gold.reconciled_balance`
- `collections.dunning.gold.dunning_cube`
- `kpis.scoring.silver.ng.default_profile`
- `master_data.gold.customer` (no subdomain)

### How are attributes named?

`<entity_short_name>_<field>_v<N>` — e.g., `invoices_amount_eur_v1`, `customer_credit_limit_v1`

---

## Architecture Context

This feature implements semantic model authoring for the catalog described in:

- **Primary:** `docs/ARCHITECTURE.md` - Section 2.5 (Semantic Catalog)
- **Epic:** `specs/milestones/M1_MVP_FOUNDATION/epics/E0_CATALOG_FOUNDATION/EPIC.md`
- **Draft:** `specs/drafts/explorations/DRAFT_semantic_model_authoring.md`

**Modules touched:**

- `catalog_libraries/` — New domain-organized YAML files
- `src/dq_catalog/loader.py` — May need updates for nested domain/subdomain/layer structure
- `src/dq_catalog/models.py` — Verify entity_id supports new naming convention
- `scripts/seed_catalog.py` — May need path updates for new structure

**Key architectural decisions (v3.0 - 2025-12-05):**

1. **8 domains** — Semantic separation: billing ≠ payments, ledger ≠ balance, risk → kpis
2. **Domain-first organization** — Optimizes for search (primary use case)
3. **Subdomains optional** — Not all domains need subdivision
4. **`_shared/` and `_unified/`** — Clear naming for cross-tenant patterns
5. **Tenant-specific gold allowed** — `gold/{tenant}/` accommodates legacy designs
6. **Storage as metadata** — Decouples physical location from logical structure
7. **Phase 1 scope** — heron + ng tenants only (~36 entities)
8. **Phase 2 deferred** — helpe, mrhealth_jordan, terna_energy, kordelos

---

## Why 8 Domains?

The expansion from 4 to 8 domains reflects semantic separation of concerns:

| Previous (4) | Revised (8) | Rationale |
|--------------|-------------|-----------|
| billing | billing | Invoices only (charges TO customer) |
| — | payments | Money FROM customer (semantically distinct) |
| — | ledger | May be ingested as ledger format at bronze |
| — | balance | Critical for balance reconciliation rule |
| collections | collections | Unchanged (dunning, settlements) |
| — | mitigants | Guarantees/collateral need dedicated tracking |
| risk | kpis | Platform calculates many KPIs beyond risk |
| master_data | master_data | Expanded with supply_number |

### Balance Reconciliation Rule

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

---

## Why Domain-First?

| Concern | Layer-First | Domain-First |
|---------|-------------|--------------|
| "Find all billing" | `bronze/billing/** + silver/billing/** + gold/billing/**` | `billing/**` |
| "Find NG bronze" | `bronze/**/ng/**` | `**/bronze/ng/**` |
| Adding new domain | Create files in 3 directories | Create 1 domain directory |
| Lineage visibility | Scattered across layers | `domain/` shows full bronze→silver→gold journey |

---

## Phase 1: Core Structure & Billing/Payments Domains

**Goal:** Establish 8-domain structure and author billing + payments domains (heron + ng)

### Tasks

1. Create directory structure for all 8 domains
2. Author DOMAIN.yaml for each domain
3. Author billing/energy bronze assets (heron invoices, ng invoices)
4. Author payments/cash and payments/instruments bronze assets
5. Verify loader picks up new structure

### Deliverables

- `catalog_libraries/` with 8 domain directories
- DOMAIN.yaml for each domain
- Bronze billing and payments entities for heron/ng

### Success Criteria

- [ ] 8 DOMAIN.yaml files created
- [ ] 4 billing/payments bronze entities defined
- [ ] Entity IDs follow convention
- [ ] Seed script loads without errors

---

## Phase 2: Ledger & Balance Domains

**Goal:** Define ledger and balance domains for transaction/reconciliation support

### Tasks

1. Create ledger/energy directory structure
2. Author ledger bronze (ng transactions)
3. Create balance/energy directory structure
4. Author balance bronze/silver/gold

### Deliverables

- Complete ledger domain with ng transactions
- Complete balance domain with reconciliation entities

### Success Criteria

- [ ] 3 ledger entities (bronze, silver)
- [ ] 3 balance entities (bronze, silver, gold)
- [ ] Balance reconciliation lineage documented

---

## Phase 3: Collections & Mitigants Domains

**Goal:** Complete collections (dunning, settlements) and mitigants (guarantees)

### Tasks

1. Create collections subdomains (dunning, settlements)
2. Author collections bronze/silver/gold assets
3. Create mitigants/guarantees structure
4. Author mitigants bronze/silver

### Deliverables

- Complete collections domain with 7 entities
- Complete mitigants domain with 2 entities

### Success Criteria

- [ ] 7 collections entities across subdomains
- [ ] 2 mitigants entities
- [ ] Derivation documented (bronze → silver)

---

## Phase 4: KPIs Domain

**Goal:** Define KPIs domain (renamed from risk) with scoring and survival subdomains

### Tasks

1. Create kpis/scoring and kpis/survival structure
2. Author silver assets (default_profile, ml_probabilities, survival_predictions)
3. Author gold cubes (scoring_cube, survival_cube)

### Deliverables

- Complete kpis domain with 5 entities
- ML feature documentation

### Success Criteria

- [ ] 3 silver entities (scoring + survival)
- [ ] 2 gold cubes with business definitions
- [ ] KPI calculation methodology documented

---

## Phase 5: Master Data Domain

**Goal:** Define master data entities (customer, account, supply_number, address)

### Tasks

1. Create master_data structure (bronze/_shared, silver/_unified, gold)
2. Author bronze assets (customer_import, supply_number)
3. Author tenant-specific bronze (ng supply_numbers)
4. Author silver/gold master records

### Deliverables

- Complete master_data domain with 9 entities
- Cross-tenant _shared schemas

### Success Criteria

- [ ] `_shared/` used for cross-tenant bronze
- [ ] `_unified/` used for merged silver
- [ ] Gold entities include business definitions

---

## Phase 6: Validation & Documentation

**Goal:** Ensure catalog integrity and document patterns

### Tasks

1. Run full seed and verify all ~36 entities load
2. Create sample contract referencing catalog entities
3. Author `catalog_libraries/README.md`
4. Clean up legacy files

### Deliverables

- Updated README with 8-domain documentation
- Sample contract with catalog references
- Old files archived or removed

### Success Criteria

- [ ] All ~36 entities load successfully
- [ ] No duplicate entity/attribute IDs
- [ ] README documents 8-domain patterns
- [ ] Sample contract validates

---

## Phase 7: Integration Verification

**Goal:** Confirm catalog works with existing infrastructure

### Tasks

1. Test catalog API endpoints
2. Verify contract creation with catalog references
3. Run existing unit tests
4. Update loader if needed

### Deliverables

- API endpoints return new entities
- All tests pass

### Success Criteria

- [ ] GET /api/catalog/entities lists all entities
- [ ] GET /api/catalog/entities/{id} returns details
- [ ] No test regressions

---

## Entity Reference

### Domains & Subdomains

| Domain | Subdomains | Description | Entity Count |
|--------|------------|-------------|--------------|
| `billing` | `energy` | Charges TO customer | 4 |
| `payments` | `cash`, `instruments` | Money FROM customer | 3 |
| `ledger` | `energy` | Unified transactions | 3 |
| `balance` | `energy` | Point-in-time snapshots | 3 |
| `collections` | `dunning`, `settlements` | Debt collection | 7 |
| `mitigants` | `guarantees` | Credit risk mitigation | 2 |
| `kpis` | `scoring`, `survival` | Metrics & predictions | 5 |
| `master_data` | — | Reference entities | 9 |
| **Total** | | | **~36** |

### Entity Inventory by Domain

#### billing (4 entities)

| Entity ID | Layer | Tenant | Key Attributes |
|-----------|-------|--------|----------------|
| `billing.energy.bronze.heron.invoices` | bronze | heron | customer_name, tax_id, amount_eur, consumption_kwh |
| `billing.energy.bronze.ng.invoices` | bronze | ng | transaction_id, account_entities_key, invoice_energy |
| `billing.energy.silver._unified.validated_billing` | silver | _unified | Merged billing from Heron + NG |
| `billing.energy.gold.billing_summary` | gold | — | Billing analytics cube |

#### payments (3 entities)

| Entity ID | Layer | Tenant | Key Attributes |
|-----------|-------|--------|----------------|
| `payments.cash.bronze.heron.payments` | bronze | heron | business_partner_id, payment_date, amount |
| `payments.instruments.bronze.heron.checks` | bronze | heron | check_number, amount, date, status |
| `payments.cash.silver._unified.validated_payments` | silver | _unified | Merged payment records |

#### ledger (3 entities)

| Entity ID | Layer | Tenant | Key Attributes |
|-----------|-------|--------|----------------|
| `ledger.energy.bronze.ng.transactions` | bronze | ng | transaction_date, amount, posting_key |
| `ledger.energy.bronze.heron.transactions` | bronze | heron | payment_type, amount, date |
| `ledger.energy.silver._unified.unified_ledger` | silver | _unified | Combined transaction history |

#### balance (3 entities)

| Entity ID | Layer | Tenant | Key Attributes |
|-----------|-------|--------|----------------|
| `balance.energy.bronze.ng.balance_snapshot` | bronze | ng | account_key, snapshot_date, balance |
| `balance.energy.silver._unified.calculated_balance` | silver | _unified | Computed from ledger transactions |
| `balance.energy.gold.reconciled_balance` | gold | — | Reconciled with variance analysis |

#### collections (7 entities)

| Entity ID | Layer | Tenant | Key Attributes |
|-----------|-------|--------|----------------|
| `collections.dunning.bronze.ng.dunnings_raw` | bronze | ng | action, action_date, past_due |
| `collections.dunning.bronze.ng.dunning_actions` | bronze | ng | action_type, success_rate |
| `collections.dunning.silver.ng.dunning_21day` | silver | ng | dunning_efficiency, paid_amount |
| `collections.dunning.gold.dunning_cube` | gold | — | Dunning ROI analysis |
| `collections.settlements.bronze.heron.settlements` | bronze | heron | settlement_id, total_amount |
| `collections.settlements.bronze.ng.settlements_raw` | bronze | ng | status, installments |
| `collections.settlements.gold.settlement_cube` | gold | — | Settlement success tracking |

#### mitigants (2 entities)

| Entity ID | Layer | Tenant | Key Attributes |
|-----------|-------|--------|----------------|
| `mitigants.guarantees.bronze.ng.guarantees` | bronze | ng | guarantee_id, amount, status |
| `mitigants.guarantees.silver._unified.validated_guarantees` | silver | _unified | Validated guarantee records |

#### kpis (5 entities)

| Entity ID | Layer | Tenant | Key Attributes |
|-----------|-------|--------|----------------|
| `kpis.scoring.silver.ng.default_profile` | silver | ng | risk_level, balance, oldest_past_due_days |
| `kpis.scoring.silver.ng.ml_probabilities` | silver | ng | prob_of_disconnection, prob_to_pay_settlement |
| `kpis.scoring.gold.scoring_cube` | gold | — | Full credit scoring materialized view |
| `kpis.survival.silver.ng.survival_predictions` | silver | ng | expected_survival_months, survival_prob_* |
| `kpis.survival.gold.survival_cube` | gold | — | Survival analysis dashboard |

#### master_data (9 entities)

| Entity ID | Layer | Tenant | Key Attributes |
|-----------|-------|--------|----------------|
| `master_data.bronze._shared.customer_import` | bronze | _shared | Cross-tenant customer schema |
| `master_data.bronze._shared.account_import` | bronze | _shared | Cross-tenant account schema |
| `master_data.bronze._shared.supply_number_import` | bronze | _shared | Cross-tenant supply number schema |
| `master_data.bronze.heron.customers` | bronze | heron | customer_id, name, vat_number |
| `master_data.bronze.ng.b2c_supply_number` | bronze | ng | supply_number, meter_id, address |
| `master_data.bronze.ng.b2b_supply_number` | bronze | ng | supply_number, business_type |
| `master_data.silver._unified.account_entity` | silver | _unified | Unified account entity |
| `master_data.gold.customer` | gold | — | customer_key, name, payment_terms |
| `master_data.gold.account_entities` | gold | — | account_entities_key, customer_id |
| `master_data.gold.address` | gold | — | Address records |

---

## YAML Templates

### DOMAIN.yaml

```yaml
# catalog_libraries/billing/DOMAIN.yaml
domain_id: "billing"
name: "Billing"
description: "Charges TO customer — invoices, consumption debits, and billing adjustments"
owner: "data-engineering@wemetrix.com"
tags:
  - financial
  - revenue
subdomains:
  - "energy"
```

### SUBDOMAIN.yaml

```yaml
# catalog_libraries/billing/energy/SUBDOMAIN.yaml
subdomain_id: "energy"
domain: "billing"
name: "Energy Billing"
description: "Energy consumption invoices from Heron and NG suppliers"
tenants:
  - "heron"
  - "ng"
layers:
  - "bronze"
  - "silver"
  - "gold"
```

### Asset YAML

```yaml
# catalog_libraries/billing/energy/bronze/heron/invoices.yaml
entity_id: "billing.energy.bronze.heron.invoices"
name: "Heron Invoices"
description: "Raw invoice data from Heron energy supplier"
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
  amount_eur: "Ποσό EUR"
tags:
  - financial
  - energy
  - billing
attributes:
  - attribute_id: "invoices_customer_name_v1"
    name: "Customer Name"
    description: "Customer full name (Greek: Επωνυμία)"
    data_type: "string"
    is_pii: true
    is_required: true

  - attribute_id: "invoices_tax_id_v1"
    name: "Tax ID"
    description: "Greek VAT number (ΑΦΜ)"
    data_type: "string"
    is_pii: true
    is_required: true

  - attribute_id: "invoices_amount_eur_v1"
    name: "Amount EUR"
    description: "Invoice amount in EUR"
    data_type: "decimal"
    is_pii: false
    is_required: true
```

---

## Search Query Examples

| Query | Pattern |
|-------|---------|
| All billing data | `billing.**` |
| All payments data | `payments.**` |
| All bronze billing | `billing.*.bronze.**` |
| All NG tenant assets | `**.ng.**` |
| All unified silver | `**.silver._unified.**` |
| KPI scoring (any layer) | `kpis.scoring.**` |
| All gold cubes | `**.gold.*_cube` |
| Balance reconciliation | `balance.**` |

---

## Success Criteria Summary

- [ ] ~36 entities across 8 domains
- [ ] Domain-first naming: `{domain}.{subdomain?}.{layer}.{tenant}.{asset}`
- [ ] DOMAIN.yaml for each domain
- [ ] SUBDOMAIN.yaml where applicable
- [ ] PII classifications accurate
- [ ] Bronze→silver derivations documented
- [ ] Gold entities have business definitions
- [ ] Seed script runs successfully
- [ ] API endpoints return new entities
- [ ] Sample contract validates against catalog
- [ ] README documents 8-domain patterns

---

## Next Steps After This Feature

1. **E0.F2 (Catalog Persistence)** — Move from YAML/in-memory to Postgres
2. **E0.F3 (Contract Validation)** — Enforce catalog references on contract save
3. **E0.F4 (Engine Integration)** — Wire catalog into validation/profiling engines

---

## Phase 2 Scope (Deferred)

Additional tenants to add after core catalog is stable:

| Tenant | Domains Affected | Priority |
|--------|------------------|----------|
| kordelos | billing.traditional, payments.instruments, ledger | Medium |
| helpe | balance, mitigants, master_data | Medium |
| mrhealth_jordan | ledger, payments, balance | Low |
| terna_energy | ledger | Low |
