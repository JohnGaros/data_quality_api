# Action Libraries

Author reusable post-job action definitions (notifications, lineage events, webhooks, ticketing, storage exports, etc.) using YAML/JSON/Excel files.

- Mirrors other authoring libraries: version-controlled source, validated by loaders, normalised into canonical JSON.
- Produces `ActionProfile` payloads that the runtime registry (`src/dq_actions/`) will persist in Postgres JSONB so APIs and job managers can resolve them.
- Keeps actions declarative and tenant-aware instead of scattering post-job behaviour across custom scripts.
