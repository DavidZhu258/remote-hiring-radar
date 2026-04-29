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

    @classmethod
    def from_env(cls) -> "Settings":
        return cls(
            dry_run=env_bool("RADAR_DRY_RUN", True),
            max_items=int(os.getenv("RADAR_MAX_ITEMS", "50")),
            foorilla_base_url=os.getenv("FOORILLA_BASE_URL", cls.foorilla_base_url),
            llm_provider=os.getenv("LLM_PROVIDER", ""),
        )

