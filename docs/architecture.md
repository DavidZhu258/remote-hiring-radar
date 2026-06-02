# Architecture

Remote Hiring Radar is a modular monolith with a FastAPI + Next.js dashboard for the
first vertical product: fresh remote AI/data/agent/vision jobs worth reviewing today.

## Modules

- `models.py`: typed domain objects for jobs, scored jobs, and reports.
- `pipeline.py`: deterministic normalize, score, and report logic.
- `quality.py`: deterministic job-quality view fields such as freshness, remote quality,
  role tags, salary status, repost key, and explainable reasons.
- `repository.py`: ClickHouse-backed and in-memory job repositories.
- `service.py`: API-level filtering, pagination, facets, and health aggregation.
- `api.py`: FastAPI app exposing `/api/health`, `/api/jobs`, and `/api/facets`.
- `cli.py`: thin command-line entrypoint for local and scheduled runs.
- `frontend/`: Next.js dashboard with URL-synced filters and a responsive table/detail view.
- `sources/`: future adapters for Foorilla, ATS feeds, and curated remote boards.

## Runtime

```text
ClickHouse analytics.jobs
  -> ClickHouseJobRepository
  -> deterministic quality rules
  -> FastAPI JSON
  -> Next.js dashboard
```

The first release does not create a persistent ClickHouse view. The logical
`job_quality_view` is composed from SQL reads plus Python rules, which keeps tag and
quality heuristics easy to inspect and change.

## Design Rules

- Every job keeps a source URL and score reasons.
- Vision is a first-class broad tag covering computer vision, OCR, video, multimodal,
  robotics perception, OpenCV, YOLO, SAM, and related wording.
- LLM output must pass schema validation before it can affect a report.
- Source adapters can fail independently; one bad source should not kill the run.
- Review is required before outreach or downstream distribution.

## Inspired By

- Job radar projects with provider-gated ingestion and explainable filters.
- OpenJobsEU style compliance-first policy checks.
- Recall-first job pipelines that keep diagnostics for missing sources.
