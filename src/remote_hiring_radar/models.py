from __future__ import annotations

from dataclasses import dataclass, field
from datetime import date


@dataclass(frozen=True)
class JobListing:
    source: str
    source_url: str
    title: str
    company: str
    location: str
    description: str
    posted_at: date | None = None
    salary_text: str = ""
    tags: tuple[str, ...] = ()


@dataclass(frozen=True)
class ScoredJob:
    job: JobListing
    score: int
    reasons: tuple[str, ...] = field(default_factory=tuple)


@dataclass(frozen=True)
class RadarReport:
    title: str
    total_seen: int
    shortlisted: tuple[ScoredJob, ...]

