from __future__ import annotations

from collections.abc import Callable
from datetime import date

from fastapi import FastAPI, HTTPException, Query
from fastapi.middleware.cors import CORSMiddleware

from .repository import ClickHouseJobRepository, JobRepository
from .service import JobFilters, get_facets, get_health, get_jobs


def create_app(
    *,
    repository: JobRepository | None = None,
    today: Callable[[], date] = date.today,
) -> FastAPI:
    repo = repository or ClickHouseJobRepository.from_env()
    app = FastAPI(title="Remote Hiring Radar API", version="0.1.0")
    app.add_middleware(
        CORSMiddleware,
        allow_origins=[
            "http://localhost:3000",
            "http://localhost:3010",
            "http://127.0.0.1:3000",
            "http://127.0.0.1:3010",
            "https://davidzhu258.github.io",
        ],
        allow_credentials=False,
        allow_methods=["GET"],
        allow_headers=["*"],
    )

    @app.get("/api/health")
    def health() -> dict[str, object]:
        try:
            return get_health(repo, today=today())
        except Exception as exc:  # noqa: BLE001
            raise HTTPException(status_code=503, detail="ClickHouse unavailable") from exc

    @app.get("/api/jobs")
    def jobs(
        days: int = Query(7, ge=1, le=30),
        tags: str = "",
        remote_quality: str = "",
        salary_status: str = "",
        source: str = "",
        q: str = "",
        hide_reposts: bool = False,
        limit: int = Query(50, ge=1, le=100),
        offset: int = Query(0, ge=0),
        sort: str = "fresh",
    ) -> dict[str, object]:
        filters = JobFilters(
            days=days,
            tags=parse_csv(tags),
            remote_quality=remote_quality,
            salary_status=salary_status,
            source=source,
            q=q,
            hide_reposts=hide_reposts,
            limit=limit,
            offset=offset,
            sort=sort,
        )
        try:
            return get_jobs(repo, filters, today=today())
        except Exception as exc:  # noqa: BLE001
            raise HTTPException(status_code=503, detail="Job query unavailable") from exc

    @app.get("/api/facets")
    def facets(days: int = Query(7, ge=1, le=30), q: str = "") -> dict[str, object]:
        try:
            return get_facets(repo, JobFilters(days=days, q=q), today=today())
        except Exception as exc:  # noqa: BLE001
            raise HTTPException(status_code=503, detail="Facet query unavailable") from exc

    return app


def parse_csv(value: str) -> tuple[str, ...]:
    return tuple(part.strip() for part in value.split(",") if part.strip())


app = create_app()
