from __future__ import annotations

from datetime import date

from fastapi.testclient import TestClient

from remote_hiring_radar.api import create_app
from remote_hiring_radar.models import JobListing
from remote_hiring_radar.repository import InMemoryJobRepository


def test_jobs_endpoint_filters_vision_and_hides_reposts() -> None:
    repository = InMemoryJobRepository(
        jobs=[
            JobListing(
                source="foorilla.com",
                source_url="https://foorilla.com/jobs/1",
                title="Remote Vision Engineer",
                company="VisionCo",
                location="Remote",
                description="Computer vision and OCR production work.",
                posted_at=date(2026, 5, 11),
                salary_text="$160k",
            ),
            JobListing(
                source="foorilla.com",
                source_url="https://foorilla.com/jobs/2",
                title="remote vision engineer",
                company="visionco",
                location="Remote",
                description="Duplicate repost for image recognition.",
                posted_at=date(2026, 5, 10),
                salary_text="$160k",
            ),
            JobListing(
                source="jobsdb",
                source_url="https://jobsdb.com/job/3",
                title="Data Analyst",
                company="DataCo",
                location="Bangkok",
                description="Dashboards and SQL.",
                posted_at=date(2026, 5, 11),
            ),
        ]
    )
    client = TestClient(create_app(repository=repository, today=lambda: date(2026, 5, 11)))

    response = client.get("/api/jobs?tags=vision&days=3&hide_reposts=true")

    assert response.status_code == 200
    body = response.json()
    assert body["total"] == 1
    assert body["items"][0]["role_tags"] == ["vision"]
    assert body["items"][0]["repost_count"] == 2
    assert body["items"][0]["quality_reasons"]


def test_health_endpoint_reports_stale_data_without_leaking_config() -> None:
    repository = InMemoryJobRepository(
        jobs=[
            JobListing(
                source="foorilla.com",
                source_url="https://foorilla.com/jobs/1",
                title="Remote AI Engineer",
                company="AI Co",
                location="Remote",
                description="LLM systems.",
                posted_at=date(2026, 5, 8),
            )
        ],
        config={"password": "super-secret-password"},
    )
    client = TestClient(create_app(repository=repository, today=lambda: date(2026, 5, 11)))

    response = client.get("/api/health")

    assert response.status_code == 200
    body = response.json()
    assert body["status"] == "ok"
    assert body["clickhouse"] == "connected"
    assert body["latest_posted_date"] == "2026-05-08"
    assert body["stale"] is True
    assert "super-secret-password" not in response.text


def test_facets_endpoint_returns_filter_counts() -> None:
    repository = InMemoryJobRepository(
        jobs=[
            JobListing(
                source="foorilla.com",
                source_url="https://foorilla.com/jobs/1",
                title="Remote Agent Engineer",
                company="AgentCo",
                location="Remote",
                description="Agentic LLM workflows.",
                posted_at=date(2026, 5, 11),
                salary_text="$120k",
            ),
            JobListing(
                source="jobsdb",
                source_url="https://jobsdb.com/job/2",
                title="Data Engineer",
                company="DataCo",
                location="Remote",
                description="ETL and analytics platform.",
                posted_at=date(2026, 5, 10),
            ),
        ]
    )
    client = TestClient(create_app(repository=repository, today=lambda: date(2026, 5, 11)))

    response = client.get("/api/facets?days=7")

    assert response.status_code == 200
    body = response.json()
    assert body["sources"]["foorilla.com"] == 1
    assert body["role_tags"]["agent"] == 1
    assert body["role_tags"]["data"] == 1
    assert body["salary_status"]["has_salary"] == 1
