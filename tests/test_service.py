from __future__ import annotations

from datetime import date

from remote_hiring_radar.models import JobListing
from remote_hiring_radar.service import FACET_SAMPLE_LIMIT, JobFilters, get_facets, get_jobs


class RecordingRepository:
    def __init__(self) -> None:
        self.calls: list[dict[str, object]] = []

    def fetch_jobs(
        self,
        *,
        days: int,
        q: str = "",
        source: str = "",
        max_rows: int = 5000,
        ordered: bool = True,
    ) -> list[JobListing]:
        self.calls.append(
            {
                "days": days,
                "q": q,
                "source": source,
                "max_rows": max_rows,
                "ordered": ordered,
            }
        )
        return []

    def latest_posted_date(self) -> date | None:
        return None

    def check(self) -> None:
        return None


def test_get_jobs_uses_smaller_candidate_window_for_keyword_search() -> None:
    repository = RecordingRepository()

    get_jobs(
        repository,
        JobFilters(days=30, q="robotics", limit=25, offset=0),
        today=date(2026, 6, 1),
    )

    assert repository.calls[0]["max_rows"] == 500


def test_get_jobs_defaults_to_500_rows() -> None:
    repository = RecordingRepository()

    response = get_jobs(repository, JobFilters(days=30), today=date(2026, 6, 1))

    assert response["limit"] == 500
    assert repository.calls[0]["max_rows"] == 750


def test_get_facets_uses_light_unsorted_sample() -> None:
    repository = RecordingRepository()

    get_facets(repository, JobFilters(days=30), today=date(2026, 6, 1))

    assert repository.calls[0]["max_rows"] == FACET_SAMPLE_LIMIT
    assert repository.calls[0]["ordered"] is False
