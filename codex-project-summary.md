# Codex Project Summary

## Current Focus

Implement the first vertical product slice: Fresh Remote AI/Data/Agent/Vision Jobs Worth Applying To Today.

## Decisions

- Use existing ClickHouse `analytics.jobs`; do not add ATS collectors, auto-apply, LLM classification, embedding, or distribution in this phase.
- Keep `job_quality_view` logical in Python/API code instead of creating a persistent ClickHouse view.
- Treat broad vision as a first-class tag: computer vision, image recognition, OCR, video, multimodal, robotics perception, OpenCV, YOLO, SAM, and related wording.
- Build a local FastAPI + Next.js dashboard with URL-synced filters, a dense table, mobile cards, and a detail drawer.

## Implemented

- Added FastAPI endpoints: `/api/health`, `/api/jobs`, `/api/facets`.
- Added deterministic quality fields: freshness bucket, source trust, remote quality, role tags, salary status, duplicate key, repost count, quality reasons, and exclude reasons.
- Added ClickHouse and in-memory repositories.
- Added Next.js dashboard under `frontend/`.
- Added CI jobs for Python tests/ruff/compile/secret scan/API smoke and frontend test/lint/typecheck/build.
- Added GitHub Pages static preview support with demo fallback data and optional local API access.
- Configured repository Pages to use the legacy `gh-pages` branch source at `/`.
- Updated `.github/workflows/pages.yml` to build the frontend and force-publish only `frontend/out` to `gh-pages`.
- Added Foorilla link derivation: API now emits `source_link_url` and `apply_link_url`; Foorilla links can use `FOORILLA_AUTH_URL` or `FOORILLA_LINK_TEMPLATE`, and missing `apply_url` falls back to the Foorilla source job page.

## Verification

- Backend unit/API tests pass locally.
- Frontend test, lint, typecheck, and production build pass locally.
- Real local ClickHouse smoke returned `/api/health` with latest `posted_date=2026-05-08` and stale warning.
- 2026-05-12: GitHub Actions for commit `cb30df5` completed successfully: CI run `25728368688`, Pages run `25728368705`.
- 2026-05-12: GitHub Pages latest build is `built` with no error, source `gh-pages` `/`.
- 2026-05-12: Live preview returns HTTP 200 at `https://davidzhu258.github.io/remote-hiring-radar/` with expected Next static asset paths.
- 2026-05-12: PR opened: `https://github.com/DavidZhu258/remote-hiring-radar/pull/1`.
- 2026-05-12: Local API started on `127.0.0.1:8010` against ClickHouse `analytics.jobs`; `/api/health` reports connected, latest `posted_date=2026-05-08`, stale warning true.
- 2026-05-12: `/api/jobs?days=30&source=foorilla.com&limit=1` returns real ClickHouse data and Foorilla source/apply links both redirect through the configured auth entry.
- 2026-05-12: After Foorilla link changes, local verification passed: `python -m pytest -q`, `python -m ruff check .`, `python -m ruff format --check .`, `python -m compileall src tests`, `python scripts\secret_scan.py`, `npm test`, `npm run lint`, `npm run typecheck`, `npm run build`, and GitHub Pages static export build.

## Notes

- Local data is stale relative to 2026-05-11, so the UI shows a non-blocking stale feed notice.
- `gh` CLI is not installed locally; GitHub PR creation should use available GitHub tooling or a compare URL after push.
- Pages preview uses `NEXT_PUBLIC_ENABLE_DEMO_FALLBACK=true`; real data still requires the local FastAPI service.
- For GitHub operations in this session, the classic PAT file was used directly to avoid Git Credential Manager prompts. Do not print token contents.
- If the Pages UI shows demo data, make sure the local FastAPI process is running on `127.0.0.1:8010`; the static page cannot host the API or ClickHouse itself.
