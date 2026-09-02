# Repository bootstrap plan

## Repository layout

VirtuJudge uses four peer repositories in the GitHub organization:

| Repository | Purpose | Primary owners |
|---|---|---|
| `Docs` | Product model, architecture, stories, plans, reviewed contract snapshots | Cross-team |
| `Frontend` | Next.js client | Frontend |
| `Backend` | FastAPI control plane | Backend |
| `AI-ML` | Pipeline workers, model adapters, derived data, evaluations | AI/ML |

Do not nest Git repositories or use submodules for daily development. A separate local parent folder or optional orchestration repository may hold a Compose file later, but it must not silently own or pin peer repos without a reviewed decision.

## Common files

Each code repo starts with:

- `README.md`
- `LICENSE` using Apache-2.0 text
- `CONTRIBUTING.md`
- `SECURITY.md`
- `CODE_OF_CONDUCT.md`
- `.gitignore`, `.gitattributes`, `.editorconfig`
- example environment file containing placeholders only
- dependency update and vulnerability scanning configuration
- issue and PR templates
- ownership/reviewer rules
- local verification command or task runner
- architecture and contract test entry points

## Branch and review policy

- Protect `main` from direct pushes.
- Require at least one owner review; require cross-repo consumer review for contracts.
- Require lint, types, unit, architecture, contract, integration, security, and build gates applicable to the repo.
- Dismiss stale approvals when contract, security, migration, or generated files change.
- Require linear history or squash merges and Conventional Commit subjects.
- Tag compatible releases with semantic versions once external consumers exist.

## Contract publication

- Backend owns public and internal OpenAPI plus AI job/update schemas.
- AI/ML owns AI-produced artifact schemas.
- Each producer publishes a versioned schema artefact in CI.
- Consumers pin a compatible version and run the golden corpus.
- Docs receives generated reviewed snapshots; prose in `Contracts/` explains the semantics and invariants.

## Local orchestration

The shared Compose profile starts:

- frontend;
- backend API;
- AI worker;
- PostgreSQL with backend and AI-owned tables;
- Redis for AI jobs and cache;
- S3-compatible object storage;
- backend mail configuration that reads Gmail credentials from environment-backed secrets; Gmail itself remains external to Compose;
- OpenTelemetry collector and a lightweight trace/metrics viewer;
- optional OIDC test issuer or documented Supabase development configuration.

Fake AI adapters are the default local profile. Real-provider profiles require explicit environment configuration and never become necessary for ordinary unit or end-to-end tests.

## Current workspace note

At the time of planning, `Docs` is the only working repository in the local VirtuJudge folder. The root `.git` directory is empty, and the proposal and presentation files are untracked in `Docs`. Review those existing files deliberately before staging anything; they are source material, not generated output.
