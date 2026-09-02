---
status: accepted
---

# Use versioned boundary contracts

Frontend/backend REST and the worker callback use OpenAPI 3.1, frontend updates use a documented SSE schema, and queued AI Jobs use JSON Schema. The backend owns the job and callback interface, AI/ML owns derived artifact schemas, and breaking changes require a new version so the repos cannot silently drift.
