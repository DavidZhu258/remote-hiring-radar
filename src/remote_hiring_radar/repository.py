from __future__ import annotations

from collections.abc import Iterable, Sequence
from dataclasses import dataclass, field
from datetime import date, datetime, timedelta
from typing import Any, Protocol

from .config import Settings
from .models import JobListing


class JobRepository(Protocol):
    def fetch_jobs(
        self,
        *,
        days: int,
        q: str = "",
        source: str = "",
        max_rows: int = 5000,
        ordered: bool = True,
    ) -> list[JobListing]: ...

    def latest_posted_date(self) -> date | None: ...

    def check(self) -> None: ...


@dataclass
class InMemoryJobRepository:
    jobs: list[JobListing]
    config: dict[str, object] = field(default_factory=dict)

    def fetch_jobs(
        self,
        *,
        days: int,
        q: str = "",
        source: str = "",
        max_rows: int = 5000,
        ordered: bool = True,
    ) -> list[JobListing]:
        latest = self.latest_posted_date() or date.today()
        cutoff = latest - timedelta(days=days)
        lowered_query = q.strip().lower()
        lowered_source = source.strip().lower()
        results: list[JobListing] = []
        for job in self.jobs:
            if job.posted_at is not None and job.posted_at < cutoff:
                continue
            if lowered_source and job.source.lower() != lowered_source:
                continue
            if lowered_query and lowered_query not in searchable_text(job).lower():
                continue
            results.append(job)
        return results[:max_rows]

    def latest_posted_date(self) -> date | None:
        dates = [job.posted_at for job in self.jobs if job.posted_at is not None]
        return max(dates) if dates else None

    def check(self) -> None:
        return None


@dataclass(frozen=True)
class ClickHouseJobRepository:
    settings: Settings

    @classmethod
    def from_env(cls) -> ClickHouseJobRepository:
        return cls(Settings.from_env())

    def fetch_jobs(
        self,
        *,
        days: int,
        q: str = "",
        source: str = "",
        max_rows: int = 5000,
        ordered: bool = True,
    ) -> list[JobListing]:
        client = self._client()
        prewhere_conditions = ["posted_date >= today() - INTERVAL %(days)s DAY"]
        where_conditions: list[str] = []
        params: dict[str, object] = {
            "days": safe_days(days),
            "max_rows": max(1, min(max_rows, 20000)),
        }
        source_filter = source.strip()
        if source_filter:
            prewhere_conditions.append("source_name = %(source)s")
            params["source"] = source_filter
        keyword = q.strip()
        if keyword:
            where_conditions.append(
                "("
                "positionCaseInsensitive(title, %(q)s) > 0 OR "
                "positionCaseInsensitive(company, %(q)s) > 0 OR "
                "positionCaseInsensitive(location, %(q)s) > 0 OR "
                "positionCaseInsensitive(description, %(q)s) > 0 OR "
                "positionCaseInsensitive(requirements, %(q)s) > 0 OR "
                "positionCaseInsensitive(skills, %(q)s) > 0"
                ")"
            )
            params["q"] = keyword

        where_sql = f"WHERE {' AND '.join(where_conditions)}" if where_conditions else ""
        order_sql = "ORDER BY posted_date DESC, job_id DESC" if ordered else ""
        query = f"""
            SELECT
                job_id,
                title,
                company,
                location,
                salary,
                salary_detail,
                description,
                requirements,
                responsibilities,
                benefits,
                skills,
                job_type,
                source_url,
                source_name,
                budget_min,
                budget_max,
                budget_currency,
                apply_url,
                posted_date
            FROM jobs
            PREWHERE {" AND ".join(prewhere_conditions)}
            {where_sql}
            {order_sql}
            LIMIT %(max_rows)s
        """
        rows = client.query(query, parameters=params).result_rows
        return [job_from_row(row) for row in rows]

    def latest_posted_date(self) -> date | None:
        client = self._client()
        rows = client.query("SELECT max(posted_date) FROM jobs").result_rows
        if not rows:
            return None
        return coerce_date(rows[0][0])

    def check(self) -> None:
        self._client().command("SELECT 1")

    def _client(self) -> Any:
        import clickhouse_connect

        return clickhouse_connect.get_client(
            host=self.settings.clickhouse_host,
            port=self.settings.clickhouse_port,
            username=self.settings.clickhouse_user,
            password=self.settings.clickhouse_password,
            database=self.settings.clickhouse_database,
        )


def job_from_row(row: Sequence[object]) -> JobListing:
    (
        job_id,
        title,
        company,
        location,
        salary,
        salary_detail,
        description,
        requirements,
        responsibilities,
        benefits,
        skills,
        job_type,
        source_url,
        source_name,
        budget_min,
        budget_max,
        budget_currency,
        apply_url,
        posted_date,
    ) = row
    return JobListing(
        source=str(source_name or ""),
        source_url=str(source_url or ""),
        title=str(title or ""),
        company=str(company or ""),
        location=str(location or ""),
        description=str(description or ""),
        posted_at=coerce_date(posted_date),
        salary_text=str(salary or ""),
        job_id=str(job_id or ""),
        requirements=str(requirements or ""),
        responsibilities=str(responsibilities or ""),
        benefits=str(benefits or ""),
        skills=str(skills or ""),
        job_type=str(job_type or ""),
        salary_detail=str(salary_detail or ""),
        budget_min=coerce_float(budget_min),
        budget_max=coerce_float(budget_max),
        budget_currency=str(budget_currency or ""),
        apply_url=str(apply_url or ""),
        raw={
            "job_id": job_id,
            "source_name": source_name,
            "posted_date": str(posted_date or ""),
        },
    )


def coerce_date(value: object) -> date | None:
    if value is None:
        return None
    if isinstance(value, datetime):
        return value.date()
    if isinstance(value, date):
        return value
    text = str(value).strip()
    if not text:
        return None
    try:
        return date.fromisoformat(text[:10])
    except ValueError:
        return None


def coerce_float(value: object) -> float | None:
    if value is None or value == "":
        return None
    try:
        return float(value)
    except (TypeError, ValueError):
        return None


def searchable_text(job: JobListing) -> str:
    return " ".join(
        [
            job.title,
            job.company,
            job.location,
            job.description,
            job.requirements,
            job.skills,
            " ".join(job.tags),
        ]
    )


def safe_days(days: int) -> int:
    return min(max(days, 1), 30)


def sort_jobs_newest_first(jobs: Iterable[JobListing]) -> list[JobListing]:
    return sorted(jobs, key=lambda job: job.posted_at or date.min, reverse=True)
