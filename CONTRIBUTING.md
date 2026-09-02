# Contributing to VirtuJudge documentation

VirtuJudge is contract-first. Start with the user need and update the relevant story, architecture, contract, or plan before proposing implementation behaviour.

## Before making a change

1. Read the [domain language](./CONTEXT.md) and use its terms consistently.
2. Find the affected user story and contract.
3. Discuss hard-to-reverse choices before writing a new ADR.
4. Keep real presentation, document, transcript, and identity data out of examples and fixtures.

## Documentation style

- Write concrete requirements and explain trade-offs plainly.
- Use relative links for files in this repository.
- Put executable schema ownership in the producing code repo; this repo holds reviewed explanations and generated snapshots.
- Don't describe model-generated observations as emotion, confidence, honesty, personality, anxiety, or mental state.

## Review

Follow the [Review Workflow](./Planning/Review-Workflow.md). Contract changes require producer and consumer review. AI component changes require benchmark evidence. UI and PDF changes require accessibility and rendered visual evidence.

Do not push or open a PR until the local diff and relevant checks have been reviewed.

## Commit and PR expectations

- Use a focused Conventional Commit subject.
- Link the affected story or decision.
- Describe contract and migration impact.
- Include commands and evidence used to verify the change.
- Call out limitations and deferred work directly.
