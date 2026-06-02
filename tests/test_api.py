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
    assert body["items"][0]["target_bucket"] == "priority"
    assert "Vision Engineer" in body["items"][0]["priority_terms"]


def test_jobs_endpoint_serializes_target_fit_fields() -> None:
    repository = InMemoryJobRepository(
        jobs=[
            JobListing(
                source="foorilla.com",
                source_url="https://foorilla.com/jobs/target",
                title="Computer Vision Field Application Engineer",
                company="VisionCo",
                location="Remote",
                description="Customer deployment and training for OpenCV systems.",
                posted_at=date(2026, 5, 11),
            ),
            JobListing(
                source="foorilla.com",
                source_url="https://foorilla.com/jobs/downranked",
                title="Marketing Analyst",
                company="MarketCo",
                location="Remote",
                description="Analytics campaign work.",
                posted_at=date(2026, 5, 11),
            ),
        ]
    )
    client = TestClient(create_app(repository=repository, today=lambda: date(2026, 5, 11)))

    response = client.get("/api/jobs?days=3&sort=target_fit")

    assert response.status_code == 200
    body = response.json()
    assert body["items"][0]["target_bucket"] == "priority"
    assert body["items"][0]["target_score"] > body["items"][1]["target_score"]
    assert "Computer Vision Field Application Engineer" in body["items"][0]["priority_terms"]
    assert body["items"][1]["target_bucket"] == "downranked"
    assert body["items"][1]["downrank_terms"] == ["Marketing", "Analyst"]


def test_jobs_endpoint_defaults_to_personal_best_fit_sorting() -> None:
    repository = InMemoryJobRepository(
        jobs=[
            JobListing(
                source="foorilla.com",
                source_url="https://foorilla.com/jobs/newest-low-fit",
                title="Frontend Engineer",
                company="WebCo",
                location="Remote",
                description="Build React UI for marketing pages.",
                posted_at=date(2026, 5, 11),
            ),
            JobListing(
                source="foorilla.com",
                source_url="https://foorilla.com/jobs/older-best-fit",
                apply_url="https://foorilla.com/jobs/older-best-fit/apply",
                title="Computer Vision Field Application Engineer",
                company="VisionCo",
                location="Global / Travel",
                description=(
                    "Travel to customer sites for machine vision deployment, "
                    "implementation, integration, and training."
                ),
                posted_at=date(2026, 5, 9),
                salary_text="$150k",
            ),
        ]
    )
    client = TestClient(create_app(repository=repository, today=lambda: date(2026, 5, 11)))

    response = client.get("/api/jobs?days=7")

    assert response.status_code == 200
    body = response.json()
    assert body["items"][0]["title"] == "Computer Vision Field Application Engineer"
    assert body["items"][0]["personal_fit_bucket"] == "strong_match"
    assert "travel" in body["items"][0]["mobility_tags"]
    assert "field_application" in body["items"][0]["people_facing_tags"]
    assert "machine_vision" in body["items"][0]["domain_tags"]
    assert body["items"][1]["personal_fit_bucket"] == "downrank"
    assert "pure_frontend" in body["items"][1]["risk_tags"]


def test_jobs_endpoint_accepts_default_dashboard_page_size() -> None:
    repository = InMemoryJobRepository(
        jobs=[
            JobListing(
                source="foorilla.com",
                source_url="https://foorilla.com/jobs/1",
                title="Remote AI Engineer",
                company="AI Co",
                location="Remote",
                description="LLM systems.",
                posted_at=date(2026, 5, 11),
            )
        ]
    )
    client = TestClient(create_app(repository=repository, today=lambda: date(2026, 5, 11)))

    response = client.get("/api/jobs?days=7&limit=500")

    assert response.status_code == 200
    assert response.json()["limit"] == 500


def test_best_for_me_sort_keeps_high_scoring_downranked_jobs_below_good_matches() -> None:
    repository = InMemoryJobRepository(
        jobs=[
            JobListing(
                source="foorilla.com",
                source_url="https://foorilla.com/jobs/noisy",
                apply_url="https://foorilla.com/jobs/noisy/apply",
                title="Partner Value Solution Engineer Malware Research",
                company="NoisyCo",
                location="Global / Travel",
                description=(
                    "Solutions implementation deployment integration consulting AI platform "
                    "MLOps data platform cloud vision robotics edge AI customer training."
                ),
                posted_at=date(2026, 5, 11),
                salary_text="$180k",
            ),
            JobListing(
                source="foorilla.com",
                source_url="https://foorilla.com/jobs/good",
                apply_url="https://foorilla.com/jobs/good/apply",
                title="Remote Computer Vision Engineer",
                company="VisionCo",
                location="Remote",
                description="Computer vision and OCR production work.",
                posted_at=date(2026, 5, 10),
            ),
        ]
    )
    client = TestClient(create_app(repository=repository, today=lambda: date(2026, 5, 11)))

    response = client.get("/api/jobs?days=7&sort=best_for_me")

    assert response.status_code == 200
    body = response.json()
    assert body["items"][0]["title"] == "Remote Computer Vision Engineer"
    assert body["items"][0]["personal_fit_bucket"] == "good_match"
    assert body["items"][1]["personal_fit_bucket"] == "downrank"


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
    assert body["target_fit"]["standard"] == 2
    assert body["personal_fit"]["maybe"] == 2


def test_overview_endpoint_summarizes_current_data_quality() -> None:
    repository = InMemoryJobRepository(
        jobs=[
            JobListing(
                source="foorilla.com",
                source_url="https://foorilla.com/jobs/1",
                apply_url="https://foorilla.com/jobs/1/apply",
                title="Remote Computer Vision Engineer",
                company="VisionCo",
                location="Remote (US)",
                description="Computer vision and OCR production work.",
                posted_at=date(2026, 5, 11),
                salary_text="$160k",
            ),
            JobListing(
                source="foorilla.com",
                source_url="https://foorilla.com/jobs/2",
                title="Remote Computer Vision Engineer",
                company="VisionCo",
                location="Remote (US)",
                description="Computer vision repost.",
                posted_at=date(2026, 5, 10),
            ),
            JobListing(
                source="linkedin",
                source_url="",
                title="Hybrid Security Analyst",
                company="SecureCo",
                location="San Francisco",
                description="Hybrid AI security analytics.",
                posted_at=date(2026, 5, 9),
            ),
        ]
    )
    client = TestClient(create_app(repository=repository, today=lambda: date(2026, 5, 11)))

    response = client.get("/api/overview?days=7")

    assert response.status_code == 200
    body = response.json()
    assert body["total_observed"] == 3
    assert body["latest_posted_date"] == "2026-05-11"
    assert body["coverage"]["source_url"]["count"] == 2
    assert body["coverage"]["salary"]["count"] == 1
    assert body["coverage"]["remote_friendly"]["count"] == 2
    assert body["quality"]["duplicate_groups"] == 1
    assert body["quality"]["repost_like_records"] == 2
    assert body["target_fit"]["priority"] == 2
    assert body["target_fit"]["downranked"] == 1
    assert body["personal_fit"]["good_match"] == 2
    assert body["personal_fit"]["downrank"] == 1
    assert body["top_sources"][0] == {"name": "foorilla.com", "count": 2, "ratio": 0.6667}
    assert body["top_companies"][0] == {"name": "VisionCo", "count": 2, "ratio": 0.6667}
