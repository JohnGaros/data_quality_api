# Catalog Libraries

This directory contains the authoritative YAML definitions for the Global Data Catalog.
These files are the source of truth for all Semantic Entities and Attributes.

## Structure

Organize files by domain or subject area. The filename does not affect the logical ID, but helps with organization.

Example: `customer_domain.yaml`

```yaml
entities:
  - catalog_entity_id: "customer_v1"
    name: "Customer"
    description: "Global Customer Entity"
    domain: "Sales"
    attributes:
      - catalog_attribute_id: "customer_email_v1"
        name: "Email"
        data_type: "string"
        description: "Personal Email Address"
        tags: ["PII", "Contact"]
```

## Versioning (Append-Only)

- **Do not** change the semantic meaning of an existing `catalog_attribute_id`.
- If a definition changes, create a **new** attribute with a new ID (e.g., `customer_email_v2`).
- Mark the old attribute as `deprecated: true`.

## Seeding

Run `python scripts/seed_catalog.py` to load these definitions into the active Catalog Repository.
