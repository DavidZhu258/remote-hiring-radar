from __future__ import annotations

import os
from dataclasses import dataclass


def env_bool(name: str, default: bool = False) -> bool:
    value = os.getenv(name)
    if value is None:
        return default
    return value.strip().lower() in {"1", "true", "yes", "on"}


@dataclass(frozen=True)
class Settings:
    dry_run: bool = True
    max_items: int = 50
    foorilla_base_url: str = "https://foorilla.com/hiring/"
    llm_provider: str = ""
    clickhouse_host: str = "localhost"
    clickhouse_port: int = 8123
    clickhouse_user: str = "default"
    clickhouse_password: str = ""
    clickhouse_database: str = "analytics"
    radar_default_days: int = 7

    @classmethod
    def from_env(cls) -> Settings:
        return cls(
            dry_run=env_bool("RADAR_DRY_RUN", True),
            max_items=int(os.getenv("RADAR_MAX_ITEMS", "50")),
            foorilla_base_url=os.getenv("FOORILLA_BASE_URL", cls.foorilla_base_url),
            llm_provider=os.getenv("LLM_PROVIDER", ""),
            clickhouse_host=os.getenv("CLICKHOUSE_HOST", cls.clickhouse_host),
            clickhouse_port=int(os.getenv("CLICKHOUSE_PORT", str(cls.clickhouse_port))),
            clickhouse_user=os.getenv("CLICKHOUSE_USER", cls.clickhouse_user),
            clickhouse_password=os.getenv("CLICKHOUSE_PASSWORD", ""),
            clickhouse_database=os.getenv("CLICKHOUSE_DATABASE", cls.clickhouse_database),
            radar_default_days=int(os.getenv("RADAR_DEFAULT_DAYS", str(cls.radar_default_days))),
        )
