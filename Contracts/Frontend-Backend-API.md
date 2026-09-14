# Frontend/backend API contract

## Protocol

- Base path: `/api/v1`
- JSON media type: `application/json`
- Errors: `application/problem+json`
- Authentication: OIDC bearer JWT unless marked public
- Async commands: return `202 Accepted` with the current resource and `Location`
- Resource creation: return `201 Created`
- Deletion request: return `202 Accepted` with an Erasure Request
- Conditional changes: use `ETag` and `If-Match`
- Retried commands: require `Idempotency-Key`

The field definitions in [Data Contracts](./Data-Contracts.md) are normative for the Markdown design.

## Identity and teams

| Method | Path | Request | Success | Important errors |
|---|---|---|---|---|
| `GET` | `/me` | None | `200 User` | `401 invalid_token` |
| `GET` | `/teams` | cursor query | `200 Page<Team>` | None |
| `POST` | `/teams` | `{name}` | `201 Team` | `409 team_name_conflict` |
| `GET` | `/teams/{team_id}` | None | `200 Team` | `403`, `404` |
| `PATCH` | `/teams/{team_id}` | `{name}` + `If-Match` | `200 Team` | `403`, `412` |
| `GET` | `/teams/{team_id}/members` | cursor query | `200 Page<TeamMembership>` | `403` |
| `DELETE` | `/teams/{team_id}/members/{user_id}` | confirmation | `204` | `403`, `409 last_owner` |
| `POST` | `/teams/{team_id}/invitations` | `{email, role:"member"}` | `201 TeamInvitation` | `403`, `409 already_member`, `429` |
| `GET` | `/teams/{team_id}/invitations` | cursor query | `200 Page<TeamInvitation>` | `403` |
| `POST` | `/teams/{team_id}/invitations/{id}/resend` | empty + `Idempotency-Key` | `202 TeamInvitation` | `403`, `409 invitation_not_pending`, `429` |
| `DELETE` | `/teams/{team_id}/invitations/{id}` | `If-Match` | `204` | `403`, `409 already_consumed` |
| `GET` | `/invitations/{token}` | public token | `200 InvitationPreview` | `404`, `410 invitation_expired` |
| `POST` | `/invitations/{token}/accept` | authenticated, empty body | `200 TeamMembership` | `409 email_mismatch`, `410` |

Invitation creation schedules a Gmail send after commit. A Gmail-delivery failure does not delete the invitation; the owner sees its delivery state and may resend with a new idempotent command.

## Projects

| Method | Path | Request | Success | Important errors |
|---|---|---|---|---|
| `GET` | `/teams/{team_id}/projects` | cursor, optional search | `200 Page<Project>` | `403` |
| `POST` | `/teams/{team_id}/projects` | `{name, description?}` | `201 Project` | `422` |
| `GET` | `/projects/{project_id}` | None | `200 Project` | `403`, `404` |
| `PATCH` | `/projects/{project_id}` | `{name?, description?}` + `If-Match` | `200 Project` | `403`, `412` |
| `DELETE` | `/projects/{project_id}` | `{confirmation}` + `Idempotency-Key` | `202 ErasureRequest` | `403`, `409` |

## Assets and direct uploads

Backend endpoints use RFC 4122 UUID strings for `project_id`, `asset_id`, `version_id`, `user_id`, and `team_id` for compatibility with BE-01 persistence.

### Create upload intent

`POST /projects/{project_id}/assets/upload-intents`

Headers: `Idempotency-Key` required. Scoped to actor, project, operation, and key.

```json
{
  "kind": "supporting_document",
  "file_name": "demo-slides.pdf",
  "declared_media_type": "application/pdf",
  "declared_size_bytes": 241172
}
```

Returns `201 UploadIntent`.

Accepted upload combinations are:

| Kind | Extensions and declared MIME types | Byte limit | Verified duration limit |
|---|---|---|---|
| `supporting_document` | `.pdf`: `application/pdf`; `.pptx`: `application/vnd.openxmlformats-officedocument.presentationml.presentation` | 25 MiB | None |
| `presentation_video` | `.mp4`: `video/mp4`; `.webm`: `video/webm` | 500 MiB | 600,000 ms |
| `answer_audio` | `.webm`: `audio/webm`; `.ogg`: `audio/ogg`; `.mp4` or `.m4a`: `audio/mp4`; `.wav`: `audio/wav` | 25 MiB | 120,000 ms |

Clients must send the canonical MIME type without codec parameters. Media verification checks the actual container, supported codecs, required tracks, and full decoded duration; uploads are not transcoded by this endpoint. Presentation video requires a video track, while answer audio must contain audio and no video. Browser WebM without a duration header uses decoded duration. `duration_ms` is measured by the backend and persisted on the Asset and AssetVersion. Raw media receives `retention_expires_at` 30 days after its upload intent was created. This timestamp records the retention boundary; the separate erasure workflow owns physical raw-media purging. Session attachment counts are enforced by the session workflow.

The returned upload URL is a signed S3 SigV4 PUT URL. Its `X-Amz-SignedHeaders` enforces `content-length`, `content-type`, and `if-none-match: *` to prevent object overwrite. Browsers populate `Content-Length` automatically from the upload Blob length.

Important errors (returned as `application/problem+json`):
- `404 not_found`: unknown project, outsider user, or project erasure requested (concealment)
- `409 conflict`: idempotency key reused with different request payload, replay of expired upload intent, or replay for version in terminal or deleting state
- `413 payload_too_large`: declared size exceeds the kind-specific byte limit
- `415 unsupported_media_type`: unsupported kind, extension/MIME combination, or media type
- `422 validation_failed`: invalid request fields or non-positive size

### Create version upload intent

`POST /assets/{asset_id}/versions/upload-intents`

Headers: `Idempotency-Key` required. Scoped to actor, project, asset, operation, and key.

```json
{
  "file_name": "updated-slides.pptx",
  "declared_media_type": "application/vnd.openxmlformats-officedocument.presentationml.presentation",
  "declared_size_bytes": 524288
}
```

Returns `201 UploadIntent`. Only supporting documents accept replacement. A replacement creates a new immutable version with unique number and storage key under the same logical asset. The previously verified version remains available and current while replacement is pending or rejected. Advancing the logical asset current version occurs only on successful newer completion.

Important errors (returned as `application/problem+json`):
- `404 not_found`: unknown asset, outsider user, or project erasure requested
- `409 conflict`: idempotency key reused with different request payload, replay of expired upload intent, replay for version in terminal or deleting state, or asset is not a supporting document
- `413 payload_too_large`: declared size exceeds 25 MiB limit
- `415 unsupported_media_type`: unsupported extension or media type
- `422 validation_failed`: invalid request fields or non-positive size

### Complete upload

`POST /assets/{asset_id}/versions/{version_id}/complete`

Headers: `Idempotency-Key` required.

```json
{
  "checksum": "sha256:4b227777d4dd1fc61c6f884f48641d02b4d121d3fd328cb08b5531fcacdabf8a",
  "size_bytes": 241172
}
```

The server streams uploaded bytes from storage to bounded temporary disk, verifies observed length, recalculates SHA-256, and inspects PDF structure and page tree or OOXML presentation package relationships and slide definitions using an isolated worker parser.

Returns `202 Asset` in `verified` state upon success, representing the exact version completed.

Repeated completions returning the same verified version succeed when checksum and size match. Conflicting completions or attempts to complete an already rejected or deleting/deleted version return `409 conflict` while the logical asset survives. If cleanup deletes the logical asset because no usable version remains, later access is concealed with `404 not_found`. Replays after completion do not alter records.

When validation fails, the version is committed as `rejected` with a safe `rejection_reason` before returning `422 unprocessable_entity`. If the asset previously had a verified version, that version remains current.

Important errors (returned as `application/problem+json`):
- `404 not_found`: unknown or cleanup-deleted asset or version, outsider user, or project erasure requested
- `409 conflict`: mismatch against existing verified version, version in deleting or deleted state, or version already rejected
- `413 payload_too_large`: observed size exceeds limit
- `422 unprocessable_entity`: invalid values, checksum mismatch, size mismatch, corrupt document, or encrypted document
- `503 service_unavailable`: transient object storage connectivity failure or verifier unavailable

### Asset endpoints

| Method | Path | Request | Success | Notes |
|---|---|---|---|---|
| `GET` | `/projects/{project_id}/assets` | query `cursor`, `limit` (1-100, default 20), `kind`, `state` | `200 Page<Asset>` | Filter by `kind` and `state` |
| `GET` | `/assets/{asset_id}` | None | `200 Asset` | Team permission required |
| `POST` | `/assets/{asset_id}/versions/upload-intents` | metadata sans kind + `Idempotency-Key` | `201 UploadIntent` | Supporting documents only |
| `GET` | `/assets/{asset_id}/versions` | query `cursor`, `limit` (1-100, default 20) | `200 Page<AssetVersion>` | List versions of asset |
| `GET` | `/assets/{asset_id}/versions/{version_id}` | None | `200 AssetVersion` | Exact version details |
| `POST` | `/assets/{asset_id}/versions/{version_id}/download-intents` | None | `200 DownloadIntent` | Signed GET URL for verified version |
| `POST` | `/assets/{asset_id}/download-intents` | None | `200 DownloadIntent` | Short-lived signed GET URL for verified current version |
| `DELETE` | `/assets/{asset_id}` | None | `202 ErasureRequest` | Fails when immutable active manifest still requires asset |

## Practice Sessions

### Create draft

`POST /projects/{project_id}/practice-sessions`

```json
{
  "name": "Demo Day practice",
  "presentation_asset_version_id": "01J...",
  "supporting_document_version_ids": ["01J..."],
  "rubric": {"rubric_id": "startup_pitch", "version": 1}
}
```

Returns `201 PracticeSession`. The backend validates ownership and asset state. The manifest becomes immutable when analysis starts.

### Session endpoints

| Method | Path | Request | Success | Important errors |
|---|---|---|---|---|
| `GET` | `/projects/{project_id}/practice-sessions` | cursor, state filter | `200 Page<PracticeSessionSummary>` | `403` |
| `GET` | `/practice-sessions/{session_id}` | None | `200 PracticeSession` | `403`, `404` |
| `PATCH` | `/practice-sessions/{session_id}` | draft fields + `If-Match` | `200 PracticeSession` | `409 manifest_frozen`, `412` |
| `POST` | `/practice-sessions/{session_id}/analysis-attempts` | consent + `Idempotency-Key` | `202 AnalysisAttempt` | `409 session_not_ready`, `422 consent_required` |
| `GET` | `/practice-sessions/{session_id}/analysis-attempts` | None | `200 AnalysisAttempt[]` | `403` |
| `POST` | `/practice-sessions/{session_id}/cancel` | `{reason?}` + idempotency | `202 PracticeSession` | `403`, `409 terminal_state` |
| `POST` | `/practice-sessions/{session_id}/retries` | empty + idempotency | `202 AnalysisAttempt` | `403`, `409 retry_not_allowed` |
| `PUT` | `/practice-sessions/{session_id}/speaker-mappings` | mappings + `If-Match` | `200 SpeakerMapping[]` | `409 analysis_not_ready`, `422 invalid_label` |

Analysis start request:

```json
{
  "consent": {
    "accepted": true,
    "policy_version": 1
  }
}
```

Speaker mapping request:

```json
{
  "mappings": [
    {"speaker_label": "SPEAKER_00", "user_id": "01J..."},
    {"speaker_label": "SPEAKER_01", "user_id": "01J..."}
  ]
}
```

Each user may appear once unless the diarization correction flow explicitly joins multiple labels. Unknown labels or users outside the team are rejected.

## Q&A

| Method | Path | Request | Success | Important errors |
|---|---|---|---|---|
| `GET` | `/practice-sessions/{session_id}/qa` | None | `200 QARound` | `409 questions_not_ready` |
| `POST` | `/questions/{question_id}/answer-upload-intents` | file metadata + idempotency | `201 {answer, upload_intent}` | `409 question_not_active` |
| `POST` | `/answers/{answer_id}/submit` | checksum/size + idempotency | `202 Answer` | `409 already_submitted`, `422 duration_exceeded` |
| `POST` | `/questions/{question_id}/skip` | `{reason?}` + idempotency | `200 Answer` with `skipped` | `409 question_not_active` |

Only one question is active at a time. A draft recording may be replaced before submission. Submitted and skipped answers are immutable. The backend advances the current question atomically and never creates more than three primary and two follow-up questions.

## Evaluations and reports

| Method | Path | Success | Important errors |
|---|---|---|---|
| `GET` | `/practice-sessions/{session_id}/evaluation` | `200 Evaluation` | `409 evaluation_not_ready` |
| `GET` | `/practice-sessions/{session_id}/report` | `200 ReportPayload` | `409 report_not_ready` |
| `POST` | `/practice-sessions/{session_id}/report/pdf` | `202 ReportExport` | `409 report_not_ready` |
| `GET` | `/report-exports/{export_id}` | `200 ReportExport` | `403`, `404` |
| `POST` | `/report-exports/{export_id}/download-intents` | `200 DownloadIntent` | `409 export_not_ready` |
| `DELETE` | `/practice-sessions/{session_id}` | `202 ErasureRequest` | `403`, `409 deletion_in_progress` |

`ReportPayload` always includes `team_feedback` and a `member_feedback` entry for every mapped member. A member with no reliable source evidence receives an explicit limitation rather than invented feedback.

The final Evaluation is created with the Report after Q&A. Before that point, the Practice Session exposes analysis findings and limitations without claiming a Q&A-inclusive overall score.

## Erasure status

`GET /erasure-requests/{request_id}` returns:

```json
{
  "id": "01J...",
  "scope": "practice_session",
  "scope_id": "01J...",
  "status": "in_progress",
  "requested_at": "2026-09-02T12:30:00Z",
  "deadline_at": "2026-09-03T12:30:00Z",
  "completed_at": null
}
```

Status is `pending`, `in_progress`, `completed`, or `failed`. User access is revoked when the request is accepted, not when the physical purge finishes.

## SSE session stream

`GET /practice-sessions/{session_id}/events`

### Transport and authentication

- Media type: `text/event-stream`
- Response headers: `Content-Type: text/event-stream`, `Cache-Control: no-cache`, `Connection: keep-alive`
- Authentication: Bearer authentication required via `Authorization: Bearer <token>` header.
- No tokens in query parameters: passing access tokens in URL query parameters is rejected with `401 Unauthorized` (`invalid_token`) to prevent token exposure in logs, proxies, and browser history.
- Authorization: verified through Team Membership ancestry for the Practice Session. Unauthorized callers receive `403 Forbidden` (or `404 Not Found` when concealing resource existence).
- Heartbeat: server emits comment line `: heartbeat` every 15 seconds to prevent proxy and client timeouts.

### Framing and sequence rules

- Every frame uses standard SSE format:
  ```text
  id: <sequence>
  event: <event_name>
  data: <json_payload>
  ```
- SSE `id` equals the numeric `sequence`.
- `sequence` is a positive, strictly monotonically increasing integer (`sequence >= 1`) scoped to the Practice Session.
- Every persisted event contains:
  - `sequence` (integer): strictly monotonic per-session event sequence number.
  - `practice_session_id` (string): ULID of the Practice Session.
  - `occurred_at` (string): RFC 3339 UTC timestamp.
  - `trace_id` (string): correlation identifier.

### Last-Event-ID behavior and recovery

- Reconnection cursor: clients supply `Last-Event-ID: <integer>` on reconnect.
- Rejection of invalid values: malformed or negative values (`< 0`) are rejected immediately with `400 Bad Request` (`application/problem+json`).
- Replay: when `Last-Event-ID` identifies an event retained in the backend buffer, the server replays all retained events with `sequence > Last-Event-ID` in strictly ascending order before streaming live events.
- Resync required triggers: the server emits `practice_session.resync_required.v1` when:
  - the client connects with no cursor (missing `Last-Event-ID`) on a session where events already occurred;
  - the supplied cursor has been trimmed or compacted past the retention buffer limit;
  - the cursor has expired beyond the retention window;
  - the supplied cursor is ahead of the current server sequence (future cursor).
- Gap recovery: if a client detects a sequence gap (`sequence != expected_sequence + 1`), or receives `practice_session.resync_required.v1`, the client must treat local stream state as desynchronized and refetch canonical resources via REST before processing further events.

### Strict privacy and content exclusions

SSE payloads contain identifiers, entity versions, public Stage names, numeric progress, and safe statuses only.

Strictly excluded from all SSE payloads:
- transcripts and transcript segments;
- prompts and instructions;
- Evidence content and excerpts;
- storage object keys;
- signed download or upload URLs;
- worker messages;
- provider request and response bodies;
- raw provider errors and stack traces.

### Reconciled event catalogue

Frontend-visible SSE event types:

- `practice_session.updated.v1`
- `practice_session.analysis_progressed.v1`
- `qa.question_available.v1`
- `qa.answer_updated.v1`
- `report.ready.v1`
- `erasure.updated.v1`
- `practice_session.resync_required.v1`

### Event specifications and examples

#### `practice_session.updated.v1`

Emitted when Practice Session state changes or session resource version advances.

| Field | Type | Required | Notes |
|---|---|---:|---|
| `sequence` | integer | Yes | Monotonic sequence number |
| `practice_session_id` | ID | Yes | ULID |
| `version` | integer | Yes | Session resource version (`EntityVersion`) |
| `state` | enum | Yes | `draft`, `ready`, `analyzing`, `questions_ready`, `qa_in_progress`, `report_generating`, `completed`, `failed`, `cancelled` |
| `current_attempt` | integer | No | Present when an Analysis Attempt is active |
| `occurred_at` | timestamp | Yes | UTC |
| `trace_id` | string | Yes | Correlation ID |

```text
id: 184
event: practice_session.updated.v1
data: {"sequence":184,"practice_session_id":"01J2X3Y4Z5A6B7C8D9E0F1G2H3","version":12,"state":"questions_ready","current_attempt":1,"occurred_at":"2026-09-02T12:30:00Z","trace_id":"01J2X3Y4Z5A6B7C8D9E0F1G2H4"}
```

#### `practice_session.analysis_progressed.v1`

Emitted when an Analysis Attempt stage changes status or reports progress.

| Field | Type | Required | Notes |
|---|---|---:|---|
| `sequence` | integer | Yes | Monotonic sequence number |
| `practice_session_id` | ID | Yes | ULID |
| `analysis_attempt_id` | ID | Yes | ULID of running Analysis Attempt |
| `analysis_attempt_number` | integer | Yes | Attempt number starting at 1 |
| `stage` | enum | Yes | Public Stage: `ingestion`, `speech`, `diarization`, `vision`, `audio_features`, `documents`, `aggregation`, `grounding`, `questions`, `answers`, `report` |
| `status` | enum | Yes | Stage status: `pending`, `running`, `completed`, `failed`, `skipped`, `cancelled` |
| `progress` | number | Yes | Normalized progress from `0.0` to `1.0` |
| `occurred_at` | timestamp | Yes | UTC |
| `trace_id` | string | Yes | Correlation ID |

```text
id: 185
event: practice_session.analysis_progressed.v1
data: {"sequence":185,"practice_session_id":"01J2X3Y4Z5A6B7C8D9E0F1G2H3","analysis_attempt_id":"01J2X3Y4Z5A6B7C8D9E0F1G2H5","analysis_attempt_number":1,"stage":"speech","status":"running","progress":0.45,"occurred_at":"2026-09-02T12:30:20Z","trace_id":"01J2X3Y4Z5A6B7C8D9E0F1G2H6"}
```

#### `qa.question_available.v1`

Emitted when a Primary Question or Follow-up Question becomes active for the session. Question text and Evidence content are omitted; clients refetch the Q&A Round (`GET /practice-sessions/{session_id}/qa`).

| Field | Type | Required | Notes |
|---|---|---:|---|
| `sequence` | integer | Yes | Monotonic sequence number |
| `practice_session_id` | ID | Yes | ULID |
| `qa_round_id` | ID | Yes | ULID of Q&A Round |
| `question_id` | ID | Yes | ULID of active Question |
| `position` | integer | Yes | Question position (1 to 5) |
| `kind` | enum | Yes | `primary` or `follow_up` |
| `state` | enum | Yes | `active` |
| `version` | integer | Yes | Q&A Round resource version |
| `occurred_at` | timestamp | Yes | UTC |
| `trace_id` | string | Yes | Correlation ID |

```text
id: 186
event: qa.question_available.v1
data: {"sequence":186,"practice_session_id":"01J2X3Y4Z5A6B7C8D9E0F1G2H3","qa_round_id":"01J2X3Y4Z5A6B7C8D9E0F1G2H7","question_id":"01J2X3Y4Z5A6B7C8D9E0F1G2H8","position":1,"kind":"primary","state":"active","version":3,"occurred_at":"2026-09-02T12:32:00Z","trace_id":"01J2X3Y4Z5A6B7C8D9E0F1G2H9"}
```

#### `qa.answer_updated.v1`

Emitted when an Answer is submitted or skipped. Audio references and transcripts are omitted; clients refetch the Q&A Round (`GET /practice-sessions/{session_id}/qa`).

| Field | Type | Required | Notes |
|---|---|---:|---|
| `sequence` | integer | Yes | Monotonic sequence number |
| `practice_session_id` | ID | Yes | ULID |
| `qa_round_id` | ID | Yes | ULID of Q&A Round |
| `question_id` | ID | Yes | ULID of answered or skipped Question |
| `answer_id` | ID | Yes | ULID of Answer |
| `status` | enum | Yes | `submitted` or `skipped` |
| `version` | integer | Yes | Q&A Round resource version |
| `occurred_at` | timestamp | Yes | UTC |
| `trace_id` | string | Yes | Correlation ID |

```text
id: 187
event: qa.answer_updated.v1
data: {"sequence":187,"practice_session_id":"01J2X3Y4Z5A6B7C8D9E0F1G2H3","qa_round_id":"01J2X3Y4Z5A6B7C8D9E0F1G2H7","question_id":"01J2X3Y4Z5A6B7C8D9E0F1G2H8","answer_id":"01J2X3Y4Z5A6B7C8D9E0F1G2HA","status":"submitted","version":4,"occurred_at":"2026-09-02T12:34:00Z","trace_id":"01J2X3Y4Z5A6B7C8D9E0F1G2HB"}
```

#### `report.ready.v1`

Emitted when Report generation finishes and the Report resource is ready. Scores, feedback, recommendations, and limitations are omitted; clients fetch the Report (`GET /practice-sessions/{session_id}/report`).

| Field | Type | Required | Notes |
|---|---|---:|---|
| `sequence` | integer | Yes | Monotonic sequence number |
| `practice_session_id` | ID | Yes | ULID |
| `report_id` | ID | Yes | ULID of Report |
| `evaluation_id` | ID | Yes | ULID of Evaluation |
| `status` | enum | Yes | `ready` |
| `version` | integer | Yes | Session resource version |
| `occurred_at` | timestamp | Yes | UTC |
| `trace_id` | string | Yes | Correlation ID |

```text
id: 188
event: report.ready.v1
data: {"sequence":188,"practice_session_id":"01J2X3Y4Z5A6B7C8D9E0F1G2H3","report_id":"01J2X3Y4Z5A6B7C8D9E0F1G2HC","evaluation_id":"01J2X3Y4Z5A6B7C8D9E0F1G2HD","status":"ready","version":15,"occurred_at":"2026-09-02T12:36:00Z","trace_id":"01J2X3Y4Z5A6B7C8D9E0F1G2HE"}
```

#### `erasure.updated.v1`

Emitted when an active Erasure Request targeting the Practice Session changes status. Deleted content is omitted; clients fetch the Erasure Request (`GET /erasure-requests/{request_id}`).

| Field | Type | Required | Notes |
|---|---|---:|---|
| `sequence` | integer | Yes | Monotonic sequence number |
| `practice_session_id` | ID | Yes | ULID |
| `erasure_request_id` | ID | Yes | ULID of Erasure Request |
| `status` | enum | Yes | `pending`, `in_progress`, `completed`, `failed` |
| `occurred_at` | timestamp | Yes | UTC |
| `trace_id` | string | Yes | Correlation ID |

```text
id: 189
event: erasure.updated.v1
data: {"sequence":189,"practice_session_id":"01J2X3Y4Z5A6B7C8D9E0F1G2H3","erasure_request_id":"01J2X3Y4Z5A6B7C8D9E0F1G2HF","status":"in_progress","occurred_at":"2026-09-02T12:37:00Z","trace_id":"01J2X3Y4Z5A6B7C8D9E0F1G2HG"}
```

#### `practice_session.resync_required.v1`

Emitted when the client cursor cannot be replayed from retained events or when stream desynchronization requires a full client state refetch. Clients must refetch the canonical Practice Session and related active resources.

| Field | Type | Required | Notes |
|---|---|---:|---|
| `sequence` | integer | Yes | Current head sequence on the server |
| `practice_session_id` | ID | Yes | ULID |
| `reason` | enum | Yes | `cursor_missing`, `cursor_trimmed`, `cursor_expired`, `cursor_future` |
| `current_sequence` | integer | Yes | Current head sequence on the server |
| `requested_sequence` | integer | No | Sequence requested in `Last-Event-ID`, or `null` if absent |
| `occurred_at` | timestamp | Yes | UTC |
| `trace_id` | string | Yes | Correlation ID |

```text
id: 189
event: practice_session.resync_required.v1
data: {"sequence":189,"practice_session_id":"01J2X3Y4Z5A6B7C8D9E0F1G2H3","reason":"cursor_trimmed","current_sequence":189,"requested_sequence":120,"occurred_at":"2026-09-02T12:38:00Z","trace_id":"01J2X3Y4Z5A6B7C8D9E0F1G2HH"}
```

## Pagination

```json
{
  "items": [],
  "next_cursor": "opaque-or-absent"
}
```

Clients must not inspect cursor contents. Default page size is 20; maximum is 100.

## HTTP status policy

| Status | Use |
|---:|---|
| `200` | Successful query or command returning an existing resource |
| `201` | Resource or upload intent created |
| `202` | Accepted asynchronous operation |
| `204` | Completed deletion/revocation with no body |
| `400` | Malformed syntax |
| `401` | Missing or invalid identity |
| `403` | Authenticated but not permitted; do not reveal cross-team existence |
| `404` | Resource absent or deliberately concealed |
| `409` | Valid command conflicts with current domain state |
| `410` | Expired or consumed invitation token |
| `412` | ETag/version precondition failed |
| `413` | Declared or observed payload too large |
| `415` | Unsupported media type |
| `422` | Well-formed request violates field or domain validation |
| `429` | Rate limit or configured budget exceeded |
