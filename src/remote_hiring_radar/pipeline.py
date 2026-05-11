from __future__ import annotations

from collections.abc import Iterable

from .models import JobListing, RadarReport, ScoredJob

REMOTE_TERMS = ("remote", "work from anywhere", "distributed", "anywhere")
FOCUS_TERMS = ("ai", "agent", "llm", "machine learning", "data", "rag", "automation")
SENIORITY_PENALTY_TERMS = ("principal", "staff", "vp ", "head of")


def identity_key(job: JobListing) -> tuple[str, str]:
    return (job.title.strip().lower(), job.company.strip().lower())


def dedupe_jobs(jobs: Iterable[JobListing]) -> list[JobListing]:
    seen: set[tuple[str, str]] = set()
    result: list[JobListing] = []
    for job in jobs:
        key = identity_key(job)
        if key in seen:
            continue
        seen.add(key)
        result.append(job)
    return result


def score_job(job: JobListing) -> ScoredJob:
    text = " ".join([job.title, job.location, job.description, " ".join(job.tags)]).lower()
    score = 0
    reasons: list[str] = []

    if any(term in text for term in REMOTE_TERMS):
        score += 35
        reasons.append("remote-friendly")
    if any(term in text for term in FOCUS_TERMS):
        score += 35
        reasons.append("matches AI/data/agent focus")
    if job.salary_text:
        score += 10
        reasons.append("has compensation signal")
    if job.source_url:
        score += 10
        reasons.append("source is reviewable")
    if any(term in text for term in SENIORITY_PENALTY_TERMS):
        score -= 15
        reasons.append("seniority may be too high")

    return ScoredJob(job=job, score=max(0, min(100, score)), reasons=tuple(reasons))


def build_report(jobs: Iterable[JobListing], threshold: int = 60, limit: int = 20) -> RadarReport:
    unique_jobs = dedupe_jobs(jobs)
    scored = sorted(
        (score_job(job) for job in unique_jobs), key=lambda item: item.score, reverse=True
    )
    shortlisted = tuple(item for item in scored if item.score >= threshold)[:limit]
    return RadarReport(
        title="Remote Hiring Radar",
        total_seen=len(unique_jobs),
        shortlisted=shortlisted,
    )
