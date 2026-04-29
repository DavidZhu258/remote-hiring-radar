# Remote Hiring Radar

Remote Hiring Radar is a small internal-first product for finding remote work and hiring signals without becoming a full job board.

It answers one question: which remote AI/data/agent roles or hiring movements deserve attention today?

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
- Local JSON/SQLite first, ClickHouse export later.

Out of scope:

- Auto-applying to jobs.
- Full CRM or ATS replacement.
- Heavy multi-agent orchestration.

## Architecture

```text
Sources -> Normalize -> Dedupe -> Score -> Shortlist -> Report/API
```

The structure follows the simpler patterns seen in recent open-source job radar projects: adapter contracts, deterministic scoring, a CLI pipeline, and CI-tested core logic before adding UI.

## Quick Start

```bash
python -m pip install -e ".[dev]"
python -m pytest -q
remote-hiring-radar --sample
```

## Configuration

Copy `.env.example` to `.env` for local runs. Keep real tokens in environment variables or a secret manager, never in the repo.

## CI

GitHub Actions runs tests, compile checks, and a lightweight secret scan on every push and pull request.

