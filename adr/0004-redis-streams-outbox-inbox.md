---
status: accepted
---

# Use Redis Streams with outbox and inbox

Backend and AI/ML will exchange long-running commands and facts through Redis Streams using consumer groups, transactional outboxes, consumer inboxes, and idempotent handlers. This reuses the accepted Redis dependency and makes processing recoverable without requiring synchronous model calls; contracts remain broker-neutral so a production limit can justify migration later.
