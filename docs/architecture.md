# Architecture

Remote Hiring Radar is a modular monolith with a CLI-first core.

## Modules

- `models.py`: typed domain objects for jobs, scored jobs, and reports.
- `pipeline.py`: deterministic normalize, score, and report logic.
- `cli.py`: thin command-line entrypoint for local and scheduled runs.
- `sources/`: future adapters for Foorilla, ATS feeds, and curated remote boards.

## Design Rules

- Every job keeps a source URL and score reasons.
- LLM output must pass schema validation before it can affect a report.
- Source adapters can fail independently; one bad source should not kill the run.
- Review is required before outreach or downstream distribution.

## Inspired By

- Job radar projects with provider-gated ingestion and explainable filters.
- OpenJobsEU style compliance-first policy checks.
- Recall-first job pipelines that keep diagnostics for missing sources.

