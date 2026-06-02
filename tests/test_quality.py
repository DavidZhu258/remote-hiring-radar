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


def test_target_fit_prioritizes_vision_solutions_roles() -> None:
    job = JobListing(
        source="foorilla.com",
        source_url="https://foorilla.com/jobs/target",
        title="Senior Computer Vision Solutions Engineer",
        company="VisionCo",
        location="Remote",
        description="Customer-facing image recognition deployments.",
    )

    quality = evaluate_job_quality(job, today=date(2026, 5, 11))

    assert quality.target_bucket == "priority"
    assert quality.target_score > 0
    assert "Computer Vision Solutions Engineer" in quality.priority_terms
    assert "Solutions" in quality.priority_terms
    assert "Vision" in quality.priority_terms
    assert quality.downrank_terms == ()


def test_target_fit_downranks_titles_with_only_non_priority_terms() -> None:
    job = JobListing(
        source="foorilla.com",
        source_url="https://foorilla.com/jobs/non-target",
        title="Frontend QA Tester",
        company="WebCo",
        location="Remote",
        description="General web testing.",
    )

    quality = evaluate_job_quality(job, today=date(2026, 5, 11))

    assert quality.target_bucket == "downranked"
    assert quality.target_score < 0
    assert quality.priority_terms == ()
    assert set(quality.downrank_terms) == {"Frontend", "QA", "Tester"}


def test_personal_fit_prioritizes_global_customer_facing_vision_delivery() -> None:
    job = JobListing(
        source="foorilla.com",
        source_url="https://foorilla.com/jobs/best-fit",
        apply_url="https://foorilla.com/jobs/best-fit/apply",
        title="Computer Vision Field Application Engineer",
        company="VisionCo",
        location="Global / Travel",
        description=(
            "Travel internationally to customer sites to deploy machine vision and "
            "edge AI inspection systems, lead implementation workshops, integrate "
            "OpenCV pipelines, and train operators."
        ),
        posted_at=date(2026, 5, 11),
        salary_text="$150k",
    )

    quality = evaluate_job_quality(job, today=date(2026, 5, 11))

    assert quality.personal_fit_bucket == "strong_match"
    assert quality.personal_fit_score >= 40
    assert set(quality.domain_tags) >= {"vision", "machine_vision", "edge_ai"}
    assert set(quality.people_facing_tags) >= {"field_application", "implementation", "training"}
    assert set(quality.mobility_tags) >= {"global", "travel", "customer_site"}
    assert quality.risk_tags == ()
    assert "customer-facing delivery role" in quality.fit_reasons


def test_personal_fit_marks_ai_platform_consulting_as_good_transition_role() -> None:
    job = JobListing(
        source="foorilla.com",
        source_url="https://foorilla.com/jobs/ai-platform-consultant",
        apply_url="https://foorilla.com/jobs/ai-platform-consultant/apply",
        title="AI Platform Implementation Consultant",
        company="PlatformCo",
        location="Remote",
        description=(
            "Run customer workshops, integrate MLOps and data platform workflows, "
            "support deployment, and enable enterprise teams."
        ),
        posted_at=date(2026, 5, 11),
    )

    quality = evaluate_job_quality(job, today=date(2026, 5, 11))

    assert quality.personal_fit_bucket in {"strong_match", "good_match"}
    assert set(quality.domain_tags) >= {"ai_platform", "mlops", "data_platform"}
    assert set(quality.people_facing_tags) >= {"implementation", "consulting", "enablement"}
    assert "technical transition fit" in quality.fit_reasons


def test_personal_fit_downranks_pure_frontend_marketing_roles() -> None:
    job = JobListing(
        source="linkedin",
        source_url="https://linkedin.com/jobs/frontend-marketing",
        title="Frontend Marketing Analyst",
        company="WebCo",
        location="Remote",
        description="React landing pages, campaign analytics, and marketing operations.",
        posted_at=date(2026, 5, 11),
    )

    quality = evaluate_job_quality(job, today=date(2026, 5, 11))

    assert quality.personal_fit_bucket == "downrank"
    assert quality.personal_fit_score < 0
    assert set(quality.risk_tags) >= {"pure_frontend", "marketing", "analyst_only"}
    assert quality.people_facing_tags == ()
    assert "role appears outside the target transition path" in quality.fit_reasons


def test_personal_fit_does_not_over_promote_security_research_noise() -> None:
    job = JobListing(
        source="foorilla.com",
        source_url="https://foorilla.com/jobs/security-noise",
        apply_url="https://foorilla.com/jobs/security-noise/apply",
        title="Manager, Development - Malware Research",
        company="SecureCo",
        location="Remote",
        description=(
            "Lead malware research and vulnerability analysis. Similar jobs mention "
            "AI platform, MLOps, implementation consultant, pre sales, and data platform."
        ),
        posted_at=date(2026, 5, 11),
        salary_text="$150k",
    )

    quality = evaluate_job_quality(job, today=date(2026, 5, 11))

    assert quality.personal_fit_bucket == "downrank"
    assert "security_only" in quality.risk_tags
    assert "malware_research" in quality.risk_tags


def test_vision_insurance_does_not_count_as_computer_vision() -> None:
    job = JobListing(
        source="foorilla.com",
        source_url="https://foorilla.com/jobs/workfront",
        apply_url="https://foorilla.com/jobs/workfront/apply",
        title="Adobe Workfront Solution Architect",
        company="WorkflowCo",
        location="Remote",
        description=(
            "Implement workflow automation for enterprise customers. Benefits include "
            "medical, dental, and vision insurance."
        ),
        posted_at=date(2026, 5, 11),
        salary_text="$130k",
    )

    quality = evaluate_job_quality(job, today=date(2026, 5, 11))

    assert "vision" not in quality.role_tags
    assert "vision" not in quality.domain_tags


def test_generic_infra_support_does_not_become_strong_personal_fit() -> None:
    job = JobListing(
        source="foorilla.com",
        source_url="https://foorilla.com/jobs/backup-specialist",
        apply_url="https://foorilla.com/jobs/backup-specialist/apply",
        title="Senior Backup Specialist",
        company="InfraCo",
        location="Remote",
        description=(
            "Support global onsite implementation and consulting for backup systems, "
            "cloud infrastructure, data retention, and customer enablement."
        ),
        posted_at=date(2026, 5, 11),
        salary_text="$120k",
    )

    quality = evaluate_job_quality(job, today=date(2026, 5, 11))

    assert quality.personal_fit_bucket != "strong_match"
