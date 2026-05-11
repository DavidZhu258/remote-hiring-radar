from __future__ import annotations

from datetime import date

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
