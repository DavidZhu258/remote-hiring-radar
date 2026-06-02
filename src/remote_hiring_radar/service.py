from __future__ import annotations

from collections import Counter
from collections.abc import Iterable
from dataclasses import dataclass
from datetime import date

from .links import apply_link_url, source_link_url
from .models import JobListing
from .quality import evaluate_job_quality, normalize_duplicate_key
from .repository import JobRepository, safe_days, sort_jobs_newest_first

ALLOWED_DAYS = {1, 3, 7, 30}
FACET_SAMPLE_LIMIT = 500
OVERVIEW_SAMPLE_LIMIT = 500


@dataclass(frozen=True)
class JobFilters:
    days: int = 7
    tags: tuple[str, ...] = ()
    remote_quality: str = ""
    salary_status: str = ""
    source: str = ""
    q: str = ""
    hide_reposts: bool = False
    limit: int = 500
    offset: int = 0
    sort: str = "best_for_me"


def get_jobs(repository: JobRepository, filters: JobFilters, *, today: date) -> dict[str, object]:
    days = normalize_days(filters.days)
    candidate_padding = 250
    candidate_floor = 500
    raw_jobs = repository.fetch_jobs(
        days=days,
        q=filters.q,
        source=filters.source,
        max_rows=max(filters.limit + filters.offset + candidate_padding, candidate_floor),
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

    if filters.sort in {"best_for_me", "personal_fit"}:
        filtered.sort(
            key=lambda item: (
                personal_fit_rank(item[1].personal_fit_bucket),
                item[1].personal_fit_score,
                item[1].target_score,
                item[0].posted_at or date.min,
                item[0].company.lower(),
            ),
            reverse=True,
        )
    elif filters.sort == "source":
        filtered.sort(
            key=lambda item: (item[0].source, item[0].posted_at or date.min), reverse=True
        )
    elif filters.sort == "company":
        filtered.sort(key=lambda item: item[0].company.lower())
    elif filters.sort == "target_fit":
        filtered.sort(
            key=lambda item: (
                item[1].target_score,
                item[0].posted_at or date.min,
                item[0].company.lower(),
            ),
            reverse=True,
        )

    limit = max(1, min(filters.limit, 500))
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
        max_rows=FACET_SAMPLE_LIMIT,
        ordered=False,
    )
    duplicate_counts = Counter(normalize_duplicate_key(job) for job in raw_jobs)
    counters = {
        "sources": Counter[str](),
        "role_tags": Counter[str](),
        "remote_quality": Counter[str](),
        "salary_status": Counter[str](),
        "freshness": Counter[str](),
        "target_fit": Counter[str](),
        "personal_fit": Counter[str](),
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
        counters["target_fit"][quality.target_bucket] += 1
        counters["personal_fit"][quality.personal_fit_bucket] += 1

    return {name: dict(counter) for name, counter in counters.items()}


def get_overview(
    repository: JobRepository, filters: JobFilters, *, today: date
) -> dict[str, object]:
    raw_jobs = repository.fetch_jobs(
        days=normalize_days(filters.days),
        q=filters.q,
        source=filters.source,
        max_rows=OVERVIEW_SAMPLE_LIMIT,
    )
    duplicate_counts = Counter(normalize_duplicate_key(job) for job in raw_jobs)
    enriched = [
        (
            job,
            evaluate_job_quality(
                job,
                today=today,
                repost_count=duplicate_counts[normalize_duplicate_key(job)],
            ),
        )
        for job in raw_jobs
    ]
    total = len(enriched)
    latest = latest_posted_date(job for job, _quality in enriched)

    source_counter = Counter(job.source or "unknown" for job, _quality in enriched)
    company_counter = Counter(
        (job.company or "unknown").strip() or "unknown" for job, _ in enriched
    )
    freshness_counter = Counter(quality.freshness_bucket for _job, quality in enriched)
    remote_counter = Counter(quality.remote_quality for _job, quality in enriched)
    salary_counter = Counter(quality.salary_status for _job, quality in enriched)
    target_fit_counter = Counter(quality.target_bucket for _job, quality in enriched)
    personal_fit_counter = Counter(quality.personal_fit_bucket for _job, quality in enriched)
    tag_counter: Counter[str] = Counter()

    source_url_count = 0
    apply_url_count = 0
    salary_count = 0
    remote_friendly_count = 0
    direct_source_count = 0
    missing_remote_evidence_count = 0
    for job, quality in enriched:
        if job.source_url.strip():
            source_url_count += 1
        if job.apply_url.strip():
            apply_url_count += 1
        if quality.salary_status == "has_salary":
            salary_count += 1
        if quality.remote_quality in {"worldwide", "country-limited"}:
            remote_friendly_count += 1
        if quality.source_trust == "direct_source":
            direct_source_count += 1
        if "remote evidence missing" in quality.exclude_reasons:
            missing_remote_evidence_count += 1
        for tag in quality.role_tags:
            tag_counter[tag] += 1

    duplicate_groups = sum(1 for count in duplicate_counts.values() if count > 1)
    repost_like_records = sum(count for count in duplicate_counts.values() if count > 1)

    return {
        "days": normalize_days(filters.days),
        "total_observed": total,
        "sample_limit": OVERVIEW_SAMPLE_LIMIT,
        "sample_limit_reached": total >= OVERVIEW_SAMPLE_LIMIT,
        "latest_posted_date": latest.isoformat() if latest else None,
        "coverage": {
            "source_url": count_ratio(source_url_count, total),
            "apply_url": count_ratio(apply_url_count, total),
            "salary": count_ratio(salary_count, total),
            "remote_friendly": count_ratio(remote_friendly_count, total),
            "direct_source": count_ratio(direct_source_count, total),
        },
        "quality": {
            "duplicate_groups": duplicate_groups,
            "repost_like_records": repost_like_records,
            "missing_source_url": total - source_url_count,
            "no_salary": total - salary_count,
            "needs_remote_evidence": missing_remote_evidence_count,
        },
        "top_sources": top_counts(source_counter, total),
        "top_companies": top_counts(company_counter, total),
        "freshness": dict(freshness_counter),
        "remote_quality": dict(remote_counter),
        "salary_status": dict(salary_counter),
        "target_fit": dict(target_fit_counter),
        "personal_fit": dict(personal_fit_counter),
        "role_tags": dict(tag_counter),
    }


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
        "source_link_url": source_link_url(job),
        "apply_link_url": apply_link_url(job),
        "freshness_bucket": quality.freshness_bucket,
        "source_trust": quality.source_trust,
        "remote_quality": quality.remote_quality,
        "role_tags": list(quality.role_tags),
        "salary_status": quality.salary_status,
        "duplicate_key": quality.duplicate_key,
        "repost_count": quality.repost_count,
        "target_bucket": quality.target_bucket,
        "target_score": quality.target_score,
        "priority_terms": list(quality.priority_terms),
        "downrank_terms": list(quality.downrank_terms),
        "personal_fit_bucket": quality.personal_fit_bucket,
        "personal_fit_score": quality.personal_fit_score,
        "mobility_tags": list(quality.mobility_tags),
        "people_facing_tags": list(quality.people_facing_tags),
        "domain_tags": list(quality.domain_tags),
        "risk_tags": list(quality.risk_tags),
        "fit_reasons": list(quality.fit_reasons),
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


def personal_fit_rank(bucket: str) -> int:
    return {
        "strong_match": 3,
        "good_match": 2,
        "maybe": 1,
        "downrank": 0,
    }.get(bucket, 0)


def latest_posted_date(jobs: Iterable[JobListing]) -> date | None:
    dates = [job.posted_at for job in jobs if job.posted_at is not None]
    return max(dates) if dates else None


def count_ratio(count: int, total: int) -> dict[str, object]:
    return {"count": count, "ratio": ratio(count, total)}


def top_counts(counter: Counter[str], total: int, limit: int = 6) -> list[dict[str, object]]:
    return [
        {"name": name, "count": count, "ratio": ratio(count, total)}
        for name, count in sorted(counter.items(), key=lambda item: (-item[1], item[0]))[:limit]
    ]


def ratio(count: int, total: int) -> float:
    if total <= 0:
        return 0
    return round(count / total, 4)
