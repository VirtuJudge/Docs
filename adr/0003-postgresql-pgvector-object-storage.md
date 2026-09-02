---
status: accepted
---

# Use PostgreSQL, pgvector, and object storage

Product state, AI Job status, and AI-derived metadata will share one PostgreSQL/pgvector instance, using normal tables and an `ai_*` prefix or schema to make ownership clear. Media and large artifacts use S3-compatible object storage. MongoDB is excluded because Q&A and report JSON do not justify another database during the MVP.
