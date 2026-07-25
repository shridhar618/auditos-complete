# AuditOS — Foundation Build (Phase 1)

Autonomous Enterprise Audit & Compliance Intelligence Platform.
This is Phase 1 of the feature-by-feature build: **architecture, database schema,
project scaffold, and Authentication + RBAC.** Everything here is real, working
code — not placeholders — but the business modules (dashboard data, investigations,
AI agents, etc.) are stubbed as "coming soon" pages until their own build phase.

## Architecture decisions (Step 1–3 of the workflow)

- **Backend**: FastAPI + SQLAlchemy 2.0, Clean/DDD-ish layering:
  - `app/domain/models` — ORM entities only, no business logic
  - `app/repositories` — Repository Pattern; all raw queries live here
  - `app/services` — business rules and orchestration (the only layer that
    raises domain exceptions)
  - `app/api/v1` — thin HTTP routers that translate request ↔ service call
  - `app/core` — config, DB engine, JWT/password utilities, domain exceptions
- **Multi-tenancy**: every business table carries `organization_id`. A user
  only ever sees data scoped to their own organization.
- **RBAC**: granular `resource:action` permissions (e.g. `investigations:approve`)
  bundled into roles (`admin`, `compliance_officer`, `auditor`, `viewer`).
  Enforced declaratively per-route via `Depends(require_permission("code"))`.
- **Auth**: short-lived JWT access tokens (15 min) + longer-lived, rotating,
  revocable refresh tokens (7 days) persisted in `refresh_tokens` so logout /
  admin-forced logout actually works (not just relying on JWT expiry).
- **Frontend**: React + TypeScript + Vite + Tailwind, shadcn-style component
  primitives (hand-written, no CLI needed), TanStack Query for server state,
  React Hook Form + Zod for forms, Framer Motion for polish, dark/light theme
  via CSS variables.

## Prerequisites

- Docker + Docker Compose (recommended path), **or**
- Python 3.12+, Node.js 20+, a local PostgreSQL 16 and Redis 7 if running without Docker

## Quick start (Docker — recommended)

```bash
# 1. Copy env template and edit as needed (JWT secret especially)
cp backend/.env.example backend/.env

# 2. Build and start everything
docker compose up --build

# 3. In a second terminal, run migrations and seed roles/permissions
docker compose exec backend alembic upgrade head
docker compose exec backend python -m app.seed
```

- Frontend: http://localhost:5173
- Backend docs (Swagger): http://localhost:8000/api/docs
- Health check: http://localhost:8000/api/health

Open the frontend, click **"Create your organization"**, and register — this
creates your tenant plus your first `admin` user with every permission.

## Quick start (without Docker)

**Backend**

```bash
cd backend
python -m venv .venv && source .venv/bin/activate   # Windows: .venv\Scripts\activate
pip install -r requirements.txt
cp .env.example .env   # edit DATABASE_URL to point at your local Postgres

alembic upgrade head
python -m app.seed
uvicorn app.main:app --reload
```

**Frontend**

```bash
cd frontend
npm install
npm run dev
```

## Project layout

```
auditos/
├── backend/
│   ├── app/
│   │   ├── core/            # config, db, security, exceptions
│   │   ├── domain/models/    # SQLAlchemy entities
│   │   ├── schemas/          # Pydantic request/response models
│   │   ├── repositories/     # data access layer
│   │   ├── services/         # business logic
│   │   ├── api/v1/           # routers
│   │   ├── main.py
│   │   └── seed.py           # seeds default roles + permission catalogue
│   ├── alembic/               # migrations
│   ├── requirements.txt
│   └── Dockerfile
├── frontend/
│   ├── src/
│   │   ├── components/{ui,layout}/
│   │   ├── context/           # Auth + Theme providers
│   │   ├── lib/                # api client, validation, utils
│   │   ├── pages/
│   │   ├── routes/             # ProtectedRoute
│   │   ├── types/
│   │   ├── App.tsx
│   │   └── main.tsx
│   ├── package.json
│   └── Dockerfile
└── docker-compose.yml
```

## What's next (per the feature-by-feature roadmap)

1. ~~**Dashboard module**~~ ✅ Done — real KPIs, compliance/risk scores, monthly trend, department/vendor risk, recent activity — all backed by live SQL aggregation (`app/repositories/dashboard_repository.py` + `app/services/dashboard_service.py`), rendered with Recharts on the frontend.
2. ~~**Transaction Management**~~ ✅ Done — filtered/paginated listing (`GET /transactions`), detail view, manual creation (`POST /transactions`), department/vendor lookups (`GET /lookups/departments|vendors`). New transactions start at `risk_score=0` / `status=normal` — real scoring is the Detection Agent's job, not faked here.
3. ~~**AI Agent pipeline**~~ ✅ Done — see below.
4. ~~**Document & Policy Center**~~ ✅ Done — see below.
5. ~~**Reporting & Analytics**~~ ✅ Done — see below.

All six phases from the original roadmap are now implemented. Natural next phases beyond the
original scope would be: real-time notifications, multi-tenant billing, a Settings/Users &
Roles management UI (currently "coming soon" placeholders — the backend APIs already exist,
e.g. `GET/POST /users`, `GET /roles`), and a background job queue (Celery/RQ) so document
processing and report generation don't block the request thread.

Each phase follows: understand → design architecture → design DB → design API →
design UI → implement backend → implement frontend → integrate AI → test → refactor,
same as this one.

### AI Agent pipeline (`app/ai_agents/`)

A LangGraph `StateGraph` implements the Supervisor's coordination:

```
Transaction → Detection Agent → Policy Agent → [anomalous or violates a rule?]
                                                        │yes
                                Investigation Agent → Evidence Agent → Recommendation Agent → (pending human approval)
```

- **Detection Agent** (`nodes/detection_agent.py`) computes a real 0–100 risk score from the
  transaction's z-score against its peer group's (same department/vendor) historical amounts —
  not a random number. An LLM (if `OPENAI_API_KEY` is set) only phrases the explanation of an
  already-computed score.
- **Policy Agent** (`nodes/policy_agent.py`) checks the transaction against active `PolicyRule`
  threshold rules (seeded examples: "Large Purchase Threshold", "Procurement Approval Limit").
- **Investigation Agent** opens the actual `Investigation` case when either agent flags something.
- **Evidence Agent** assembles a structured snapshot (transaction + detection stats + matched rules).
- **Recommendation Agent** suggests a next action — advisory only, degrades to a deterministic
  template with no API key, and **never** changes the case's status itself.
- Every step is persisted to `AgentRunLog` (input/output/reasoning/whether an LLM was used) and
  rendered as a visual timeline on the case detail page — this is the audit trail.
- The pipeline always ends at `pending_approval`. A human must call `POST
  /investigations/{id}/resolve` or `/dismiss` — the AI never self-approves.

Trigger it from a transaction's detail page ("Run AI Investigation") or via
`POST /api/v1/agents/run/{transaction_id}`. Without an `OPENAI_API_KEY`, everything still works —
scoring and policy checks are rule-based; only the phrasing of explanations/recommendations
falls back to templates instead of LLM-generated text.

### Seeing the dashboard with real numbers

The Dashboard module aggregates real rows from `transactions`, `investigations`,
and `audit_logs` — it does not fabricate anything in the UI. Until the
Transaction Management module is built to ingest real transactions, use the
included demo-data generator to populate your organization for testing:

```bash
# after registering an organization through the UI, grab its slug from the
# /auth/register response (organization_name -> slug) or query the DB, then:
docker compose exec backend python -m app.seed_demo_data --org-slug your-org-slug
```

This creates ~400 sample transactions across 6 departments and 8 vendors, plus
~60 investigations and a handful of activity-log entries, so every chart and
KPI on the dashboard has real data to render. Refresh the dashboard afterward.
It also seeds two sample `PolicyRule`s the Policy Agent will check new
transactions against.

### Trying the AI Agent pipeline

1. Open any transaction (or create one with a large amount) and click **"Run AI Investigation"**.
2. If it's anomalous or violates a policy rule, you'll be taken straight to the new case, showing
   the full agent timeline, evidence, and recommendation.
3. As an `admin` or `compliance_officer`, resolve or dismiss the case from there.
4. Add `OPENAI_API_KEY` to `backend/.env` to get LLM-phrased explanations/recommendations instead
   of the deterministic templates — no code changes needed either way.

### Document & Policy Center (`app/services/document_service.py`, `policy_document_service.py`)

- **Document Center**: upload invoices, POs, contracts, bank statements, emails (PDF/DOCX/TXT/CSV).
  Files are stored on disk under `UPLOAD_DIR` (persisted via the `auditos_uploads` Docker volume);
  text is extracted natively (`pypdf`/`python-docx`) with an OCR fallback (`pytesseract` +
  `pdf2image`) for scanned PDFs. If OCR's system dependencies (tesseract, poppler) aren't
  installed, the document is marked `failed` with a clear error instead of crashing.
- **Policy Center**: upload policy/regulation documents (RBI guidelines, SOX, GST, internal
  policies). Each is chunked (~1000 chars, 150 char overlap) and embedded via OpenAI
  (`text-embedding-3-small`) into `pgvector` — **note the Postgres image is `pgvector/pgvector:pg16`,
  not the plain `postgres` image**, since the extension has to ship with the database. Search uses
  cosine similarity when embeddings exist, and falls back to `ILIKE` keyword search with no
  `OPENAI_API_KEY` or no embedded matches — the UI always tells you which mode ran.
- The **Policy Agent** (from the AI pipeline) now also searches uploaded policy documents using
  the transaction's description as the query, surfacing relevant excerpts as citations in the
  case's evidence bundle alongside the hard threshold-rule violations.

### Reporting & Analytics (`app/services/report_*.py`, `app/repositories/analytics_repository.py`)

- **Reports**: generate Audit, Risk, Compliance, Department, or Vendor reports as real PDF
  (reportlab), Excel (openpyxl), or CSV files. `report_data_builder.py` deliberately **reuses**
  `DashboardRepository` and `AnalyticsRepository` rather than re-deriving KPIs, so the numbers in
  a report always match what's on the Dashboard. Every generated report is saved to disk and
  tracked in the `reports` table so it can be re-downloaded without regenerating.
- **Analytics**: a risk-matrix heatmap (department × risk band transaction counts), a weekly
  investigation timeline (resolved/dismissed/pending), and reviewer accountability (who resolved
  vs. dismissed how many cases) — all new aggregations in `AnalyticsRepository`, distinct from the
  Dashboard's high-level KPIs.

### An important correctness fix worth knowing about

While building this phase I caught a bug affecting every status/enum column in the schema:
SQLAlchemy's `Enum` type binds a Python enum's **name** (`"OPEN"`) to the database by default, not
its **value** (`"open"`) — but every migration creates native Postgres enum types using lowercase
values. Left unfixed, every write to `transactions.status`, `investigations.status`, `documents.category`,
and every other enum column would have failed at runtime with "invalid input value for enum".
Fixed via a shared `values_callable` helper (`app/domain/models/mixins.py::enum_values`) applied to
all 8 enum columns — this was a schema-level fix, so it corrects every phase retroactively without
touching the query code written in earlier phases.
