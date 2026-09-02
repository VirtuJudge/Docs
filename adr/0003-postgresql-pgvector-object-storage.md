---
status: accepted
---

# Use PostgreSQL, pgvector, and object storage

Operational state and AI-derived metadata will use separately owned PostgreSQL databases or schemas, embeddings will use pgvector, and media/large artifacts will use S3-compatible object storage. MongoDB is excluded because Q&A and report JSON do not justify another operational database, while PostgreSQL JSONB covers the flexible validated payloads needed by the MVP.
