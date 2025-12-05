# Semantic Model Authoring — Task List

**Feature:** E0.F1 - Semantic Model Authoring
**Epic:** E0_CATALOG_FOUNDATION
**Version:** 3.0 (8-Domain Structure)
**Last Updated:** 2025-12-05
**Status:** Not Started

---

## Phase 1: Core Structure & Billing/Payments Domains

### Task 1.1: Create 8-domain directory structure

- [ ] Create `catalog_libraries/billing/energy/bronze/{heron,ng}/`
- [ ] Create `catalog_libraries/billing/energy/{silver/_unified,gold}/`
- [ ] Create `catalog_libraries/payments/{cash,instruments}/bronze/heron/`
- [ ] Create `catalog_libraries/payments/cash/silver/_unified/`
- [ ] Create `catalog_libraries/ledger/energy/{bronze/ng,silver/_unified}/`
- [ ] Create `catalog_libraries/balance/energy/{bronze/ng,silver/_unified,gold}/`
- [ ] Create `catalog_libraries/collections/dunning/{bronze/ng,silver/ng,gold}/`
- [ ] Create `catalog_libraries/collections/settlements/{bronze/heron,bronze/ng,gold}/`
- [ ] Create `catalog_libraries/mitigants/guarantees/{bronze/ng,silver/_unified}/`
- [ ] Create `catalog_libraries/kpis/scoring/{silver/ng,gold}/`
- [ ] Create `catalog_libraries/kpis/survival/{silver/ng,gold}/`
- [ ] Create `catalog_libraries/master_data/bronze/{_shared,heron,ng}/`
- [ ] Create `catalog_libraries/master_data/{silver/_unified,gold}/`

**Quick command:**

```bash
# Billing
mkdir -p catalog_libraries/billing/energy/bronze/{heron,ng}
mkdir -p catalog_libraries/billing/energy/silver/_unified
mkdir -p catalog_libraries/billing/energy/gold

# Payments
mkdir -p catalog_libraries/payments/cash/bronze/heron
mkdir -p catalog_libraries/payments/cash/silver/_unified
mkdir -p catalog_libraries/payments/instruments/bronze/heron

# Ledger
mkdir -p catalog_libraries/ledger/energy/bronze/{ng,heron}
mkdir -p catalog_libraries/ledger/energy/silver/_unified

# Balance
mkdir -p catalog_libraries/balance/energy/bronze/ng
mkdir -p catalog_libraries/balance/energy/silver/_unified
mkdir -p catalog_libraries/balance/energy/gold

# Collections
mkdir -p catalog_libraries/collections/dunning/bronze/ng
mkdir -p catalog_libraries/collections/dunning/silver/ng
mkdir -p catalog_libraries/collections/dunning/gold
mkdir -p catalog_libraries/collections/settlements/bronze/{heron,ng}
mkdir -p catalog_libraries/collections/settlements/gold

# Mitigants
mkdir -p catalog_libraries/mitigants/guarantees/bronze/ng
mkdir -p catalog_libraries/mitigants/guarantees/silver/_unified

# KPIs
mkdir -p catalog_libraries/kpis/scoring/silver/ng
mkdir -p catalog_libraries/kpis/scoring/gold
mkdir -p catalog_libraries/kpis/survival/silver/ng
mkdir -p catalog_libraries/kpis/survival/gold

# Master Data
mkdir -p catalog_libraries/master_data/bronze/_shared
mkdir -p catalog_libraries/master_data/bronze/{heron,ng}
mkdir -p catalog_libraries/master_data/silver/_unified
mkdir -p catalog_libraries/master_data/gold
```

**Verification:** `tree catalog_libraries/ -d` shows all 8 domain directories

### Task 1.2: Author 8 DOMAIN.yaml files

- [ ] Create `billing/DOMAIN.yaml`
- [ ] Create `payments/DOMAIN.yaml`
- [ ] Create `ledger/DOMAIN.yaml`
- [ ] Create `balance/DOMAIN.yaml`
- [ ] Create `collections/DOMAIN.yaml`
- [ ] Create `mitigants/DOMAIN.yaml`
- [ ] Create `kpis/DOMAIN.yaml`
- [ ] Create `master_data/DOMAIN.yaml`

**Verification:** 8 DOMAIN.yaml files exist and parse without errors

### Task 1.3: Author billing/energy assets (4 entities)

- [ ] Create `billing/energy/SUBDOMAIN.yaml`
- [ ] Create `billing/energy/bronze/heron/invoices.yaml`
  - entity_id: `billing.energy.bronze.heron.invoices`
  - field_mappings: Greek→English (Επωνυμία→customer_name, ΑΦΜ→tax_id)
- [ ] Create `billing/energy/bronze/ng/invoices.yaml`
  - entity_id: `billing.energy.bronze.ng.invoices`
- [ ] Create `billing/energy/silver/_unified/validated_billing.yaml`
  - entity_id: `billing.energy.silver._unified.validated_billing`
- [ ] Create `billing/energy/gold/billing_summary.yaml`
  - entity_id: `billing.energy.gold.billing_summary`

**Verification:** `python scripts/seed_catalog.py` loads 4 billing entities

### Task 1.4: Author payments assets (3 entities)

- [ ] Create `payments/cash/SUBDOMAIN.yaml`
- [ ] Create `payments/instruments/SUBDOMAIN.yaml`
- [ ] Create `payments/cash/bronze/heron/payments.yaml`
  - entity_id: `payments.cash.bronze.heron.payments`
- [ ] Create `payments/instruments/bronze/heron/checks.yaml`
  - entity_id: `payments.instruments.bronze.heron.checks`
- [ ] Create `payments/cash/silver/_unified/validated_payments.yaml`
  - entity_id: `payments.cash.silver._unified.validated_payments`

**Verification:** `python scripts/seed_catalog.py` loads 7 entities total (4 billing + 3 payments)

---

## Phase 2: Ledger & Balance Domains

### Task 2.1: Author ledger/energy assets (3 entities)

- [ ] Create `ledger/energy/SUBDOMAIN.yaml`
- [ ] Create `ledger/energy/bronze/ng/transactions.yaml`
  - entity_id: `ledger.energy.bronze.ng.transactions`
  - Source: ng_ledger / b2c_transactions
- [ ] Create `ledger/energy/bronze/heron/transactions.yaml`
  - entity_id: `ledger.energy.bronze.heron.transactions`
- [ ] Create `ledger/energy/silver/_unified/unified_ledger.yaml`
  - entity_id: `ledger.energy.silver._unified.unified_ledger`

**Verification:** 3 ledger entities load

### Task 2.2: Author balance/energy assets (3 entities)

- [ ] Create `balance/energy/SUBDOMAIN.yaml`
- [ ] Create `balance/energy/bronze/ng/balance_snapshot.yaml`
  - entity_id: `balance.energy.bronze.ng.balance_snapshot`
- [ ] Create `balance/energy/silver/_unified/calculated_balance.yaml`
  - entity_id: `balance.energy.silver._unified.calculated_balance`
  - Derivation: starting_balance + SUM(ledger)
- [ ] Create `balance/energy/gold/reconciled_balance.yaml`
  - entity_id: `balance.energy.gold.reconciled_balance`
  - Business definition: Reconciled balance with variance analysis

**Verification:** 6 entities total in ledger + balance domains

---

## Phase 3: Collections & Mitigants Domains

### Task 3.1: Author collections/dunning assets (4 entities)

- [ ] Create `collections/dunning/SUBDOMAIN.yaml`
- [ ] Create `collections/dunning/bronze/ng/dunnings_raw.yaml`
  - entity_id: `collections.dunning.bronze.ng.dunnings_raw`
- [ ] Create `collections/dunning/bronze/ng/dunning_actions.yaml`
  - entity_id: `collections.dunning.bronze.ng.dunning_actions`
- [ ] Create `collections/dunning/silver/ng/dunning_21day.yaml`
  - entity_id: `collections.dunning.silver.ng.dunning_21day`
  - Derivation: dunnings_raw + payments
- [ ] Create `collections/dunning/gold/dunning_cube.yaml`
  - entity_id: `collections.dunning.gold.dunning_cube`
  - Business definition: Dunning action ROI analysis

**Verification:** 4 dunning entities load

### Task 3.2: Author collections/settlements assets (3 entities)

- [ ] Create `collections/settlements/SUBDOMAIN.yaml`
- [ ] Create `collections/settlements/bronze/heron/settlements.yaml`
  - entity_id: `collections.settlements.bronze.heron.settlements`
- [ ] Create `collections/settlements/bronze/ng/settlements_raw.yaml`
  - entity_id: `collections.settlements.bronze.ng.settlements_raw`
- [ ] Create `collections/settlements/gold/settlement_cube.yaml`
  - entity_id: `collections.settlements.gold.settlement_cube`
  - Business definition: Settlement success tracking

**Verification:** 7 collections entities total

### Task 3.3: Author mitigants/guarantees assets (2 entities)

- [ ] Create `mitigants/guarantees/SUBDOMAIN.yaml`
- [ ] Create `mitigants/guarantees/bronze/ng/guarantees.yaml`
  - entity_id: `mitigants.guarantees.bronze.ng.guarantees`
- [ ] Create `mitigants/guarantees/silver/_unified/validated_guarantees.yaml`
  - entity_id: `mitigants.guarantees.silver._unified.validated_guarantees`

**Verification:** 2 mitigants entities load

---

## Phase 4: KPIs Domain

### Task 4.1: Author kpis/scoring assets (3 entities)

- [ ] Create `kpis/scoring/SUBDOMAIN.yaml`
- [ ] Create `kpis/scoring/silver/ng/default_profile.yaml`
  - entity_id: `kpis.scoring.silver.ng.default_profile`
  - Source: ng326_default table
  - Attributes: risk_level, balance, past_due_balance, oldest_past_due_days
- [ ] Create `kpis/scoring/silver/ng/ml_probabilities.yaml`
  - entity_id: `kpis.scoring.silver.ng.ml_probabilities`
  - Source: ng_4_probabilities table
  - Attributes: prob_of_disconnection, prob_of_termination, prob_to_pay_settlement
- [ ] Create `kpis/scoring/gold/scoring_cube.yaml`
  - entity_id: `kpis.scoring.gold.scoring_cube`
  - Business definition: Full credit scoring materialized view
  - Attributes: aging buckets, DSO, risk_level, settlement metrics, dunning efficiency

**Verification:** 3 scoring entities load

### Task 4.2: Author kpis/survival assets (2 entities)

- [ ] Create `kpis/survival/SUBDOMAIN.yaml`
- [ ] Create `kpis/survival/silver/ng/survival_predictions.yaml`
  - entity_id: `kpis.survival.silver.ng.survival_predictions`
  - Source: ng326_survival_predictions table
  - Attributes: expected_survival_months, survival_prob_3m/6m/12m/24m
- [ ] Create `kpis/survival/gold/survival_cube.yaml`
  - entity_id: `kpis.survival.gold.survival_cube`
  - Business definition: Survival analysis dashboard

**Verification:** 5 kpis entities total

---

## Phase 5: Master Data Domain

### Task 5.1: Author master_data bronze/_shared assets (3 entities)

- [ ] Create `master_data/bronze/_shared/customer_import.yaml`
  - entity_id: `master_data.bronze._shared.customer_import`
  - Purpose: Cross-tenant canonical customer schema
- [ ] Create `master_data/bronze/_shared/account_import.yaml`
  - entity_id: `master_data.bronze._shared.account_import`
  - Purpose: Cross-tenant canonical account schema
- [ ] Create `master_data/bronze/_shared/supply_number_import.yaml`
  - entity_id: `master_data.bronze._shared.supply_number_import`
  - Purpose: Cross-tenant canonical supply number schema

**Verification:** 3 _shared entities load

### Task 5.2: Author master_data tenant-specific bronze (3 entities)

- [ ] Create `master_data/bronze/heron/customers.yaml`
  - entity_id: `master_data.bronze.heron.customers`
- [ ] Create `master_data/bronze/ng/b2c_supply_number.yaml`
  - entity_id: `master_data.bronze.ng.b2c_supply_number`
- [ ] Create `master_data/bronze/ng/b2b_supply_number.yaml`
  - entity_id: `master_data.bronze.ng.b2b_supply_number`

**Verification:** 6 master_data bronze entities total

### Task 5.3: Author master_data silver/gold assets (3 entities)

- [ ] Create `master_data/silver/_unified/account_entity.yaml`
  - entity_id: `master_data.silver._unified.account_entity`
- [ ] Create `master_data/gold/customer.yaml`
  - entity_id: `master_data.gold.customer`
- [ ] Create `master_data/gold/account_entities.yaml`
  - entity_id: `master_data.gold.account_entities`
- [ ] Create `master_data/gold/address.yaml`
  - entity_id: `master_data.gold.address`

**Verification:** 9 master_data entities total (note: gold has 3 entities, making 10 total)

---

## Phase 6: Validation & Documentation

### Task 6.1: Full catalog validation

- [ ] Run `python scripts/seed_catalog.py`
- [ ] Verify ~36 entities load
- [ ] Check for duplicate entity IDs
- [ ] Check for duplicate attribute IDs

**Verification:** Script completes without errors

### Task 6.2: Update loader if needed

- [ ] Review `src/dq_catalog/loader.py`
- [ ] Ensure nested domain/subdomain/layer structure is supported
- [ ] Test entity_id extraction from path

**Verification:** Loader handles 8-domain structure

### Task 6.3: Create sample contract

- [ ] Create test contract referencing catalog entities
- [ ] Include `catalog_entity_ids: ["billing.energy.bronze.heron.invoices"]`
- [ ] Include column with `catalog_attribute_id: "invoices_amount_eur_v1"`

**Verification:** Contract file validates

### Task 6.4: Update catalog_libraries/README.md

- [ ] Document 8-domain structure rationale
- [ ] Document naming conventions
- [ ] Provide DOMAIN.yaml template
- [ ] Provide SUBDOMAIN.yaml template
- [ ] Provide asset YAML template
- [ ] List all entities by domain (~36)
- [ ] Add authoring guidelines

**Verification:** README comprehensive and accurate

### Task 6.5: Clean up legacy files

- [ ] Archive or remove `customer_domain.yaml`
- [ ] Remove any other domain-centric or layer-centric legacy files
- [ ] Ensure only 8-domain structure remains

**Verification:** `ls catalog_libraries/` shows only 8 domain directories

---

## Phase 7: Integration Verification

### Task 7.1: Test API endpoints

- [ ] GET /api/catalog/entities returns all entities
- [ ] GET /api/catalog/entities/billing.energy.bronze.heron.invoices returns details
- [ ] GET /api/catalog/entities/kpis.scoring.gold.scoring_cube returns details
- [ ] GET /api/catalog/entities/master_data.gold.customer returns details
- [ ] GET /api/catalog/entities/balance.energy.gold.reconciled_balance returns details

**Verification:** All API calls succeed with correct data

### Task 7.2: Run existing tests

- [ ] `pytest tests/unit/test_catalog*.py -v`
- [ ] All tests pass
- [ ] No regressions

**Verification:** Test suite green

### Task 7.3: Document completion

- [ ] Update feature checkpoint to completed
- [ ] Update EPIC.md Feature 1 status
- [ ] Archive draft exploration document

**Verification:** Planning docs reflect completion

---

## Task Summary

| Phase | Tasks | Entities Created |
|-------|-------|------------------|
| Phase 1 | 4 | 7 (billing + payments bronze/silver) |
| Phase 2 | 2 | 6 (ledger + balance) |
| Phase 3 | 3 | 9 (collections + mitigants) |
| Phase 4 | 2 | 5 (kpis scoring + survival) |
| Phase 5 | 3 | 9 (master_data all layers) |
| Phase 6 | 5 | 0 (validation) |
| Phase 7 | 3 | 0 (integration) |
| **Total** | **22** | **~36** |

---

## Dependencies

- **Requires:** None (foundational feature)
- **Blocks:** E0.F2 (Catalog Persistence) needs YAML files to load into Postgres

## Files to Create

### Domain Definitions (8 files)

1. `catalog_libraries/billing/DOMAIN.yaml`
2. `catalog_libraries/payments/DOMAIN.yaml`
3. `catalog_libraries/ledger/DOMAIN.yaml`
4. `catalog_libraries/balance/DOMAIN.yaml`
5. `catalog_libraries/collections/DOMAIN.yaml`
6. `catalog_libraries/mitigants/DOMAIN.yaml`
7. `catalog_libraries/kpis/DOMAIN.yaml`
8. `catalog_libraries/master_data/DOMAIN.yaml`

### Subdomain Definitions (10 files)

1. `billing/energy/SUBDOMAIN.yaml`
2. `payments/cash/SUBDOMAIN.yaml`
3. `payments/instruments/SUBDOMAIN.yaml`
4. `ledger/energy/SUBDOMAIN.yaml`
5. `balance/energy/SUBDOMAIN.yaml`
6. `collections/dunning/SUBDOMAIN.yaml`
7. `collections/settlements/SUBDOMAIN.yaml`
8. `mitigants/guarantees/SUBDOMAIN.yaml`
9. `kpis/scoring/SUBDOMAIN.yaml`
10. `kpis/survival/SUBDOMAIN.yaml`

### Entity Assets (~36 files)

**billing (4):**
- `billing/energy/bronze/heron/invoices.yaml`
- `billing/energy/bronze/ng/invoices.yaml`
- `billing/energy/silver/_unified/validated_billing.yaml`
- `billing/energy/gold/billing_summary.yaml`

**payments (3):**
- `payments/cash/bronze/heron/payments.yaml`
- `payments/instruments/bronze/heron/checks.yaml`
- `payments/cash/silver/_unified/validated_payments.yaml`

**ledger (3):**
- `ledger/energy/bronze/ng/transactions.yaml`
- `ledger/energy/bronze/heron/transactions.yaml`
- `ledger/energy/silver/_unified/unified_ledger.yaml`

**balance (3):**
- `balance/energy/bronze/ng/balance_snapshot.yaml`
- `balance/energy/silver/_unified/calculated_balance.yaml`
- `balance/energy/gold/reconciled_balance.yaml`

**collections (7):**
- `collections/dunning/bronze/ng/dunnings_raw.yaml`
- `collections/dunning/bronze/ng/dunning_actions.yaml`
- `collections/dunning/silver/ng/dunning_21day.yaml`
- `collections/dunning/gold/dunning_cube.yaml`
- `collections/settlements/bronze/heron/settlements.yaml`
- `collections/settlements/bronze/ng/settlements_raw.yaml`
- `collections/settlements/gold/settlement_cube.yaml`

**mitigants (2):**
- `mitigants/guarantees/bronze/ng/guarantees.yaml`
- `mitigants/guarantees/silver/_unified/validated_guarantees.yaml`

**kpis (5):**
- `kpis/scoring/silver/ng/default_profile.yaml`
- `kpis/scoring/silver/ng/ml_probabilities.yaml`
- `kpis/scoring/gold/scoring_cube.yaml`
- `kpis/survival/silver/ng/survival_predictions.yaml`
- `kpis/survival/gold/survival_cube.yaml`

**master_data (9):**
- `master_data/bronze/_shared/customer_import.yaml`
- `master_data/bronze/_shared/account_import.yaml`
- `master_data/bronze/_shared/supply_number_import.yaml`
- `master_data/bronze/heron/customers.yaml`
- `master_data/bronze/ng/b2c_supply_number.yaml`
- `master_data/bronze/ng/b2b_supply_number.yaml`
- `master_data/silver/_unified/account_entity.yaml`
- `master_data/gold/customer.yaml`
- `master_data/gold/account_entities.yaml`
- `master_data/gold/address.yaml`

### Documentation

- `catalog_libraries/README.md` (update)
- Sample contract with catalog references

---

## Definition of Done

- [ ] ~36 entities defined across 8 domains
- [ ] Entity IDs follow domain-first convention
- [ ] DOMAIN.yaml for each domain (8 total)
- [ ] SUBDOMAIN.yaml where applicable (10 total)
- [ ] Seed script loads all entities without errors
- [ ] API endpoints return entity data
- [ ] README documents 8-domain authoring patterns
- [ ] Sample contract demonstrates catalog usage
- [ ] All existing tests pass
- [ ] Legacy files removed
