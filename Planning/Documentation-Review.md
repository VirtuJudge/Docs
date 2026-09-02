# Documentation review: 2 September 2026

## Review outcome

The documentation is internally coherent enough for team review. It should not be pushed or used to open implementation PRs until the team accepts the remaining evidence items below and the Mermaid diagrams have been rendered with the repository's eventual documentation toolchain.

No files were staged, committed, pushed, or submitted as a PR during this review.

## Scope reviewed

- Product scope, requirements, rubric, risks, domain language, and future work
- 35 detailed user stories and the complete story map
- System, backend, frontend, AI/ML, security, and technology architecture
- Frontend/backend REST and SSE contract
- Backend/AI job, callback, result, and retry contract
- Shared data contracts and job/notification catalogue
- 34 delivery tasks across six contributor lanes and ten calendar days
- Testing, repository bootstrap, open-source governance, and pre-push/PR review gates
- Seven accepted architecture decisions

## Findings resolved during review

1. The original proposal mixed a backend monolith with a decoupled AI pipeline. The design now uses one four-layer FastAPI backend and one separate AI worker.
2. The original storage list added MongoDB without a distinct need. The design now uses one PostgreSQL/pgvector instance plus object storage, with normal and `ai_*` table ownership.
3. The final Evaluation initially appeared before Q&A even though Q&A carries 20% of the score. The pre-Q&A result is now an Analysis Artifact; the final Evaluation and Report are created together after Q&A.
4. Invitation delivery and invitation validity were too easy to couple. Gmail acceptance/failure now updates delivery state without creating or deleting membership.
5. The first design required a general bidirectional event platform. It now uses one Redis AI job queue and one authenticated backend callback with five update statuses.
6. Team feedback and individual observations could have been read as one report section. The contract now requires team feedback and one complete feedback section for every mapped presenting member.
7. `not_evaluated` could have accidentally rewarded skipped Q&A by normalizing away its 20% weight. A user-initiated skip now contributes zero; system-unavailable evidence remains `not_evaluated`.
8. The first architecture was too large for ten days. It is now three application processes, one PostgreSQL instance, one object store, one Redis AI-job queue, Gmail SMTP, four backend layers, and one deep AI pipeline interface.

## Automated checks run

- All local Markdown links resolve.
- Every fenced JSON example parses.
- All authored Markdown code fences are balanced.
- Authored Markdown contains no trailing whitespace.
- Markdown documents contain no em dash characters.
- All 35 detailed user-story IDs appear in the story-map diagrams.
- All 34 implementation-task IDs are unique and every task dependency reference resolves.
- The default rubric weights total 100%, with Q&A at 20%.
- No authored document contains the common artificial/corporate phrases checked by the humanization pass; source proposal content was left unchanged apart from the requested punctuation cleanup.

## Review still required before merge

### Team confirmation

- Confirm the six-person allocation: two backend developers, two AI/ML developers, and two frontend developers. Each pair must agree who takes lane 1 and lane 2 before Day 1.
- Confirm the AI team's exact LLM, embedding model, hosting, sampling, and provider data-handling choices.
- Confirm the dedicated Gmail or Google Workspace sender account, from-address, and secret owner.
- Confirm that individual feedback is visible to the whole team for the MVP.

### Evidence and tool checks

- Render all 20 Mermaid blocks using the chosen docs renderer. The source was inspected and fenced correctly, but a Mermaid CLI was not installed in this workspace.
- Run Markdown lint using the config that will be committed with the repo.
- Verify market claims against primary sources before using them publicly.
- Establish the Day 5 AI quality baseline and Day 9 latency/cost results instead of treating proposal numbers as promises.
- Review model licences and provider terms before selecting default adapters.

### Existing untracked source material

Before staging, review the pre-existing untracked files under `Proposal/` and `Presentations/` separately. They were present before this documentation work and include the original Markdown proposal and two PDFs.

## Recommended review order

1. Product owner/team: Scope, Requirements, User Stories, Risks.
2. Backend and AI: System Architecture, both code architecture docs, Backend/AI Contract, Job/Notification Catalogue, Data Contracts.
3. Frontend and backend: Frontend Architecture and Frontend/Backend API.
4. Backend 2 with affected reviewers: Security/Privacy, Technology Stack, Repository Bootstrap, Testing.
5. All contributors: Ten-Day Plan, Future Work, ADRs, and Review Workflow.

Only after comments are resolved should the team stage the intended files, review the full staged diff, and decide whether to push or open PRs.
