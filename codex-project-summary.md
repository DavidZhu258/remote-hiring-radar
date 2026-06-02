# Codex Project Summary

## Current Focus

Implement the first vertical product slice: Fresh Remote AI/Data/Agent/Vision Jobs Worth Applying To Today.

## Decisions

- Use existing ClickHouse `analytics.jobs`; do not add ATS collectors, auto-apply, LLM classification, embedding, or distribution in this phase.
- Keep `job_quality_view` logical in Python/API code instead of creating a persistent ClickHouse view.
- Treat broad vision as a first-class tag: computer vision, image recognition, OCR, video, multimodal, robotics perception, OpenCV, YOLO, SAM, and related wording.
- Build a local FastAPI + Next.js dashboard with URL-synced filters, a dense table, mobile cards, and a detail drawer.
- 2026-06-01: User's personal job target is not pure software-only AI roles. Prioritize AI/CV/Data/Robotics/Edge roles that involve global travel, overseas/non-China work exposure, customer-facing communication, implementation, professional services, consulting, field/application engineering, deployment, pre-sales/post-sales, and training/enablement. Downrank pure backend/frontend/full-stack/QA/admin/recruiting/marketing and roles with weak evidence.

## Implemented

- 2026-06-02: Updated Remote Hiring Radar default dashboard page size from 50/100-capped behavior to 500. Frontend defaults and URL canonicalization now produce `limit=500`; demo fallback defaults to 500; FastAPI `/api/jobs` accepts `limit=500`; service layer defaults and clamps to 500.
- 2026-06-02: Investigated the GitHub Pages URL opening with `?days=7&tags=infra&limit=1&offset=0&sort=fresh`. Before the 500-page-size fix, the app defaulted to `limit=50` while accepting `limit=1` from URL state.
- 2026-06-02: Checked GitHub upload state for the dashboard/API work. Local `feature/fresh-remote-jobs-dashboard` and `origin/feature/fresh-remote-jobs-dashboard` are both at `87dace0`; current local edits are still modified/untracked and have not been uploaded.
- Added FastAPI endpoints: `/api/health`, `/api/jobs`, `/api/facets`.
- 2026-06-01: Added target-fit scoring for the user's global travel/customer-facing AI/CV/data transition goal. The API now emits `target_bucket`, `target_score`, `priority_terms`, and `downrank_terms`; `sort=target_fit` ranks the best matches first. Priority terms include Solutions, Implementation, Field, Application, Consultant, Professional Services, Customer, Deployment, Integration, Onsite, Travel, Pre-sales, Post-sales, Industrial, Robotics, Vision, Automation, and Edge AI. Downrank terms include Backend, Frontend, Full Stack, Java, .NET, QA, Tester, IT Support, Security, Marketing, Recruiter, Associate, Analyst, and Admin.
- 2026-06-01: Added `best_for_me` personal-fit scoring for the user's transition target: roles combining AI/CV/Data/Robotics/Edge/domain-platform skills with travel, overseas/customer-site exposure, implementation, consulting, solutions, professional services, pre/post-sales, training, enablement, deployment, and integration. The API now emits `personal_fit_bucket`, `personal_fit_score`, `mobility_tags`, `people_facing_tags`, `domain_tags`, `risk_tags`, and `fit_reasons`.
- 2026-06-01: Tightened vision matching so `vision insurance` no longer counts as computer vision. Vision now requires signals such as computer vision, image recognition, OCR, OpenCV, YOLO, SAM, vision engineer/systems/model/AI, visual AI, or related machine-vision terms.
- 2026-06-01: Optimized personal-fit evaluation by replacing repeated regex boundary searches with normalized boundary substring matching. This reduced local 500-row service ranking from about 5-6s to about 1-2s after warmup.
- 2026-06-01: Updated the `3010` dashboard to show Priority signals and Non-priority signals above the data overview, add a `Fit` table column, expose priority/downrank chips per row, support `Best fit` URL-synced sorting, and show full target-fit detail in the drawer.
- 2026-06-01: Added FastAPI `/api/overview` for current job data display: observed row count, source/apply/salary/remote/direct-source coverage, duplicate/repost counts, freshness/remote/tag distributions, and top sources/companies.
- 2026-06-01: Optimized search responsiveness: keyword input is debounced before URL/API submission, health is no longer refetched on every filter change, jobs load independently from summary metadata, metadata is delayed/sequential and skipped while a keyword search is active, and summary/facet endpoints use a 500-row sampled quality window.
- 2026-06-01: Fixed immediate frontend fetch failure by making the browser API client try local API candidates in order: configured `NEXT_PUBLIC_API_BASE_URL`, `127.0.0.1:8011`, `127.0.0.1:8010`, then `localhost:8000`. Restarted the temporary frontend on `3010` with `NEXT_PUBLIC_API_BASE_URL=http://127.0.0.1:8011`.
- 2026-06-01: Widened the desktop jobs table Company column from 96px to 180px and increased the table minimum width to 1500px so company names have more room without compressing other columns.
- Added deterministic quality fields: freshness bucket, source trust, remote quality, role tags, salary status, duplicate key, repost count, quality reasons, and exclude reasons.
- Added ClickHouse and in-memory repositories.
- 2026-06-01: Optimized ClickHouse job queries with `PREWHERE` for date/source pruning, exact `source_name` matching, trimmed keyword parameters, primary-key-aligned ordering (`posted_date`, `job_id`), and optional unsorted fetches for facet sampling.
- Added Next.js dashboard under `frontend/`.
- 2026-06-01: Updated the Next.js dashboard with a current-data overview panel, distribution bars, top source/company panels, data-quality chips, pagination controls, and fixed the URL default `limit` bug that caused bare URLs to load only one row.
- Added CI jobs for Python tests/ruff/compile/secret scan/API smoke and frontend test/lint/typecheck/build.
- Added GitHub Pages static preview support with demo fallback data and optional local API access.
- Configured repository Pages to use the legacy `gh-pages` branch source at `/`.
- Updated `.github/workflows/pages.yml` to build the frontend and force-publish only `frontend/out` to `gh-pages`.
- Added Foorilla link derivation: API now emits `source_link_url` and `apply_link_url`; Foorilla links can use `FOORILLA_AUTH_URL` or `FOORILLA_LINK_TEMPLATE`, and missing `apply_url` falls back to the Foorilla source job page.

## Verification

- 2026-06-02: Created local commit `fa6ad47` (`Expand remote hiring dashboard data view`) containing the dashboard/API updates and 500 default limit fix. Push to `origin/feature/fresh-remote-jobs-dashboard` is blocked: GitHub returned 403 for the current Git Credential Manager identity, so GitHub Pages has not redeployed from this commit yet.
- 2026-06-02: Default limit 500 verification passed: frontend focused tests `npm test -- --run src/lib/filters.test.ts src/lib/demo.test.ts`, Python focused tests for API/service page size, full `python -m pytest -q` -> 31 passed, `python -m ruff check .`, `python -m ruff format --check .`, `python -m compileall src tests -q`, `python scripts\secret_scan.py`, frontend `npm test`, `npm run lint`, `npm run typecheck`, regular `npm run build`, and GitHub Pages env `npm run build` all passed. Exported Pages bundle contains `limit:500`. Browser-level Playwright check could not run because `playwright` is not installed in local `node_modules`.
- 2026-06-02: GitHub/upload verification: ran `git fetch origin --prune`, `git status --short --branch`, and `git rev-parse` checks. `HEAD` equals `origin/feature/fresh-remote-jobs-dashboard` at `87dace0`, `origin/gh-pages` is `938e196`, and modified/untracked files remain locally. `gh` CLI is not installed, so GitHub state was verified through git remotes.
- 2026-06-01: Formal Foorilla official-filtered crawl inserted 644 rows from 690 in-range candidates into ClickHouse. API smoke on `127.0.0.1:8011` returned top `sort=target_fit` job `Technical Implementation Engineer I`, `target_bucket=priority`, `target_score=11`, auth-wrapped Source/Apply links, overview `target_fit.priority=5`, `target_fit.downranked=118`, `total_observed=500`, latest `2026-05-31`.
- 2026-06-01: Best-for-me verification passed after API/frontend restart. `127.0.0.1:8011/api/jobs?days=30&limit=8` returned 500 observed rows, no downranked jobs in the first 8, auth-wrapped Foorilla Source/Apply links, and top rows such as `Sr. Enterprise AI Platform Engineer`, `Senior Data Architect`, `Delivery Senior Consultant, Configuration and Integration Solutions`, `AI Solution Specialist`, and `Staff MLOps Engineer`. `/api/overview?days=30` returned `personal_fit`: `strong_match=51`, `good_match=221`, `maybe=41`, `downrank=187`.
- 2026-06-01: Final validation passed: `python -m pytest -q` -> 29 passed; `python -m ruff check .` -> all checks passed; `python -m compileall src tests` -> ok; frontend `npm test -- --run` -> 4 files / 9 tests passed; `npm run lint`, `npm run typecheck`, and `npm run build` all passed. Browser DOM verification at `http://127.0.0.1:3010/?days=30` showed `Best for me signals`, `Best For Me`, 272 strong/good rows, first rows with Strong Match badges, no downrank in first 8 rows, and Source/Apply auth links.
- 2026-06-01: Target-fit implementation verification passed: `python -m pytest -q` -> 21 passed; `python -m ruff check .` -> all checks passed; `python -m compileall src tests` -> ok; frontend `npm test -- --run` -> 4 files / 9 tests passed; `npm run lint` -> ok; `npm run build` -> successful; `npm run typecheck` -> ok when rerun after build. Browser verification at `http://127.0.0.1:3010/?days=30&sort=target_fit` showed Priority signals, Non-priority signals, counts `5 priority rows` / `118 downranked rows`, first row `Technical Implementation Engineer I`, target-fit chips, and Foorilla auth links. Screenshot saved at `.codex/logs/dashboard-target-signals-final.png`.
- 2026-06-01: TDD checks for `/api/overview`, demo overview fallback, and default URL `limit` behavior were added. Verified the red failures before implementation.
- 2026-06-01: Fresh local verification passed: `python -m pytest -q` -> 14 passed; `python -m ruff check .` -> all checks passed; `python -m ruff format --check .` -> 16 files formatted; `python -m compileall src tests -q` -> ok; `python scripts\secret_scan.py` -> clean; frontend `npm test` -> 2 files / 5 tests passed; `npm run lint` -> ok; `npm run typecheck` -> ok after `npm run build` generated `.next/types`; `npm run build` -> compiled successfully.
- 2026-06-01: Real ClickHouse smoke on temporary API `127.0.0.1:8011`: `/api/health` ok with latest `posted_date=2026-05-31`; `/api/overview?days=30&source=foorilla.com` returned `total_observed=10000`, sample capped, salary ratio `0.0097`; `/api/jobs?days=30&source=foorilla.com&limit=50` returned 50 items. Temporary frontend `127.0.0.1:3010` returned HTTP 200.
- 2026-06-01: Headless Chrome screenshot of `http://127.0.0.1:3010/?days=30&source=foorilla.com&limit=50` showed the overview panel and 50-row table window loading real data; table column widths were adjusted after visual review.
- 2026-06-01: Search/query optimization verification passed: `python -m pytest -q` -> 18 passed; `python -m ruff check .` -> all checks passed; `python -m ruff format --check .` -> 17 files formatted; `python -m compileall src tests -q` -> ok; `python scripts\secret_scan.py` -> clean; frontend `npm test` -> 3 files / 7 tests passed; `npm run lint`, `npm run build`, and `npm run typecheck` all passed. Restarted temporary API `127.0.0.1:8011`; smoke checks returned frontend HTTP 200 and `/api/jobs?days=30&source=foorilla.com&q=robotics&limit=5` HTTP 200 in about 2.0s when not competing with summary work.
- 2026-06-01: Fetch-failure fix verification passed: frontend `npm test` -> 4 files / 9 tests passed; `npm run lint`, `npm run typecheck`, and `npm run build` passed. Smoke checks after restarting `3010`: frontend HTTP 200 and `127.0.0.1:8011/api/jobs?...` HTTP 200.
- 2026-06-01: Company column width adjustment verification passed: `npm run lint`, clean `npm run build` after stopping the dev server to avoid `.next` contention, `npm run typecheck`, and frontend HTTP 200 on `127.0.0.1:3010`.
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
- 2026-05-12: Local API autostart configured for the current Windows user via Startup VBS `RemoteHiringRadarAPI.vbs`; it launches a local supervisor script under `%LOCALAPPDATA%\RemoteHiringRadar` and keeps FastAPI on `127.0.0.1:8010`.
- 2026-05-12: Autostart path verified manually: API health returns connected, port `8010` is listening, and `/api/jobs?days=30&source=foorilla.com&limit=1` returns Foorilla data with redirected source/apply links.

## Notes

- Local data is current as of 2026-05-31 in the refreshed Foorilla ClickHouse data seen on 2026-06-01; old 2026-05-11 stale note is superseded for the temporary API run.
- 2026-06-01: Current local services for review: API `127.0.0.1:8010` and `127.0.0.1:8011`; frontend `127.0.0.1:3010` restarted after clearing generated `.next` to avoid a stale Next devtools/RSC manifest error.
- `gh` CLI is not installed locally; GitHub PR creation should use available GitHub tooling or a compare URL after push.
- Pages preview uses `NEXT_PUBLIC_ENABLE_DEMO_FALLBACK=true`; real data still requires the local FastAPI service.
- For GitHub operations in this session, the classic PAT file was used directly to avoid Git Credential Manager prompts. Do not print token contents.
- If the Pages UI shows demo data, make sure the local FastAPI process is running on `127.0.0.1:8010`; the static page cannot host the API or ClickHouse itself.
- Local autostart secrets live outside the repo in the local env file; do not commit or print them.
- 2026-06-01: A temporary current-code API is running on `127.0.0.1:8011` and a temporary frontend is running on `127.0.0.1:3010`, with logs redirected to `%TEMP%`. The older autostart API on `127.0.0.1:8010` was intentionally left untouched.
