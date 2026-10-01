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

The coordinator commits revocation, an exact deletion inventory, per-store steps, and an `erase_ai_data` job together. It cancels affected jobs before purging their data, deletes external stores before product rows, and retains a safe audit tombstone. Leases and bounded backoff recover interrupted work; failed steps remain retryable and overdue requests emit an operator alert. Shared presentation/document versions remain available to surviving sessions; session-owned answer audio and PDFs are purged with the session. Project deletion removes all versions.

The scheduled raw-media sweep uses the recorded 30-day upload-intent deadline. It revokes the raw asset, removes its objects and source-linked derived measurements, and retains the Practice Session, transcripts, Evaluation, and Report. It never invokes the explicit asset cascade that deletes a dependent Practice Session.

Object inventory includes scoped backend-generated Q&A JSON and orphan objects under the target's ownership prefixes. The coordinator waits for existing upload grants to expire before its final inventory and purge, so a previously issued upload URL cannot recreate purged media. Legacy project requests are adopted by the coordinator with their original actor, request time, and deadline.

### Operating retention and erasure

Deploy the Backend migration and matching AI-ML worker contract together before enabling traffic. Keep `ERASURE_ENABLED=true`, with the default ten-second polling interval, batch size 50, and five-minute renewable lease. Every API process may run the coordinator: PostgreSQL row locks and lease tokens protect claims. Never disable the loop in production without a replacement coordinator. Keep object storage unversioned, or configure equivalent physical noncurrent-version erasure; deleting a current key in a versioned bucket alone is not physical erasure.

For rollback, stop deletion traffic and preserve the new durable tables and jobs until every accepted request is drained. Prefer a forward fix. The schema downgrade removes erasure jobs and audit tables, so it must not run over outstanding production requests. Existing signed download URLs can remain usable until their short TTL or object deletion; the application cannot revoke grants that have already left its control.

An accepted request is not a promise that unavailable dependencies will recover within 24 hours. The durable deadline, failed store, safe failure code, and retry count must be monitored. Route the `Erasure deadline exceeded` error to the operator alert channel. A dependency failure leaves resources revoked and retries the incomplete store with bounded exponential backoff. Restore the failed dependency rather than clearing steps or recreating deleted resources. To expedite an operator retry, set only that request's `next_attempt_at` to the current UTC time, leaving lease tokens, step statuses, counts, and inventories unchanged.

Use the authenticated `GET /api/v1/erasure-requests/{id}` for Team-visible progress. For operations, this read-only query lists actionable failures and overdue work without content or storage keys:

```sql
SELECT r.id, r.scope, r.scope_id, r.status, r.deadline_at,
       s.store, s.attempts, s.failure_code
FROM erasure_requests r
JOIN erasure_steps s ON s.request_id = r.id
WHERE r.status <> 'completed'
  AND (s.status = 'failed' OR r.deadline_at <= CURRENT_TIMESTAMP);
```

Redis cancellation removes only exact target task IDs from queue lists and unacknowledged deliveries. It waits for worker-reported active, reserved, and scheduled work to settle before deleting data. The AI worker checks revocation before starting and between stages, and fails closed if the backend cannot be reached. Completed requests retain only safe IDs, timestamps, statuses, and counts; temporary object inventories and dispatch payloads are removed.

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
