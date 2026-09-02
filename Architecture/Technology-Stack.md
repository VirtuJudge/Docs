# Technology stack

Choose supported stable versions when scaffolding begins and pin them in each repository. This document chooses responsibilities and libraries, not version numbers that will age before implementation starts.

## Frontend

| Concern | Choice | Reason |
|---|---|---|
| Application | Next.js with TypeScript and React | Matches the proposal and supports a production web client |
| Server state | TanStack Query or equivalent query cache | Backend resources remain canonical and can be refetched after SSE events |
| Local feature state | React state; a small Zustand store only where recording/upload workflows need it | Avoid a single global store for server-owned data |
| API types | Generated from backend OpenAPI | Prevent hand-copied request/response drift |
| Upload | Browser `fetch`/XHR to signed object URLs, checksum in a Web Worker | Keeps large media away from the backend process and UI thread |
| Recording | MediaRecorder behind a capability wrapper | Browser differences remain isolated and testable |
| Testing | Vitest, Testing Library, Playwright, automated accessibility checks | Covers components, contracts, browsers, and the critical journey |

## Backend

| Concern | Choice | Reason |
|---|---|---|
| Runtime/API | Python 3.11+ and FastAPI | Matches the accepted proposal and AI team's language |
| Boundary models | Pydantic v2 | OpenAPI generation and explicit validation |
| Persistence | SQLAlchemy 2 async plus Alembic and PostgreSQL driver | Transactions, migrations, and testable mappings without leaking ORM into Domain/Application |
| AI jobs | Celery with Redis broker behind `AIJobs` | One queue and retry mechanism without a general event platform |
| Object storage | S3-compatible adapter; MinIO locally | Direct signed uploads and portable local development |
| Auth | Standards-based OIDC JWT validation; Supabase Auth first | Keeps backend authorization independent of the identity UI/vendor |
| Mail | Gmail SMTP through a small `MailSender` adapter | Meets the selected delivery choice while keeping credentials and provider details outside application code |
| PDF | HTML/CSS template rendered server-side by a pinned renderer | Same canonical report can be checked visually and exported predictably |
| Observability | OpenTelemetry, structured JSON logs, Prometheus-compatible metrics | End-to-end correlation without private payload logging |
| Quality | Ruff, a strict type checker, pytest, architecture/import tests | Fast local feedback and executable dependency rules |

## AI/ML

| Concern | Choice | Reason |
|---|---|---|
| Runtime | Python 3.11+ Celery worker | Supports the selected ecosystem without another HTTP process |
| STT | Whisper Large V3 Turbo through `SpeechToTextPort` | Accepted initial direction; adapter/provider chosen by AI team |
| Diarization | pyannote Community-1 through `DiarizationPort` | Accepted initial direction with anonymous speaker labels |
| Vision | MediaPipe Pose and Face Landmarker through `VisionPort` | Timed observable posture, movement, and gaze landmarks |
| Audio | librosa through `AudioFeaturePort` | Deterministic rate, pause, filler, and pitch measurements |
| LLM | AI-team-selected adapter through `JudgeModelPort` | Model and hosting remain replaceable |
| Embeddings | AI-team-selected adapter through `EmbeddingPort` | Dimensions/model/chunking remain versioned |
| Derived persistence | `ai_*` PostgreSQL/pgvector tables under an AI role | Resumable stages and retrieval in the same MVP database instance |
| Media processing | FFmpeg adapter in isolated ingestion stage | Canonical audio/video normalization and metadata |
| Documents | Sandboxed PDF/PPTX extractors with page/slide provenance | Grounds retrieval and citations in exact source versions |
| Quality | pytest, schema/golden-message tests, consented benchmark harness | Separates software correctness from model quality |

## Platform

| Concern | Local | Staging |
|---|---|---|
| Containers | Docker Compose | Container platform chosen by project team |
| Database | PostgreSQL with pgvector, separate backend/AI roles | Managed PostgreSQL/pgvector with the same ownership split |
| Queue/cache | Redis | Managed Redis using separate key prefixes for jobs and cache |
| Objects | MinIO or compatible local S3 | Private S3-compatible bucket/container |
| Mail | Dedicated Gmail test sender plus fake adapter in automated tests | Dedicated Gmail or Google Workspace sender |
| Identity | OIDC test issuer or Supabase dev project | Supabase Auth first adapter |
| Telemetry | OpenTelemetry collector and local viewer | Managed or self-hosted trace/metrics/log backend |

## Technology guardrails

- Model/provider SDKs stay in AI infrastructure adapters.
- FastAPI, Pydantic, and SQLAlchemy types do not enter backend domain objects.
- Celery and Redis types stay inside the `AIJobs` implementation and worker entry point.
- Gmail credentials come from the secret store or local environment and never enter images, source control, fixtures, or logs.
- Frontend features consume the generated client rather than raw endpoint strings.
- A new framework, service, store, or provider needs a named owner, failure policy, test adapter, data-handling review, and removal path.
