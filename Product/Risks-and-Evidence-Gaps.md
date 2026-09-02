# Risks and evidence gaps

The proposal gives the project a clear direction, but several claims still need evidence. None of these gaps blocks documentation or scaffolding. They affect product claims, model acceptance, performance promises, and production decisions.

## Product and market evidence

| Risk or gap | Why it matters | Ten-day action | Later action |
|---|---|---|---|
| Market-size, glossophobia, coaching-cost, adoption, improvement, startup-failure, and deck-review-time claims have no cited sources in the proposal | Public claims may be inaccurate or impossible to defend | Remove them from release messaging or label them unverified | Research primary sources and record citation/date/method |
| “Perfectly analyze reports” is not measurable | It cannot be an acceptance criterion | Replace with retrieval, grounding, schema, and reviewer-agreement measures | Expand benchmark and publish limitations |
| Target audience includes competition teams, startups, sales, and product teams | One rubric and workflow may not fit all four | Build and test the startup/competition pitch path | Interview each segment before adding rubrics |
| Users' agreement with weaknesses is subjective | Agreement can reward agreeable wording rather than correctness | Capture structured feedback on usefulness and evidence validity | Define a study with blind review and segment breakdown |

## Delivery risks

| Risk | Likelihood/impact | Mitigation and trigger |
|---|---|---|
| Ten calendar days and four parallel tracks leave little integration margin | High/high | Fake vertical slice by Day 2; questions-ready gate on Day 5; feature freeze Day 8 |
| Gmail credentials, quota, or delivery failure blocks invitation email | Medium/medium | Dedicated sender account, secret rotation, allow-listed smoke test, resend state; invitation validity never depends on delivery state |
| Browser media formats differ | High/medium | Accept WebM/MP4, normalize server-side, test supported browsers with real recordings |
| PDF rendering can consume late sprint time | Medium/medium | Use one server-side template and visual test early; cut polish before content |
| Separate repos can drift | High/high | Producer-owned schemas, generated clients/snapshots, golden messages, cross-owner review |

## AI and data risks

| Risk | Likelihood/impact | Mitigation and trigger |
|---|---|---|
| 90-second questions-ready objective may fail on a five-minute pitch | High/high | Measure stage time on Day 5; tune sampling/parallelism; report the actual environment and p95 |
| $0.30–$0.40 session cost may not match provider choices | Medium/high | Record tokens/compute/cost per stage; treat target as an objective until benchmarked |
| Diarization can split or merge speakers incorrectly | High/high | Anonymous labels, preview intervals, explicit user mapping, no silent identity assignment |
| Gaze/pose metrics may be interpreted as confidence or emotion | High/high | Restrict to observable measurements; contract and review ban unsupported human-state inference |
| LLM can invent evidence or obey document prompt injection | High/high | Typed evidence registry, minimal context, document-as-data boundary, schema and reference validation |
| Model/provider changes alter output without code-contract changes | High/high | Record full provenance; benchmark changes to providers, prompts, embeddings, sampling, and rubrics |
| Real user benchmark media is sensitive | Medium/high | Use synthetic fixtures by default; consented benchmark access control and documented retention |
| pyannote/model licences or provider terms may constrain deployment | Medium/high | AI team records model card, licence, access terms, training/data handling, and redistributability before defaulting an adapter |

## Security and operations risks

| Risk | Mitigation |
|---|---|
| Cross-team object access | Authorize resource ancestry before issuing short-lived signed URLs; isolated key prefixes and service roles |
| Malicious documents/media | Type/signature/size/duration validation and isolated parsing; add malware scanning before production |
| Redis used for cache and AI jobs | Separate ACLs/key spaces and monitor contention; split physical instances when measurements require it |
| Erasure spans many stores | Coordinator with per-store steps, retries, 24-hour deadline, and operator alert |
| Provider or Redis outage | Stage-specific timeout/retry, stable job IDs, pending-job redispatch, limitation policy, safe user errors |
| Private content in telemetry | Synthetic canary strings and automated log checks; IDs and metrics only |

## Decision triggers

- Missing the Day 5 gate triggers scope review using the documented cut order.
- Missing the 90-second objective triggers a written benchmark analysis, not hidden sampling or quality reduction.
- Any unsupported claim in the release benchmark blocks the affected question/report component.
- Any cross-team access, consent bypass, secret leak, or failed erasure blocks release.
- A provider without acceptable data handling or licensing cannot become the default adapter.
