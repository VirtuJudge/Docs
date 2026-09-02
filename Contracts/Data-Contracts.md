# Data contracts

This document defines canonical concepts shared across APIs, jobs, stored artifacts, and generated clients. Service-owned schemas may add private persistence fields, but they may not change these meanings at a boundary.

## Common types

| Type | Representation | Constraints |
|---|---|---|
| `ResourceId` | string | 26-character ULID |
| `UtcTimestamp` | string | RFC 3339 UTC, for example `2026-09-02T12:30:00Z` |
| `DurationMs` | integer | `>= 0` |
| `Checksum` | string | `sha256:` plus 64 lowercase hex characters |
| `NormalizedScore` | number | `0.0 <= value <= 1.0` |
| `EmailAddress` | string | Normalized for comparison; original form may be retained for display |
| `ObjectReference` | object | Opaque artifact ID, checksum, media type, byte size; never a permanent public URL |
| `EntityVersion` | integer | Starts at 1 and increases on accepted state changes |

## Identity and team

### User

| Field | Type | Required | Notes |
|---|---|---:|---|
| `id` | `UserId` | Yes | Internal public ID, not OIDC subject |
| `display_name` | string | Yes | 1–100 characters |
| `email` | string | Yes | Returned only where permission allows |
| `created_at` | timestamp | Yes | UTC |

### Team

| Field | Type | Required | Notes |
|---|---|---:|---|
| `id` | `TeamId` | Yes | ULID |
| `name` | string | Yes | 1–120 characters |
| `role` | enum | Yes | `owner` or `member` for the current user |
| `member_count` | integer | Yes | `>= 1` |
| `created_at` | timestamp | Yes | UTC |
| `version` | integer | Yes | Used to form ETag |

### TeamInvitation

| Field | Type | Required | Notes |
|---|---|---:|---|
| `id` | `InvitationId` | Yes | ULID |
| `team_id` | `TeamId` | Yes | Owning team |
| `email` | string | Yes | Invited address |
| `role` | enum | Yes | MVP permits `member` |
| `status` | enum | Yes | `pending`, `accepted`, `expired`, `revoked` |
| `delivery_status` | enum | Yes | `queued`, `accepted_by_gmail`, `failed` |
| `delivery_attempts` | integer | Yes | Non-negative; safe status only |
| `expires_at` | timestamp | Yes | UTC |
| `created_at` | timestamp | Yes | UTC |

The acceptance token is write-only and appears only in the invitation email URL. It is stored hashed and never returned by a team-list endpoint.

### TeamMembership

| Field | Type | Required | Notes |
|---|---|---:|---|
| `team_id`, `user_id` | IDs | Yes | Composite identity |
| `role` | enum | Yes | `owner` or `member` |
| `display_name` | string | Yes | User display snapshot |
| `joined_at` | timestamp | Yes | UTC |
| `version` | integer | Yes | Optimistic concurrency |

### InvitationPreview

Contains `team_name`, inviter display name, invited email in masked form, `expires_at`, and status. It never contains membership lists, Project data, token hashes, or delivery-provider details.

## Project and asset

### Project

| Field | Type | Required | Notes |
|---|---|---:|---|
| `id` | `ProjectId` | Yes | ULID |
| `team_id` | `TeamId` | Yes | Immutable owner |
| `name` | string | Yes | 1–160 characters |
| `description` | string | No | At most 2,000 characters |
| `created_by` | `UserId` | Yes | Member who created it |
| `created_at`, `updated_at` | timestamp | Yes | UTC |
| `version` | integer | Yes | Optimistic concurrency |

### Asset

| Field | Type | Required | Notes |
|---|---|---:|---|
| `id` | `AssetId` | Yes | Logical asset |
| `version_id` | `AssetVersionId` | Yes | Immutable version |
| `project_id` | `ProjectId` | Yes | Ownership root |
| `kind` | enum | Yes | `presentation_video`, `supporting_document`, `answer_audio`, `report_pdf` |
| `state` | enum | Yes | `pending_upload`, `uploaded`, `verified`, `rejected`, `deleting`, `deleted` |
| `file_name` | string | Yes | Display only; never used as an object key |
| `media_type` | string | Yes | Verified server-side after upload |
| `size_bytes` | integer | Yes after upload | Non-negative |
| `checksum` | checksum | Yes after upload | SHA-256 |
| `duration_ms` | integer | Video/audio only | Verified duration |
| `created_by` | `UserId` | Yes | Uploader |
| `created_at` | timestamp | Yes | UTC |
| `retention_expires_at` | timestamp | Raw media only | Default 30-day boundary |

### UploadIntent

```json
{
  "asset_id": "01J...",
  "asset_version_id": "01J...",
  "upload_url": "https://short-lived-signed-url.example",
  "method": "PUT",
  "required_headers": {
    "content-type": "video/mp4"
  },
  "expires_at": "2026-09-02T12:45:00Z",
  "maximum_size_bytes": 524288000
}
```

Signed URLs are secrets and must not be stored in frontend logs, notifications, analytics, or telemetry.

### ObjectReference

| Field | Type | Required | Notes |
|---|---|---:|---|
| `artifact_id` | `ArtifactId` | Yes | Opaque logical reference resolved by an authorized service |
| `schema_version` | integer | Structured artifacts | Payload schema major version |
| `checksum` | checksum | Yes | Integrity and reuse key |
| `media_type` | string | Yes | Verified type |
| `size_bytes` | integer | Yes | Non-negative |

An `ObjectReference` never contains a permanent object key or public URL.

### DownloadIntent

Contains a short-lived signed `download_url`, `expires_at`, verified `media_type`, `size_bytes`, and safe suggested `file_name`. It is returned only after normal resource authorization.

## Practice Session

### SessionManifest

```json
{
  "schema_version": 1,
  "presentation": {
    "asset_id": "01J...",
    "asset_version_id": "01J...",
    "checksum": "sha256:..."
  },
  "supporting_documents": [
    {
      "asset_id": "01J...",
      "asset_version_id": "01J...",
      "checksum": "sha256:..."
    }
  ],
  "rubric": {"rubric_id": "startup_pitch", "version": 1},
  "consent": {"policy_version": 1, "confirmed_at": "2026-09-02T12:30:00Z"}
}
```

### PracticeSession

| Field | Type | Required | Notes |
|---|---|---:|---|
| `id` | `PracticeSessionId` | Yes | ULID |
| `project_id`, `team_id` | IDs | Yes | Ownership ancestry |
| `state` | enum | Yes | `draft`, `ready`, `analyzing`, `questions_ready`, `qa_in_progress`, `report_generating`, `completed`, `failed`, `cancelled` |
| `manifest` | `SessionManifest` | After start | Immutable once first attempt is created |
| `current_attempt` | integer | No | Starts at 1 |
| `current_question_id` | `QuestionId` | No | Present during Q&A when a question is active |
| `failure` | `SafeFailure` | No | Present for failed state |
| `limitations` | `Limitation[]` | Yes | Empty when none |
| `created_by` | `UserId` | Yes | Session creator |
| `created_at`, `updated_at` | timestamp | Yes | UTC |
| `version` | integer | Yes | Optimistic concurrency and SSE version |

### AnalysisAttempt

| Field | Type | Required | Notes |
|---|---|---:|---|
| `id` | `AnalysisAttemptId` | Yes | ULID |
| `practice_session_id` | ID | Yes | Parent session |
| `number` | integer | Yes | Starts at 1; unique per session |
| `status` | enum | Yes | `queued`, `running`, `completed`, `failed`, `cancelled` |
| `pipeline_version` | string | When started | Immutable |
| `stage_progress` | `StageProgress[]` | Yes | Current safe status for UI |
| `started_at`, `completed_at` | timestamp | No | UTC |
| `failure` | `SafeFailure` | No | Safe typed summary |

### AIJob

| Field | Type | Required | Notes |
|---|---|---:|---|
| `id` | `AIJobId` | Yes | Stable idempotency key shared by database, Redis, and callback |
| `practice_session_id` | ID | Yes | Parent session |
| `analysis_attempt` | integer | Yes | Current attempt number |
| `job_type` | enum | Yes | `analyze_session`, `analyze_answer`, `generate_report`, `erase_ai_data` |
| `status` | enum | Yes | `pending`, `queued`, `running`, `completed`, `failed`, `cancelled` |
| `last_update_sequence` | integer | Yes | Starts at 0; only larger worker updates apply |
| `payload_version` | integer | Yes | Queue job schema version |
| `attempts` | integer | Yes | Worker execution attempts |
| `cancel_requested` | boolean | Yes | Checked between expensive stages |
| `created_at`, `updated_at` | timestamp | Yes | UTC |
| `failure` | `SafeFailure` | On failure | Safe user/operator summary |

### Page

List endpoints return `{items, next_cursor?}`. The cursor is opaque, the default page size is 20, and the maximum is 100.

### StageProgress

| Field | Type | Required | Notes |
|---|---|---:|---|
| `stage` | enum | Yes | `ingestion`, `speech`, `diarization`, `vision`, `audio_features`, `documents`, `aggregation`, `grounding`, `questions`, `answers`, `report` |
| `status` | enum | Yes | `pending`, `running`, `completed`, `failed`, `skipped`, `cancelled` |
| `progress` | number | Yes | `0.0`–`1.0`; stage estimate, not total truth |
| `started_at`, `completed_at` | timestamp | No | UTC |
| `limitation_code` | string | No | Safe documented code |

## Speakers and timed artifacts

### DerivedArtifact

| Field | Type | Required | Notes |
|---|---|---:|---|
| `id` | `ArtifactId` | Yes | ULID |
| `kind` | enum | Yes | `transcript`, `speaker_turns`, `speaker_preview`, `vision_observations`, `audio_observations`, `document_chunks`, `embeddings`, `analysis`, `answer_assessment`, `evaluation`, `report` |
| `schema_version` | integer | Yes | Major payload version |
| `practice_session_id` | ID | Yes | Ownership root |
| `analysis_attempt` | integer | Yes | Producing attempt |
| `object` | `ObjectReference` | When stored as an object | Checksummed reference |
| `created_at` | timestamp | Yes | UTC |
| `producer_version` | string | Yes | Pipeline/stage version |
| `source_artifact_ids` | ID[] | Yes | Inputs used to derive it |

AI/ML owns the derived record and object. The backend persists only validated references and user-facing canonical data.

### SpeakerMapping

| Field | Type | Required | Notes |
|---|---|---:|---|
| `speaker_label` | string | Yes | AI label such as `SPEAKER_00` |
| `user_id` | `UserId` | No | Present when mapped to a member |
| `display_name` | string | No | Snapshot used in the report |
| `confirmed_by` | `UserId` | Yes | Member performing mapping |
| `confirmed_at` | timestamp | Yes | UTC |

### TranscriptSegment

| Field | Type | Required | Notes |
|---|---|---:|---|
| `id` | string | Yes | Stable within artifact version |
| `start_ms`, `end_ms` | integer | Yes | `0 <= start < end <= duration` |
| `text` | string | Yes | UTF-8 transcript |
| `speaker_label` | string | No | Diarization label, not a person identity |
| `words` | `TranscriptWord[]` | No | Word text and start/end timestamps |
| `language` | string | No | BCP 47 when known |

### DocumentChunk

| Field | Type | Required | Notes |
|---|---|---:|---|
| `id` | string | Yes | Stable for asset/checksum/chunking version |
| `asset_version_id` | ID | Yes | Supporting Document version |
| `page_or_slide` | integer | Yes | One-based source location |
| `text` | string | Yes | Extracted bounded text |
| `start_offset`, `end_offset` | integer | When extractor provides them | Source-local offsets |
| `extraction_method` | string | Yes | Parser and version |
| `chunking_version` | string | Yes | Chunk policy version |
| `embedding_model` | string | After embedding | Provider/model identifier |
| `embedding_dimensions` | integer | After embedding | Positive dimension count |

### Observation contracts

| Contract | Required fields |
|---|---|
| `VisualObservation` | `start_ms`, `end_ms`, `metric`, numeric `value`, `unit`, `source_artifact_id`, optional `speaker_label` |
| `AudioObservation` | `start_ms`, `end_ms`, `metric`, numeric `value`, `unit`, `source_artifact_id`, optional `speaker_label` |
| `SpeakerTurn` | `start_ms`, `end_ms`, `speaker_label`, `source_artifact_id` |

Metrics are allow-listed and versioned. They describe observable measurements, not confidence, emotion, honesty, anxiety, personality, or mental state.

## Evidence, scoring, and evaluation

### AnalysisArtifact

The analysis artifact is produced before Q&A. It contains validated transcript, speaker-label, observation, document-retrieval, evidence, finding, limitation, and reproducibility references used to create the three primary questions. It may contain provisional per-dimension measurements, but it does not contain the final Q&A-inclusive overall score and is not the final Evaluation.

### Rubric

| Field | Type | Required | Notes |
|---|---|---:|---|
| `id` | string | Yes | Stable ID such as `startup_pitch` |
| `version` | integer | Yes | Immutable published version |
| `name` | string | Yes | User-facing label |
| `dimensions` | `RubricDimension[]` | Yes | Unique IDs; weights total `1.0` |
| `published_at` | timestamp | Yes | UTC |

Each `RubricDimension` contains `id`, `name`, `description`, normalized `weight`, scope (`team`, `individual`, or `both`), descriptors for the four labels, and required evidence types.

### EvidenceReference

```json
{
  "id": "ev_01J...",
  "type": "document_span",
  "source": {
    "asset_version_id": "01J...",
    "page_or_slide": 4,
    "chunk_id": "chunk_012",
    "start_offset": 120,
    "end_offset": 284
  },
  "excerpt": "Optional short excerpt safe for the report"
}
```

`type` is one of `transcript_span`, `video_interval`, `audio_interval`, `document_span`, or `answer_span`. The selected `source` shape is validated by type. Excerpts are bounded and never replace the canonical artifact.

### ScoreComponent

| Field | Type | Required | Notes |
|---|---|---:|---|
| `dimension` | enum | Yes | Rubric dimension ID |
| `status` | enum | Yes | `scored` or `not_evaluated` |
| `normalized_score` | number | If scored | `0.0`–`1.0` |
| `display_score` | integer | If scored | Rounded `0`–`100` |
| `label` | enum | If scored | `needs_work`, `developing`, `good`, `strong` |
| `configured_weight` | number | Yes | Original rubric weight |
| `effective_weight` | number | If scored | Weight after transparent normalization |
| `evidence_ids` | string[] | If scored | At least one |
| `rationale` | string | If scored | Bounded, user-safe explanation |
| `limitation_code` | string | If not evaluated | Why scoring was unavailable |

Default label boundaries on the displayed `0`–`100` scale are `[0,40)` `needs_work`, `[40,60)` `developing`, `[60,80)` `good`, and `[80,100]` `strong`. Effective weights are normalized only across dimensions that the system could not evaluate. An explicitly skipped Q&A response contributes zero to Q&A rather than removing that configured weight.

### Finding

| Field | Type | Required | Notes |
|---|---|---:|---|
| `id` | string | Yes | Stable within the Evaluation |
| `kind` | enum | Yes | `strength`, `improvement`, `alignment`, `contradiction`, `omission`, `observation` |
| `title` | string | Yes | Short user-facing heading |
| `detail` | string | Yes | Concrete explanation |
| `recommendation` | string | No | Action the team/member can take |
| `evidence_ids` | string[] | Yes | At least one unless the finding is an explicit limitation |
| `rubric_dimension` | string | No | Related dimension |
| `speaker_labels` | string[] | No | Only confirmed/mapped labels for individual findings |

### FeedbackSection

Contains `summary`, `strengths`, `improvements`, `score_components`, and `limitations`. Strengths and improvements are arrays of `Finding`; the section cannot be empty without a limitation explaining why.

### Evaluation

| Field | Type | Required | Notes |
|---|---|---:|---|
| `id` | `EvaluationId` | Yes | ULID |
| `analysis_attempt_id` | ID | Yes | Analysis source for the final evaluation |
| `qa_round_id` | ID | Yes | Completed Q&A source |
| `rubric` | `{id, version}` | Yes | Immutable |
| `overall_score` | number | When at least one dimension scored | Normalized score |
| `components` | `ScoreComponent[]` | Yes | Exactly one per configured dimension |
| `findings` | `Finding[]` | Yes | Each contains evidence or a limitation |
| `team_feedback` | `FeedbackSection` | Yes | Whole-team assessment |
| `member_feedback` | `MemberFeedback[]` | Yes | One per mapped member |
| `limitations` | `Limitation[]` | Yes | Explicit missing/failed stages |
| `reproducibility` | `ReproducibilityMetadata` | Yes | Versions, checksums, timings, cost |

### MemberFeedback

| Field | Type | Required | Notes |
|---|---|---:|---|
| `user_id` | `UserId` | Yes | Mapped team member |
| `display_name` | string | Yes | Report snapshot |
| `speaker_labels` | string[] | Yes | One or more confirmed labels |
| `summary` | string | Yes | Individual feedback, not a ranking |
| `strengths` | `Finding[]` | Yes | Evidence-linked |
| `improvements` | `Finding[]` | Yes | Evidence-linked and actionable |
| `delivery_components` | `ScoreComponent[]` | Yes | Applicable individual dimensions |
| `qa_feedback` | `FeedbackSection` | No | Only if this member answered |

## Q&A

### QARound

| Field | Type | Required | Notes |
|---|---|---:|---|
| `id` | `QARoundId` | Yes | One per Practice Session |
| `practice_session_id` | ID | Yes | Parent |
| `state` | enum | Yes | `not_started`, `in_progress`, `completed` |
| `questions` | `Question[]` | Yes | Ordered; exactly 3 primary, at most 2 follow-up when complete |
| `answers` | `Answer[]` | Yes | Submitted/skipped plus active draft metadata for caller |
| `current_question_id` | `QuestionId` | No | Present while active |
| `follow_up_count` | integer | Yes | `0`–`2` |
| `version` | integer | Yes | Optimistic concurrency |

### Question

| Field | Type | Required | Notes |
|---|---|---:|---|
| `id` | `QuestionId` | Yes | ULID |
| `practice_session_id` | ID | Yes | Parent |
| `kind` | enum | Yes | `primary` or `follow_up` |
| `position` | integer | Yes | 1–5 |
| `text` | string | Yes | 1–1,000 characters |
| `reason` | string | Yes | Why it was asked |
| `rubric_dimension` | string | Yes | Target dimension ID |
| `evidence_ids` | string[] | Yes | At least one grounded reference |
| `parent_answer_id` | `AnswerId` | Follow-up only | Earlier answer that triggered it |
| `state` | enum | Yes | `pending`, `active`, `answered`, `skipped` |

### Answer

| Field | Type | Required | Notes |
|---|---|---:|---|
| `id` | `AnswerId` | Yes | ULID |
| `question_id` | `QuestionId` | Yes | Parent question |
| `answered_by` | `UserId` | Yes | Member submitting or skipping |
| `status` | enum | Yes | `draft`, `submitted`, `skipped` |
| `audio_asset_version_id` | ID | Submitted audio only | Verified answer audio |
| `transcript_artifact_id` | ID | After processing | Derived transcript |
| `duration_ms` | integer | Submitted audio only | Recommended maximum 120,000 |
| `submitted_at` | timestamp | Submitted/skipped | UTC |

Draft recordings may be replaced. Submission is immutable; correcting it requires an explicit future product decision rather than overwriting evidence.

## Report

### ReportPayload

```json
{
  "schema_version": 1,
  "report_id": "01J...",
  "practice_session_id": "01J...",
  "evaluation_id": "01J...",
  "title": "Demo Day practice: 2 September 2026",
  "executive_summary": "...",
  "overall_score": 0.74,
  "score_components": [],
  "team_feedback": {},
  "member_feedback": [],
  "transcript_timeline": [],
  "document_alignment": [],
  "qa_review": [],
  "recommendations": [],
  "limitations": [],
  "reproducibility": {},
  "generated_at": "2026-09-02T12:30:00Z"
}
```

The backend validates this payload, creates the canonical Report, and separately renders a PDF. The AI artifact alone is not a user-visible report.

### ReportExport

| Field | Type | Required | Notes |
|---|---|---:|---|
| `id` | `ReportExportId` | Yes | ULID |
| `report_id` | `ReportId` | Yes | Canonical source |
| `format` | enum | Yes | MVP value `pdf` |
| `status` | enum | Yes | `queued`, `rendering`, `ready`, `failed` |
| `asset_version_id` | ID | When ready | Private PDF asset |
| `created_at`, `completed_at` | timestamp | As applicable | UTC |
| `failure` | `SafeFailure` | On failure | Safe summary |

## Safe failures and limitations

### SafeFailure

| Field | Type | Required | Notes |
|---|---|---:|---|
| `code` | string | Yes | Stable allow-listed code |
| `stage` | string | No | Failed stage |
| `retryable` | boolean | Yes | User-facing retry eligibility |
| `message` | string | Yes | Safe explanation |
| `trace_id` | string | Yes | Operator correlation |

### Limitation

| Field | Type | Required | Notes |
|---|---|---:|---|
| `code` | string | Yes | Stable code such as `documents_not_provided` |
| `scope` | string | Yes | Stage, rubric dimension, member, or report section |
| `message` | string | Yes | Clear user-facing effect |
| `affected_dimensions` | string[] | Yes | Empty if none |

## Erasure

### ErasureRequest

| Field | Type | Required | Notes |
|---|---|---:|---|
| `id` | `ErasureRequestId` | Yes | ULID |
| `scope` | enum | Yes | `asset`, `practice_session`, `project`, or `team` |
| `scope_id` | Resource ID | Yes | Target |
| `status` | enum | Yes | `pending`, `in_progress`, `completed`, `failed` |
| `requested_by` | `UserId` | Yes | Owner initiating deletion |
| `requested_at`, `deadline_at` | timestamp | Yes | Physical deletion deadline is within 24 hours |
| `completed_at` | timestamp | No | UTC |
| `steps` | `ErasureStep[]` | Yes | Product tables, AI tables, objects, Redis/cache, PDF |

Each `ErasureStep` contains `store`, status, attempt count, and safe completion/failure metadata. Deleted content is never copied into the Erasure Request.

## ReproducibilityMetadata

Required fields are `pipeline_version`, `rubric_id`, `rubric_version`, `prompt_versions`, `contract_versions`, `input_checksums`, `stage_versions`, `model_runs`, `started_at`, `completed_at`, `duration_ms`, and `cost_summary` when available. Each model run records capability, provider, model ID/version, adapter version, relevant parameters, token/compute measures, duration, and cost. It never records secrets or hidden reasoning.
