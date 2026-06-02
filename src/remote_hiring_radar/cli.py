from __future__ import annotations

import argparse
import json
from dataclasses import asdict

from .config import Settings
from .models import JobListing
from .pipeline import build_report


def sample_jobs() -> list[JobListing]:
    return [
        JobListing(
            source="sample",
            source_url="https://foorilla.com/hiring/sample-ai-agent",
            title="Remote AI Agent Engineer",
            company="Example Labs",
            location="Remote",
            description="Build LLM agents, RAG systems, and automation pipelines.",
            salary_text="$120k-$180k",
            tags=("ai", "agents", "remote"),
        ),
        JobListing(
            source="sample",
            source_url="https://example.com/local-role",
            title="Onsite Backend Engineer",
            company="LocalCo",
            location="New York",
            description="Maintain internal APIs.",
        ),
    ]


def main() -> int:
    parser = argparse.ArgumentParser(description="Build a remote hiring radar report.")
    parser.add_argument("--sample", action="store_true", help="Run with built-in sample data.")
    args = parser.parse_args()

    settings = Settings.from_env()
    jobs = sample_jobs() if args.sample else []
    report = build_report(jobs, limit=settings.max_items)
    print(json.dumps(asdict(report), indent=2, default=str))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
