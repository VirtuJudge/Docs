# Testing and quality plan

## Quality model

VirtuJudge has two kinds of correctness:

1. deterministic software behaviour: authorization, state transitions, contracts, idempotency, calculations, and rendering;
2. model-dependent behaviour: transcription, diarization, retrieval, grounding, question usefulness, and feedback agreement.

They need different tests. A flaky model call must not make ordinary unit tests flaky, and a perfectly valid JSON response must not be treated as evidence that the feedback is good.

## Test layers

| Layer | Runs | Covers |
|---|---|---|
| Unit | Every commit | Domain invariants, state transitions, score normalization, adapters' pure mapping, media calculations |
| Architecture | Every commit | Module boundaries and inward layer dependencies |
| Schema/contract | Every commit | OpenAPI, AI Job/update JSON Schema, examples, compatibility, generated clients |
| Integration | Every PR | PostgreSQL, Redis job queue, object storage, OIDC test issuer, fake mail adapter, PDF renderer |
| Component | Every PR | Backend and AI consumers with external dependencies replaced at ports |
| Browser E2E | Every PR and staging | Critical user journeys, reconnect, permission, upload, Q&A, report, erasure |
| Security | Every PR/nightly by cost | Auth matrix, upload attacks, replay, prompt injection, secret/dependency/container scans |
| AI evaluation | Scheduled and model-change gate | Quality, grounding, unsupported claims, latency, cost |
| Performance | Daily late sprint and release | Five-minute reference pitch, per-stage timing, concurrent session smoke |
| Visual | Report/UX changes | PDF page render, responsive states, accessibility |

## Contract test corpus

Every AI Job and update type has:

- minimum valid example;
- complete valid example;
- unknown additive field example;
- missing required field;
- invalid enum;
- incorrect resource ancestry;
- stale attempt;
- duplicate update;
- oversized payload or artifact mismatch;
- relevant semantic invariant, such as three primary questions or a missing member section.

Both repos run the same golden corpus. The docs snapshot is generated only after this corpus passes.

## Critical deterministic scenarios

1. An outsider cannot discover or mutate another team's resources.
2. Two invitation accept requests create one membership.
3. Two analysis-start requests with one idempotency key create one attempt and AI Job.
4. A crash between saving and enqueueing is recovered by the pending-job dispatcher.
5. A stale AI result cannot advance a retried or cancelled session.
6. Missing documents produce `not_evaluated`, not zero.
7. Optional vision failure produces a limitation and no vision score.
8. More than three primary or two follow-up questions is rejected.
9. Every mapped member appears exactly once in the report.
10. Erasure removes data from all stores and revokes access immediately.

## AI benchmark

Use consented or synthetic material only. Keep development fixtures small; keep the full benchmark access-controlled when it contains identifiable people.

| Capability | Measure | Initial release gate |
|---|---|---|
| STT | Word error rate and timestamp tolerance | Baseline recorded; no regression beyond agreed tolerance |
| Diarization | Speaker count and diarization error | Correct speaker count on core multi-speaker fixtures; tolerance documented |
| Audio | Rate/pause/pitch metric error | Deterministic fixtures within numeric tolerance |
| Vision | Landmark coverage and interval calculation | Valid output on core fixtures; missing faces/bodies handled explicitly |
| Retrieval | Relevant source in top-k and reference correctness | Every expected answerable fixture retrieves a valid source |
| Questions | Schema, grounding, duplication, relevance review | 100% schema/evidence validity; no unsupported questions in release corpus |
| Feedback | Rubric agreement and unsupported-claim review | Human-reviewed baseline; every material finding grounded or limited |
| Performance | Warm p50/p95 and stage timings | Report against 90-second five-minute-pitch objective |
| Cost | Stage/session provider and compute cost | Report against proposal's $0.30–$0.40 objective |

Thresholds that need empirical data are not invented in advance. Day 5 establishes the baseline; Day 9 records the release result and accepted deviations.

## AI change gate

A change to model, provider, prompt, chunking, embedding, sampling, aggregation, rubric, or feature calculation must record:

- old and new version identifiers;
- benchmark dataset/version;
- quality, latency, and cost deltas;
- newly observed limitations;
- provider data-handling and licence impact;
- reviewer decision and rollback version.

## Performance test profile

The reference profile is one five-minute MP4 presentation with two speakers and three representative documents. Publish CPU/GPU, memory, operating system/container, provider region, warm/cold status, sampling rates, concurrency, and network conditions next to results.

Measure:

- upload verification;
- media normalization;
- every parallel analysis stage;
- aggregation/grounding;
- question generation;
- answer turnaround;
- report and PDF generation;
- end-to-end warm p50 and p95;
- queue wait separately from execution.

## Accessibility and visual verification

- Automated WCAG checks on sign-in, team, upload, progress, Q&A, report, and deletion screens.
- Keyboard-only completion of Q&A.
- Screen-reader labels for recording and progress states.
- Visible focus and non-colour state cues.
- Responsive checks at representative mobile, tablet, and desktop sizes.
- Render every PDF page to an image and inspect clipping, overflow, contrast, headings, tables, evidence labels, and member-section page breaks.

## Release evidence

The release review collects test summaries, schema compatibility reports, dependency/container scan results, AI benchmark report, performance/cost report, accessibility report, rendered PDF sample, staging smoke result, known limitations, and rollback steps. A green CI badge without those artefacts is not sufficient.
