from __future__ import annotations

from collections import Counter
from dataclasses import dataclass
from datetime import date

from .models import JobListing
from .quality import evaluate_job_quality, normalize_duplicate_key
from .repository import JobRepository, safe_days, sort_jobs_newest_first

ALLOWED_DAYS = {1, 3, 7, 30}


@dataclass(frozen=True)
class JobFilters:
    days: int = 7
    tags: tuple[str, ...] = ()
    remote_quality: str = ""
    salary_status: str = ""
    source: str = ""
    q: str = ""
    hide_reposts: bool = False
    limit: int = 50
    offset: int = 0
    sort: str = "fresh"


def get_jobs(repository: JobRepository, filters: JobFilters, *, today: date) -> dict[str, object]:
    days = normalize_days(filters.days)
    raw_jobs = repository.fetch_jobs(
        days=days,
        q=filters.q,
        source=filters.source,
        max_rows=max(filters.limit + filters.offset + 500, 1000),
    )
    duplicate_counts = Counter(normalize_duplicate_key(job) for job in raw_jobs)

    enriched = [
        (
            job,
            evaluate_job_quality(
                job, today=today, repost_count=duplicate_counts[normalize_duplicate_key(job)]
            ),
        )
        for job in sort_jobs_newest_first(raw_jobs)
    ]
    filtered = []
    seen_duplicate_keys: set[str] = set()
    for job, quality in enriched:
        if filters.tags and not all(tag in quality.role_tags for tag in filters.tags):
            continue
        if filters.remote_quality and quality.remote_quality != filters.remote_quality:
            continue
        if filters.salary_status and quality.salary_status != filters.salary_status:
            continue
        if filters.hide_reposts and quality.duplicate_key in seen_duplicate_keys:
            continue
        seen_duplicate_keys.add(quality.duplicate_key)
        filtered.append((job, quality))

    if filters.sort == "source":
        filtered.sort(
            key=lambda item: (item[0].source, item[0].posted_at or date.min), reverse=True
        )
    elif filters.sort == "company":
        filtered.sort(key=lambda item: item[0].company.lower())

    limit = max(1, min(filters.limit, 100))
    offset = max(filters.offset, 0)
    page = filtered[offset : offset + limit]
    return {
        "total": len(filtered),
        "limit": limit,
        "offset": offset,
        "items": [serialize_job(job, quality) for job, quality in page],
    }


def get_facets(repository: JobRepository, filters: JobFilters, *, today: date) -> dict[str, object]:
    raw_jobs = repository.fetch_jobs(
        days=normalize_days(filters.days),
        q=filters.q,
        source="",
        max_rows=10000,
    )
    duplicate_counts = Counter(normalize_duplicate_key(job) for job in raw_jobs)
    counters = {
        "sources": Counter[str](),
        "role_tags": Counter[str](),
        "remote_quality": Counter[str](),
        "salary_status": Counter[str](),
        "freshness": Counter[str](),
    }
    for job in raw_jobs:
        quality = evaluate_job_quality(
            job,
            today=today,
            repost_count=duplicate_counts[normalize_duplicate_key(job)],
        )
        counters["sources"][job.source or "unknown"] += 1
        for tag in quality.role_tags:
            counters["role_tags"][tag] += 1
        counters["remote_quality"][quality.remote_quality] += 1
        counters["salary_status"][quality.salary_status] += 1
        counters["freshness"][quality.freshness_bucket] += 1

    return {name: dict(counter) for name, counter in counters.items()}


def get_health(repository: JobRepository, *, today: date) -> dict[str, object]:
    repository.check()
    latest = repository.latest_posted_date()
    stale = latest is None or (today - latest).days > 1
    return {
        "status": "ok",
        "clickhouse": "connected",
        "latest_posted_date": latest.isoformat() if latest else None,
        "stale": stale,
        "warnings": ["job data is stale"] if stale else [],
    }


def serialize_job(job: JobListing, quality: object) -> dict[str, object]:
    return {
        "job_id": job.job_id,
        "title": job.title,
        "company": job.company,
        "location": job.location,
        "description": job.description,
        "requirements": job.requirements,
        "responsibilities": job.responsibilities,
        "benefits": job.benefits,
        "skills": job.skills,
        "posted_at": job.posted_at.isoformat() if job.posted_at else None,
        "salary": job.salary_text,
        "salary_detail": job.salary_detail,
        "budget_min": job.budget_min,
        "budget_max": job.budget_max,
        "budget_currency": job.budget_currency,
        "source": job.source,
        "source_url": job.source_url,
        "apply_url": job.apply_url,
        "freshness_bucket": quality.freshness_bucket,
        "source_trust": quality.source_trust,
        "remote_quality": quality.remote_quality,
        "role_tags": list(quality.role_tags),
        "salary_status": quality.salary_status,
        "duplicate_key": quality.duplicate_key,
        "repost_count": quality.repost_count,
        "quality_reasons": list(quality.quality_reasons),
        "exclude_reasons": list(quality.exclude_reasons),
        "raw": job.raw,
    }


def normalize_days(days: int) -> int:
    normalized = safe_days(days)
    if normalized in ALLOWED_DAYS:
        return normalized
    if normalized < 3:
        return 1
    if normalized < 7:
        return 3
    if normalized < 30:
        return 7
    return 30
