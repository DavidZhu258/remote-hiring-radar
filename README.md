# Remote Hiring Radar

Remote Hiring Radar is a small internal-first product for finding remote work and hiring signals without becoming a full job board.

It answers one question: which fresh remote AI/data/agent/vision roles are worth reviewing today?

## Why This Exists

The product is intentionally narrow. The earlier v1/v2 direction tried to cover too many information types in one system. That made the work harder to explain, harder to price, and harder to trust. This repo keeps one job: collect remote hiring signals, score them against a clear profile, and produce a short reviewable shortlist.

Expected saved cost:

- Time: reduce manual scanning of Foorilla, ATS feeds, and remote boards from hours to minutes.
- Money: avoid broad SaaS recruiting subscriptions while preserving source-level evidence.
- Reliability: deterministic scoring first, LLM enrichment second, human review before any outreach.

## Product Boundary

In scope:

- Foorilla and remote hiring source adapters.
- Normalization, deduplication, scoring, and shortlist reports.
- Explainable score reasons.
- ClickHouse `analytics.jobs` reads through a local FastAPI API.
- A Next.js dashboard with URL-synced filters, table view, mobile cards, and job details.

Out of scope:

- Auto-applying to jobs.
- Full CRM or ATS replacement.
- Heavy multi-agent orchestration.
- Auto-apply, resume generation, email tracking, and public distribution.

## Architecture

```text
ClickHouse analytics.jobs -> Quality rules -> FastAPI -> Next.js dashboard
```

The structure follows the simpler patterns seen in recent open-source job radar projects: adapter contracts, deterministic scoring, a CLI pipeline, and CI-tested core logic before adding UI.

## Quick Start

```bash
python -m pip install -e ".[dev]"
python -m pytest -q
remote-hiring-radar --sample
```

Run the API:

```bash
uvicorn remote_hiring_radar.api:app --reload --port 8000
```

Run the dashboard:

```bash
cd frontend
npm ci
npm run dev
```

Open `http://localhost:3000`.

## GitHub Pages Preview

The frontend can also be exported as a static GitHub Pages preview:

```bash
cd frontend
$env:GITHUB_PAGES="true"
$env:NEXT_PUBLIC_API_BASE_URL="http://127.0.0.1:8010"
$env:NEXT_PUBLIC_ENABLE_DEMO_FALLBACK="true"
npm run build
```

GitHub Actions deploys `frontend/out` to:

`https://davidzhu258.github.io/remote-hiring-radar/`

The Pages build uses demo fallback data when the local API is not reachable. To inspect
real ClickHouse data from the Pages UI on your own machine, run the FastAPI service on
`127.0.0.1:8010`.

## Configuration

Copy `.env.example` to `.env` for local runs. Keep real tokens in environment variables or a secret manager, never in the repo.

Required ClickHouse settings:

- `CLICKHOUSE_HOST`
- `CLICKHOUSE_PORT`
- `CLICKHOUSE_USER`
- `CLICKHOUSE_PASSWORD`
- `CLICKHOUSE_DATABASE=analytics`
- `RADAR_DEFAULT_DAYS=7`

Optional Foorilla link settings:

- `FOORILLA_AUTH_URL`: current Foorilla login/auth URL. Foorilla job links append `next=<job_url>`.
- `FOORILLA_LINK_TEMPLATE`: exact link template with `{url}` when Foorilla changes the redirect parameter.

## CI

GitHub Actions runs Python tests, ruff checks, compile checks, API smoke tests, secret scan, and frontend test/lint/typecheck/build on every push and pull request.
