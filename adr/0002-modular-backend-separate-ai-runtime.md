---
status: accepted
---

# Use a layered backend and separate AI worker

The backend will be one four-layer FastAPI application, while AI/ML runs as one separate worker with a deep pipeline interface. More backend modules or AI services would cost too much during the ten-day MVP, but keeping model workloads inside the API process would still couple API availability to long-running, resource-heavy processing.
