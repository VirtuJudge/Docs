# Requirements and success measures

## Functional requirements

| ID | Requirement | MVP acceptance measure |
|---|---|---|
| FR-01 | Team access | An owner can invite a member by email; the single-use link expires and creates one membership. |
| FR-02 | Project material | A member can manage versioned presentation and supporting-document assets within configured limits. |
| FR-03 | Immutable attempt | Starting analysis freezes the session manifest. Changing an input requires a new session. |
| FR-04 | Multimodal analysis | Speech, diarization, vision, and audio-feature stages run independently and expose progress. |
| FR-05 | Grounding | Questions and findings contain typed evidence references to presentation, documents, or answers. |
| FR-06 | Adaptive Q&A | A session contains three primary questions and no more than two follow-ups. |
| FR-07 | Recovery | Refreshing or reconnecting restores the current Q&A state without duplicate submissions. |
| FR-08 | Scoring | Results use the versioned rubric and retain raw normalized scores, weights, labels, and evidence. |
| FR-09 | Feedback | The report contains a team section and a separate section for every mapped member. |
| FR-10 | Export | A completed report can be rendered as a private PDF. |
| FR-11 | Erasure | An owner can request deletion; access is revoked immediately and physical erasure completes within 24 hours. |
| FR-12 | Retry | A failed session can start a new numbered analysis attempt without overwriting history. |

## Default rubric

| Dimension | Weight | Scope |
|---|---:|---|
| Pitch content and evidence | 25% | Team |
| Business and problem–solution reasoning | 20% | Team |
| Technical feasibility | 15% | Team |
| Delivery and body language | 15% | Team and individual |
| Timing and speech mechanics | 5% | Team and individual |
| Q&A quality | 20% | Team and answering members |

Scores are stored from `0.0` to `1.0` and displayed from `0` to `100`. Labels are `needs_work`, `developing`, `good`, and `strong`. Missing dimensions are `not_evaluated`, never zero; applicable weights are normalized and shown to the user.

Default display labels are `needs_work` below 40, `developing` from 40–59, `good` from 60–79, and `strong` from 80–100. The overall normalized score is the sum of each scored component multiplied by its effective weight. Effective weights are the configured scored weights divided by the sum of all configured scored weights.

`not_evaluated` is reserved for unavailable evidence or an unsupported/failed system capability. A user who explicitly skips a Q&A question receives a zero for that question's contribution; the system must not improve the overall score by removing the Q&A weight after a voluntary skip.

The system reports observable presentation behaviour. It must not infer anxiety, honesty, personality, emotion, or mental state.

## Non-functional requirements

| ID | Area | Requirement |
|---|---|---|
| NFR-01 | Performance | For the reference five-minute pitch, warm-run p95 from upload completion to questions-ready should be below 90 seconds. This is a measured objective, not an availability promise. |
| NFR-02 | Reliability | AI Jobs have stable IDs, idempotent processing, three attempts with exponential backoff, stage timeouts, monotonic updates, and visible failed-job retry. |
| NFR-03 | Security | Private-by-default resources, least-privilege service roles, signed object access, content-based validation, rate limits, encrypted transport, and no secrets in logs or contracts. |
| NFR-04 | Privacy | Explicit recording consent; no customer content used to train models; raw audio/video deleted after 30 days; project deletion begins immediate logical revocation and completes physical erasure within 24 hours. |
| NFR-05 | Accessibility | The critical flow meets WCAG 2.2 AA, supports keyboard use, visible focus, text transcripts, and reduced-motion preferences. |
| NFR-06 | Compatibility | Chrome, Edge, Firefox, and Safari current and previous major versions are supported for the critical path. |
| NFR-07 | Observability | Every request, message, stage, model call, and report is traceable by correlation ID without recording private media content in telemetry. |
| NFR-08 | Reproducibility | Each evaluation records input checksums and all pipeline, rubric, prompt, model, feature-setting, and contract versions. |
| NFR-09 | Cost | Cost is measured by stage and session. The proposal's $0.30–$0.40 target is a benchmark objective, not a fixed acceptance threshold until real provider data exists. |
| NFR-10 | Portability | Local development runs with Docker Compose; hosted models, mail, storage, auth, and queue access are replaceable adapters. |

## AI starting point

The initial baseline is a team choice rather than a permanent product dependency:

- Whisper Large V3 Turbo for transcription and word-level timestamps
- pyannote Community-1 for speaker diarization
- MediaPipe Pose and Face Landmarker for posture, movement, and gaze landmarks
- librosa for rate, pauses, fillers, and pitch features

The AI team chooses the LLM, embedding model, hosting providers, sampling settings, and exact versions. Those choices must satisfy the ports and data contracts and must be recorded in evaluation metadata.

## MVP release gate

The MVP is complete when a user can execute the full path described in FR-01 through FR-12 from a fresh Docker Compose setup, and the result passes automated tests, contract validation, security checks, the consented AI benchmark, PDF visual review, and a staging smoke test.
