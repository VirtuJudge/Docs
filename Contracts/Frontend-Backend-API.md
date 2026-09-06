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

Allowed inputs across the full product are:
- presentation: MP4 or WebM, one per session, at most 500 MB and 10 minutes;
- supporting document: PDF or PPTX, at most five per session and 25 MB each;
- answer audio: browser-supported audio normalized by ingestion, recommended maximum 2 minutes.

In the initial PDF slice, only `supporting_document` with `.pdf` extension and `application/pdf` media type up to 25 MiB is accepted.

The returned upload URL is a signed S3 SigV4 PUT URL. Its `X-Amz-SignedHeaders` enforces `content-length`, `content-type`, and `if-none-match: *` to prevent object overwrite. Browsers populate `Content-Length` automatically from the upload Blob length.

Important errors (returned as `application/problem+json`):
- `404 not_found`: unknown project, outsider user, or project erasure requested (concealment)
- `409 conflict`: idempotency key reused with different request payload
- `413 payload_too_large`: declared size exceeds 25 MiB limit
- `415 unsupported_media_type`: unsupported kind, non-PDF file extension, or unsupported media type
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

The server streams uploaded bytes from storage to bounded temporary disk, verifies observed length, recalculates SHA-256, and inspects PDF structure and page tree using a parser.

Returns `202 Asset` in `verified` state upon success.

Repeated completions returning the same verified version succeed when checksum and size match. Conflicting completions or attempts to complete an already rejected version return `409 conflict`.

When validation fails, the version is committed as `rejected` with a safe `rejection_reason` before returning `422 unprocessable_entity`.

Important errors (returned as `application/problem+json`):
- `404 not_found`: unknown asset or version, outsider user, or project erasure requested
- `409 conflict`: mismatch against existing verified version, or version already rejected
- `413 payload_too_large`: observed size exceeds limit
- `422 unprocessable_entity`: invalid values, checksum mismatch, size mismatch, corrupt PDF, or encrypted PDF
- `503 service_unavailable`: transient object storage connectivity failure or verifier unavailable

### Asset endpoints

| Method | Path | Request | Success | Notes |
|---|---|---|---|---|
| `GET` | `/projects/{project_id}/assets` | query `cursor`, `limit` (1-100, default 20), `kind`, `state` | `200 Page<Asset>` | Filter by `kind` and `state` |
| `GET` | `/assets/{asset_id}` | None | `200 Asset` | Team permission required |
| `POST` | `/assets/{asset_id}/download-intents` | None | `200 DownloadIntent` | Short-lived signed GET URL for verified assets |
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

- Media type: `text/event-stream`
- Authentication required.
- Supports `Last-Event-ID`.
- Sends a heartbeat comment every 15 seconds.
- Event retention is best effort; clients refetch the session after reconnect or a sequence gap.

Example:

```text
id: 184
event: practice_session.updated.v1
data: {"sequence":184,"practice_session_id":"01J...","resource_version":12,"state":"questions_ready","occurred_at":"2026-09-02T12:30:00Z","trace_id":"01J..."}
```

Frontend-visible SSE event types:

- `practice_session.updated.v1`
- `practice_session.analysis_progressed.v1`
- `qa.question_available.v1`
- `qa.answer_updated.v1`
- `report.ready.v1`
- `erasure.updated.v1`

SSE payloads contain identifiers and safe status only. The frontend fetches the corresponding resource for canonical data.

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
