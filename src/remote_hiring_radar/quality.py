from __future__ import annotations

import re
from dataclasses import dataclass
from datetime import date
from urllib.parse import urlparse

from .models import JobListing

TAG_ORDER = ("vision", "ai", "data", "agent", "security", "infra")

TAG_TERMS: dict[str, tuple[str, ...]] = {
    "vision": (
        "image recognition",
        "computer vision",
        "visual recognition",
        "ocr",
        "video",
        "multimodal",
        "robotics perception",
        "opencv",
        "yolo",
        "sam",
        "segment anything",
        "vision",
    ),
    "ai": (
        "ai",
        "artificial intelligence",
        "machine learning",
        "ml",
        "llm",
        "genai",
        "generative ai",
        "rag",
        "model training",
        "deep learning",
    ),
    "data": (
        "data",
        "analytics",
        "etl",
        "elt",
        "warehouse",
        "lakehouse",
        "bi",
        "sql",
        "spark",
        "dbt",
    ),
    "agent": (
        "agent",
        "agents",
        "agentic",
        "autonomous workflow",
        "tool calling",
        "multi-agent",
        "multi agent",
    ),
    "security": (
        "security",
        "cybersecurity",
        "infosec",
        "appsec",
        "soc",
        "threat",
        "vulnerability",
    ),
    "infra": (
        "infra",
        "infrastructure",
        "platform",
        "devops",
        "sre",
        "kubernetes",
        "k8s",
        "terraform",
        "cloud",
    ),
}

DIRECT_SOURCE_TERMS = (
    "foorilla",
    "greenhouse",
    "lever",
    "ashby",
    "workday",
    "smartrecruiters",
    "recruitee",
    "bamboohr",
    "wellfound",
    "jobs.ashbyhq",
)
AGGREGATOR_TERMS = (
    "linkedin",
    "indeed",
    "glassdoor",
    "jobsdb",
    "jobstreet",
    "ziprecruiter",
    "hiring.cafe",
    "hiringcafe",
)
WORLDWIDE_REMOTE_TERMS = (
    "worldwide",
    "anywhere",
    "work from anywhere",
    "global remote",
    "fully distributed",
    "distributed team",
)
LIMITED_REMOTE_TERMS = (
    "remote (us",
    "remote us",
    "united states",
    "usa",
    "u.s.",
    "canada",
    "uk",
    "united kingdom",
    "europe",
    "emea",
    "apac",
    "latin america",
    "latam",
    "timezone",
    "time zone",
)
HYBRID_TERMS = (
    "hybrid",
    "onsite",
    "on-site",
    "in office",
    "in-office",
    "office based",
    "days in office",
)


@dataclass(frozen=True)
class JobQuality:
    freshness_bucket: str
    source_trust: str
    remote_quality: str
    role_tags: tuple[str, ...]
    salary_status: str
    duplicate_key: str
    repost_count: int
    quality_reasons: tuple[str, ...]
    exclude_reasons: tuple[str, ...]


def normalize_text(value: object) -> str:
    text = str(value or "").lower()
    text = re.sub(r"[^a-z0-9]+", " ", text)
    return re.sub(r"\s+", " ", text).strip()


def normalize_duplicate_key(job: JobListing) -> str:
    return "|".join(
        [
            normalize_text(job.title),
            normalize_text(job.company),
            normalize_text(job.location),
        ]
    )


def evaluate_job_quality(
    job: JobListing,
    *,
    today: date | None = None,
    repost_count: int = 1,
) -> JobQuality:
    today = today or date.today()
    role_tags = detect_role_tags(job)
    freshness_bucket = detect_freshness_bucket(job, today)
    source_trust = detect_source_trust(job)
    remote_quality = detect_remote_quality(job)
    salary_status = detect_salary_status(job)
    duplicate_key = normalize_duplicate_key(job)

    quality_reasons = build_quality_reasons(
        role_tags=role_tags,
        freshness_bucket=freshness_bucket,
        source_trust=source_trust,
        remote_quality=remote_quality,
        salary_status=salary_status,
        repost_count=repost_count,
    )
    exclude_reasons = build_exclude_reasons(
        job=job,
        freshness_bucket=freshness_bucket,
        remote_quality=remote_quality,
        salary_status=salary_status,
    )

    return JobQuality(
        freshness_bucket=freshness_bucket,
        source_trust=source_trust,
        remote_quality=remote_quality,
        role_tags=role_tags,
        salary_status=salary_status,
        duplicate_key=duplicate_key,
        repost_count=repost_count,
        quality_reasons=quality_reasons,
        exclude_reasons=exclude_reasons,
    )


def detect_role_tags(job: JobListing) -> tuple[str, ...]:
    text = normalized_job_blob(job)
    detected: list[str] = []
    for tag in TAG_ORDER:
        if any(term_matches(text, term) for term in TAG_TERMS[tag]):
            detected.append(tag)
    return tuple(detected)


def detect_freshness_bucket(job: JobListing, today: date) -> str:
    if job.posted_at is None:
        return "unknown"
    age_days = max((today - job.posted_at).days, 0)
    if age_days <= 1:
        return "0-24h"
    if age_days <= 3:
        return "1-3d"
    if age_days <= 7:
        return "4-7d"
    if age_days <= 30:
        return "8-30d"
    return "stale"


def detect_source_trust(job: JobListing) -> str:
    source = " ".join([job.source, job.source_url, parsed_hostname(job.source_url)]).lower()
    if any(term in source for term in DIRECT_SOURCE_TERMS):
        return "direct_source"
    if any(term in source for term in AGGREGATOR_TERMS):
        return "aggregator"
    return "unknown"


def detect_remote_quality(job: JobListing) -> str:
    raw_text = raw_job_blob(job)
    normalized = normalize_text(raw_text)
    if any(term in raw_text.lower() or term_matches(normalized, term) for term in HYBRID_TERMS):
        return "hybrid-suspect"
    if not term_matches(normalized, "remote"):
        return "unknown"
    if any(
        term in raw_text.lower() or term_matches(normalized, term) for term in LIMITED_REMOTE_TERMS
    ):
        return "country-limited"
    if normalize_text(job.location) == "remote":
        return "worldwide"
    if any(
        term in raw_text.lower() or term_matches(normalized, term)
        for term in WORLDWIDE_REMOTE_TERMS
    ):
        return "worldwide"
    return "unknown"


def detect_salary_status(job: JobListing) -> str:
    if job.salary_text.strip() or job.salary_detail.strip():
        return "has_salary"
    if positive_number(job.budget_min) or positive_number(job.budget_max):
        return "has_salary"
    return "no_salary"


def positive_number(value: float | None) -> bool:
    return value is not None and value > 0


def build_quality_reasons(
    *,
    role_tags: tuple[str, ...],
    freshness_bucket: str,
    source_trust: str,
    remote_quality: str,
    salary_status: str,
    repost_count: int,
) -> tuple[str, ...]:
    reasons: list[str] = []
    if "vision" in role_tags:
        reasons.append("broad vision match")
    for tag in role_tags:
        if tag != "vision":
            reasons.append(f"{tag} role signal")
    if freshness_bucket in {"0-24h", "1-3d", "4-7d"}:
        reasons.append("fresh posting")
    if source_trust == "direct_source":
        reasons.append("direct source signal")
    if remote_quality in {"worldwide", "country-limited"}:
        reasons.append("remote-friendly")
    if salary_status == "has_salary":
        reasons.append("has compensation signal")
    if repost_count > 1:
        reasons.append(f"{repost_count} repost-like records")
    return tuple(reasons)


def build_exclude_reasons(
    *,
    job: JobListing,
    freshness_bucket: str,
    remote_quality: str,
    salary_status: str,
) -> tuple[str, ...]:
    reasons: list[str] = []
    if remote_quality == "hybrid-suspect":
        reasons.append("hybrid or onsite language")
    if remote_quality == "unknown" and "remote" not in normalize_text(raw_job_blob(job)):
        reasons.append("remote evidence missing")
    if salary_status == "no_salary":
        reasons.append("no salary signal")
    if freshness_bucket == "stale":
        reasons.append("stale posting")
    if not job.source_url:
        reasons.append("source URL missing")
    return tuple(reasons)


def normalized_job_blob(job: JobListing) -> str:
    return normalize_text(raw_job_blob(job))


def raw_job_blob(job: JobListing) -> str:
    return " ".join(
        [
            job.title,
            job.company,
            job.location,
            job.description,
            job.requirements,
            job.responsibilities,
            job.benefits,
            job.skills,
            job.job_type,
            " ".join(job.tags),
        ]
    )


def parsed_hostname(url: str) -> str:
    try:
        return urlparse(url).netloc
    except ValueError:
        return ""


def term_matches(text: str, term: str) -> bool:
    normalized_term = normalize_text(term)
    if not normalized_term:
        return False
    pattern = rf"(?<![a-z0-9]){re.escape(normalized_term)}(?![a-z0-9])"
    return re.search(pattern, text) is not None
