# Security, privacy, and retention

## Principles

- Private by default.
- Team-scoped authorization on every resource.
- Explicit consent before recording or analysis.
- Minimum data sent to each model provider.
- No customer content used for model training.
- Observable facts instead of psychological or biometric claims.
- Deletion revokes access immediately and removes physical data within a documented window.

## Data classification

| Class | Examples | Rules |
|---|---|---|
| Restricted media | Presentation video, answer audio | Private object storage, signed access, 30-day raw-media retention, never logged |
| Confidential content | Documents, transcripts, questions, reports | Team-only access, encrypted transport/storage, provider minimization |
| Identity data | Name, email, membership, invitation | Backend only; audit access and changes |
| Derived measurements | Timed landmarks, speech features, embeddings | AI-owned store; preserve provenance and retention link to source |
| Operational metadata | IDs, timestamps, states, timing, safe errors | Structured telemetry; exclude content and secrets |
| Public code/docs | Source, schemas, examples using synthetic data | Reviewed for accidental real data before publication |

## Consent

Before starting a session, the user confirms that every recorded participant has consented to:

- upload and processing of the presentation;
- voice transcription and speaker diarization;
- pose, face-landmark, movement, and gaze-direction processing;
- generation of team and per-member feedback;
- the stated retention period and configured external model providers.

The backend records consent policy version, actor, timestamp, and session. Revoking consent cancels active work and begins deletion; it does not rewrite already-exported files outside VirtuJudge's control.

## Retention schedule

| Data | Default | Deletion behaviour |
|---|---:|---|
| Incomplete upload | 24 hours | Automated object and intent cleanup |
| Raw presentation video | 30 days after upload | Remove object; keep safe deletion audit |
| Raw answer audio | 30 days after upload | Remove object; retain transcript only while project exists |
| Supporting documents | Until asset/project deletion | Delete all versions and linked embeddings |
| Derived features and embeddings | While source exists | Cascade erasure by source asset version |
| Evaluation and report | Until project deletion | Revoke immediately; physical purge within 24 hours |
| Invitation token | Until consumed or expired | Token is stored hashed; purge expired records on schedule |
| Security audit metadata | Configured compliance period | No media or content; pseudonymize after identity erasure where lawful |

An owner may request session or project deletion. The API returns an Erasure Request ID. Resources become inaccessible immediately, and the purge worker removes backend records, AI-derived data, vectors, objects, PDFs, cache entries, and queued work within 24 hours. Failures are retried and visible to operators.

## Threat-focused controls

| Threat | Control |
|---|---|
| Cross-team access | Server-side membership checks using resource ancestry; opaque IDs aren't authorization |
| Malicious upload | Extension allow-list, file signature and MIME inspection, size/duration checks, isolated processing; malware scanning is production-readiness work |
| Signed URL leakage | Short TTL, method/key/content constraints, HTTPS, never log URLs |
| AI Job forgery or replay | Private Redis, worker callback credential, schema validation, job ID/sequence checks, expected-attempt checks |
| Prompt injection in documents | Treat document text as untrusted evidence, isolate instructions from system prompts, constrain outputs, validate citations |
| Model data exfiltration | Provider allow-list, minimum evidence bundle, disabled training where provider supports it, document provider terms |
| Invitation theft | Random single-use token, stored hash, expiry, email match, atomic consumption |
| Excessive model spend | Per-team rate limits, duration/file limits, stage budgets, idempotency, cost telemetry |
| Sensitive telemetry | Log IDs and safe categories only; redact authorization, content, transcript, URLs, tokens, and payloads |

## Human-impact boundary

MediaPipe and librosa outputs are presentation measurements. Reports may say, for example, that gaze was directed away from the camera during a time interval or that a pause lasted 2.4 seconds. They must not claim that a person was anxious, deceptive, unprepared, confident, or emotionally distressed.

Individual feedback is visible to the team under the MVP permission model. The report must explain this before recording begins. More restrictive per-member visibility is a future policy decision.

## Security verification

- Authorization matrix integration tests.
- Upload validation and object-key isolation tests.
- JWT validation and expired/incorrect-audience tests.
- Duplicate job, stale attempt, callback authentication, and cross-team artifact tests.
- Prompt-injection and unsupported-citation evaluation cases.
- Dependency and container vulnerability scans.
- Secret scanning and synthetic-only fixture checks.
- Erasure end-to-end test across backend DB, AI DB, object store, Redis, and generated PDFs.
