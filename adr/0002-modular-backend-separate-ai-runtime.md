---
status: accepted
---

# Use a modular backend and separate AI runtime

The FastAPI backend will be a layered modular monolith that owns product state and orchestration, while AI/ML runs as a separate deployable compute plane. A backend microservice split would cost too much during the MVP, but keeping model workloads in the API process would couple API availability and deployment to long-running, resource-heavy, provider-dependent pipelines.
