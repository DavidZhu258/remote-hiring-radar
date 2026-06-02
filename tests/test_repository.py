from __future__ import annotations

from datetime import date
from typing import Any

from remote_hiring_radar.config import Settings
from remote_hiring_radar.repository import ClickHouseJobRepository


def test_clickhouse_latest_posted_date_reads_first_result_row() -> None:
    class FakeResult:
        result_rows = [(date(2026, 5, 8),)]

    class FakeClient:
        def query(self, query: str) -> FakeResult:
            assert "max(posted_date)" in query
            return FakeResult()

    class FakeRepository(ClickHouseJobRepository):
        def _client(self) -> FakeClient:
            return FakeClient()

    repository = FakeRepository(Settings())

    assert repository.latest_posted_date() == date(2026, 5, 8)


def test_clickhouse_fetch_jobs_prewhere_limits_keyword_search() -> None:
    class FakeResult:
        result_rows: list[tuple[object, ...]] = []

    class FakeClient:
        query_text = ""
        parameters: dict[str, object] = {}

        def query(self, query: str, parameters: dict[str, object] | None = None) -> FakeResult:
            self.query_text = query
            self.parameters = parameters or {}
            return FakeResult()

    fake_client = FakeClient()

    class FakeRepository(ClickHouseJobRepository):
        def _client(self) -> Any:
            return fake_client

    repository = FakeRepository(Settings())

    repository.fetch_jobs(days=30, q="robotics", source="foorilla.com", max_rows=1000)

    assert "PREWHERE posted_date >= today() - INTERVAL %(days)s DAY" in fake_client.query_text
    assert "source_name = %(source)s" in fake_client.query_text
    assert "WHERE (positionCaseInsensitive(title, %(q)s) > 0 OR" in fake_client.query_text
    assert "ORDER BY posted_date DESC, job_id DESC" in fake_client.query_text
    assert "created_at DESC" not in fake_client.query_text
    assert fake_client.parameters["days"] == 30
    assert fake_client.parameters["source"] == "foorilla.com"
    assert fake_client.parameters["q"] == "robotics"


def test_clickhouse_fetch_jobs_can_skip_sorting_for_facets() -> None:
    class FakeResult:
        result_rows: list[tuple[object, ...]] = []

    class FakeClient:
        query_text = ""

        def query(self, query: str, parameters: dict[str, object] | None = None) -> FakeResult:
            self.query_text = query
            return FakeResult()

    fake_client = FakeClient()

    class FakeRepository(ClickHouseJobRepository):
        def _client(self) -> Any:
            return fake_client

    repository = FakeRepository(Settings())

    repository.fetch_jobs(days=7, max_rows=10000, ordered=False)

    assert "PREWHERE posted_date >= today() - INTERVAL %(days)s DAY" in fake_client.query_text
    assert "ORDER BY" not in fake_client.query_text
