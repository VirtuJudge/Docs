---
status: accepted
---

# Use versioned boundary contracts

Frontend/backend REST uses OpenAPI 3.1, frontend updates use a documented SSE schema, and backend/AI messages use AsyncAPI with JSON Schema. Producers own executable schemas, Docs contains reviewed semantics and generated snapshots, and breaking changes require a new major version with a migration period so peer repositories cannot silently drift.
