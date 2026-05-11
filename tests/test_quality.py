from __future__ import annotations

from datetime import date

from remote_hiring_radar.models import JobListing
from remote_hiring_radar.quality import evaluate_job_quality, normalize_duplicate_key


def test_vision_remote_salary_and_duplicate_quality_fields() -> None:
    job = JobListing(
        source="foorilla.com",
        source_url="https://foorilla.com/jobs/vision",
        title="Remote Computer Vision Engineer",
        company="VisionCo",
        location="Remote (US)",
        description="Build image recognition and OCR pipelines with OpenCV, YOLO, and SAM.",
        posted_at=date(2026, 5, 11),
        salary_text="$150k-$190k",
    )

    quality = evaluate_job_quality(job, today=date(2026, 5, 11), repost_count=2)

    assert quality.freshness_bucket == "0-24h"
    assert quality.source_trust == "direct_source"
    assert quality.remote_quality == "country-limited"
    assert quality.role_tags == ("vision",)
    assert quality.salary_status == "has_salary"
    assert quality.repost_count == 2
    assert "broad vision match" in quality.quality_reasons
    assert "has compensation signal" in quality.quality_reasons


def test_hybrid_unknown_salary_and_aggregator_risk_fields() -> None:
    job = JobListing(
        source="linkedin",
        source_url="https://linkedin.com/jobs/view/example",
        title="Hybrid ML Platform Lead",
        company="Example",
        location="San Francisco, CA",
        description="Hybrid schedule, three days in office, Kubernetes platform and ML tooling.",
        posted_at=date(2026, 5, 6),
    )

    quality = evaluate_job_quality(job, today=date(2026, 5, 11), repost_count=1)

    assert quality.freshness_bucket == "4-7d"
    assert quality.source_trust == "aggregator"
    assert quality.remote_quality == "hybrid-suspect"
    assert quality.salary_status == "no_salary"
    assert set(quality.role_tags) >= {"ai", "infra"}
    assert "hybrid or onsite language" in quality.exclude_reasons


def test_zero_budget_does_not_count_as_salary_signal() -> None:
    job = JobListing(
        source="foorilla.com",
        source_url="https://foorilla.com/jobs/no-salary",
        title="Remote Vision Engineer",
        company="VisionCo",
        location="Remote",
        description="Computer vision pipelines.",
        budget_min=0.0,
        budget_max=0.0,
    )

    quality = evaluate_job_quality(job, today=date(2026, 5, 11))

    assert quality.salary_status == "no_salary"


def test_duplicate_key_normalization_is_stable() -> None:
    left = JobListing(
        source="a",
        source_url="https://a",
        title="Sr. Computer-Vision Engineer",
        company=" VisionCo, Inc. ",
        location="Remote - United States",
        description="",
    )
    right = JobListing(
        source="b",
        source_url="https://b",
        title="sr computer vision engineer",
        company="visionco inc",
        location="remote united states",
        description="",
    )

    assert normalize_duplicate_key(left) == normalize_duplicate_key(right)
