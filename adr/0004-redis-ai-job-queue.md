---
status: accepted
---

# Use a Redis AI job queue

The backend will save AI Jobs in PostgreSQL and enqueue them to one Celery/Redis worker; the worker reports progress and results through one authenticated backend callback. Stable job IDs, a pending-job dispatcher, retries, and monotonic updates give the MVP enough recovery without building a general event platform.
