from __future__ import annotations

from datetime import date
from urllib.parse import parse_qs, urlparse

from remote_hiring_radar.models import JobListing
from remote_hiring_radar.quality import evaluate_job_quality
from remote_hiring_radar.service import serialize_job


def test_foorilla_links_use_configured_login_redirect(monkeypatch) -> None:
    monkeypatch.setenv("FOORILLA_AUTH_URL", "https://foorilla.com/account/signin/auth/?sesame=test")
    job = JobListing(
        source="foorilla.com",
        source_url="https://foorilla.com/hiring/jobs/vision-engineer-123/",
        title="Vision Engineer",
        company="Vision Co",
        location="Remote",
        description="Computer vision role.",
        posted_at=date(2026, 5, 12),
    )
    quality = evaluate_job_quality(job, today=date(2026, 5, 12), repost_count=1)

    body = serialize_job(job, quality)

    assert body["source_url"] == "https://foorilla.com/hiring/jobs/vision-engineer-123/"
    assert body["apply_url"] == ""
    assert body["source_link_url"].startswith("https://foorilla.com/account/signin/auth/")
    assert body["apply_link_url"].startswith("https://foorilla.com/account/signin/auth/")
    source_query = parse_qs(urlparse(str(body["source_link_url"])).query)
    apply_query = parse_qs(urlparse(str(body["apply_link_url"])).query)
    assert source_query["next"] == ["https://foorilla.com/hiring/jobs/vision-engineer-123/"]
    assert apply_query["next"] == ["https://foorilla.com/hiring/jobs/vision-engineer-123/"]


def test_non_foorilla_links_remain_direct(monkeypatch) -> None:
    monkeypatch.setenv("FOORILLA_AUTH_URL", "https://foorilla.com/account/signin/auth/?sesame=test")
    job = JobListing(
        source="greenhouse",
        source_url="https://boards.greenhouse.io/example/jobs/1",
        apply_url="https://boards.greenhouse.io/example/jobs/1/apply",
        title="Data Engineer",
        company="Data Co",
        location="Remote",
        description="Data platform role.",
        posted_at=date(2026, 5, 12),
    )
    quality = evaluate_job_quality(job, today=date(2026, 5, 12), repost_count=1)

    body = serialize_job(job, quality)

    assert body["source_link_url"] == "https://boards.greenhouse.io/example/jobs/1"
    assert body["apply_link_url"] == "https://boards.greenhouse.io/example/jobs/1/apply"
