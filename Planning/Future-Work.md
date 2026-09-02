# Future work

Future work is grouped by prerequisite instead of promised dates. Nothing here is required for the ten-day MVP unless it is promoted through review and the plan is rebalanced.

## Near-term product work

| Capability | Prerequisite |
|---|---|
| Completion email notifications | Stable report-ready state transition and user notification preferences |
| Cross-session progress dashboards | Stable rubric versions, comparable session metadata, and privacy review |
| Custom rubric selection/authoring | Rubric validation, migration, preview, and permissions model |
| Per-member feedback visibility | Product policy for private member sections and owner access |
| Public report sharing | Revocation, expiry, redaction, consent, and abuse controls |
| Advanced document formats | Sandboxed parsers, provenance contract, and security fixtures |
| Manual transcript/speaker correction | Provenance and re-evaluation policy for user-edited evidence |
| Malware scanning | Scanner service, quarantine storage, signature updates, timeout/failure policy |
| Moderation and abuse handling | Policy, reporting flow, retention exceptions, and operator access controls |

## Product expansion

| Capability | Prerequisite |
|---|---|
| Live synchronous interruption | Streaming media protocol, sub-second budgets, turn-taking state machine, reconnect/cancellation semantics |
| Streaming transcription | Browser streaming, partial/final transcript contract, backpressure, cost and privacy review |
| Judge personas or avatars | Clear educational purpose, persona safety rules, media/licensing review |
| Multilingual analysis | Language detection, multilingual benchmarks, translated rubric semantics, locale-aware reports |
| Billing and subscriptions | Entitlements, metering, invoices, provider cost attribution, legal/tax decisions |
| Competition-specific judge panels | Rubric governance, panel configuration, bias review, explainability |
| Mobile applications | Stable public API, mobile recording/upload and offline-resume design |
| Real-time team collaboration | Presence, concurrent edits, member-level permissions, conflict rules |

## Production readiness

| Capability | Prerequisite |
|---|---|
| Autoscaling worker pools | Queue-depth/service-time metrics, idempotent stages, benchmark-based resource profiles |
| Dedicated CPU/GPU pools | Scheduler labels, stage routing, artifact/checkpoint compatibility |
| Physical service/data separation | Stable ownership, migrations, network/service identity controls |
| Multi-region deployment | Data residency decision, replication model, object locality, failover tests |
| Disaster recovery | RPO/RTO decisions, backups, restore rehearsal, provider failure scenarios |
| Formal SLOs | Sustained production measurements, alert policy, error-budget ownership |
| High availability | Identified availability targets and removal of single points of failure |
| Cost optimization | Per-stage cost data, caching/reuse policy, model quality/cost comparisons |
| Provider failover | Compatible adapters, benchmark parity, data-policy review, routing rules |
| Durable event platform | Proven AI Job/consumer need, portable contracts, migration and dual-run plan |
| Compliance programme | Market/legal requirements, data inventory, retention/legal-hold decisions |

## Architecture evolution triggers

- Split a backend module only when it needs independent scaling, ownership, security, or availability and the added operational cost is justified.
- Split Redis jobs and cache physically when workload contention or security policy requires it.
- Move AI schemas to a separate PostgreSQL server when resource contention or isolation needs appear.
- Add a new database only when measured query/storage needs don't fit PostgreSQL, pgvector, or object storage.
- Add a read-optimized host only after profiling shows the backend API is the bottleneck.

## Future-work review

Every promoted item needs an owner, problem statement, evidence, user stories, threat/privacy review, contract impact, test plan, migration/rollback path, and an updated delivery plan before implementation starts.
