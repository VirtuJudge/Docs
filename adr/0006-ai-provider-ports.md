---
status: accepted
---

# Keep AI choices behind provider ports

Whisper Large V3 Turbo, pyannote Community-1, MediaPipe Pose and Face Landmarker, and librosa are the initial direction, while the AI team chooses exact versions, hosting, LLM, embeddings, and settings. Every external or model-specific choice sits behind a canonical port and records provenance, allowing the team to compare or replace providers without changing pipeline or product contracts.
