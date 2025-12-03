# Draft: Semantic Model Authoring

**Created:** 2025-12-03
**Status:** exploring
**Origin:** standalone
**Target:** M1_MVP_FOUNDATION / E0_CATALOG_FOUNDATION

## Problem Statement

The platform needs a well-designed semantic data catalog that maps raw data fields to business meaning across the data pipeline layers (bronze → silver → gold). Currently:

- Catalog authoring is done via YAML files in `catalog_libraries/`
- The existing `customer_domain.yaml` example doesn't reflect the actual business domains
- No structured approach exists for deriving catalog entities from real datasets
- Team communication is organized by **pipeline layer first** (e.g., "raw data customer just sent"), then by business domain

**Who benefits:**
- Data engineers mapping ingested files to semantic meaning
- Analysts tracing KPIs back to source fields
- Data stewards governing field-level lineage

## Proposed Approach

### Organizing Principle: Pipeline Layer First, Then Business Domain

```
catalog_libraries/
├── bronze/                    # Raw ingestion (customer sends data)
│   ├── accounting.yaml        # GL, AP, AR, journal entries
│   ├── crm.yaml               # Contacts, interactions, campaigns
│   └── erp.yaml               # Orders, inventory, master data
├── silver/                    # Cleansed & enriched
│   ├── customer.yaml          # Unified customer entity
│   ├── credit.yaml            # Credit scores, limits, risk
│   └── transactions.yaml      # Normalized transaction history
├── gold/                      # Reporting & model-ready
│   ├── kpis.yaml              # Credit KPIs, customer metrics
│   └── model_features.yaml    # ML feature definitions
└── cross_cutting/
    ├── identifiers.yaml       # Customer IDs, account IDs across layers
    └── audit.yaml             # Timestamps, source tracking
```

### Why Layer-First Works

| Layer | Team Discussion Pattern | Catalog Purpose |
|-------|------------------------|-----------------|
| **Bronze** | "Customer X just sent their AR export" | Map raw fields to semantic meaning |
| **Silver** | "We need to join customer + credit data" | Define cleansed, linkable entities |
| **Gold** | "The DSO KPI looks wrong" | Trace KPI back to source fields |

### Recommended Approach

1. **Gather example datasets** — real flat files (Excel/CSV) and Postgres DDL
2. **Analyze field inventories** — extract columns, data types, patterns
3. **Cluster by business concept** — group fields into entities
4. **Author YAML catalog by layer** — bronze → silver → gold
5. **Validate against use cases** — can validation rules map to catalog attributes?

## Key Questions

- [x] What are the primary business domains? → Credit/customer KPIs, ingesting from accounting, CRM, ERP
- [x] How should catalog be organized? → Pipeline layer first, then business domain
- [ ] What specific entities exist at each layer?
- [ ] How do bronze entities transform into silver entities?
- [ ] What KPIs and model features define the gold layer?

## Research Notes

### Existing Code Analysis

| Component | Location | Status |
|-----------|----------|--------|
| Models | `src/dq_catalog/models.py` | Complete: CatalogEntity, CatalogAttribute, CatalogRelationship |
| YAML Loader | `src/dq_catalog/loader.py` | Complete: loads from `catalog_libraries/` |
| Repository | `src/dq_catalog/repository.py` | Complete: in-memory with attribute index |
| GET API | `src/dq_api/routes/catalog.py` | Complete: list/get entities |
| POST API | `src/dq_api/routes/catalog.py` | Basic: lacks validation, audit trail |
| Seeding | `scripts/seed_catalog.py` | Complete: loads directory into repository |

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

- [ ] Problem clearly defined
- [x] Approach validated (layer-first organization)
- [ ] Key questions answered
- [ ] Target epic/feature identified
- [ ] Dependencies understood
- [ ] No blocking concerns

## Session History

| Date | Activity | Outcome |
|------|----------|---------|
| 2025-12-03 | Created | Initial brainstorm on semantic model authoring |
| 2025-12-03 | Refined | Decided on layer-first organization (bronze/silver/gold) |
| 2025-12-03 | Setup | Created `examples/datasets/` structure for sample data |

---

<!--
Next: User will add example datasets, then analyze to draft concrete YAML definitions
-->
