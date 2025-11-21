# Schema Libraries

Author canonical schemas, code lists, and taxonomy definitions in YAML/JSON/Excel.

- Provide reusable schema templates referenced by data contracts (`SchemaRef`).
- Validate structure via library loaders (planned) and emit Pydantic models + canonical JSON for registries.

These authored schemas are ingested into the contract registry so engines and UIs consume resolved, versioned schemas per tenant/environment.
