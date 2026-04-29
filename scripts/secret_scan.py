from __future__ import annotations

import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SKIP_DIRS = {".git", ".venv", "venv", "__pycache__", ".pytest_cache", "build", "dist"}
PATTERNS = {
    "github_token": re.compile(r"\b(?:ghp|github_pat)_[A-Za-z0-9_]{20,}\b"),
    "openrouter_key": re.compile(r"\bsk-or-v1-[A-Za-z0-9]{20,}\b"),
    "jina_key": re.compile(r"\bjina_[A-Za-z0-9_-]{20,}\b"),
    "private_key": re.compile(r"BEGIN (?:RSA |OPENSSH |EC )?PRIVATE KEY"),
}


def should_skip(path: Path) -> bool:
    return any(part in SKIP_DIRS for part in path.parts)


def main() -> int:
    findings: list[str] = []
    for path in ROOT.rglob("*"):
        if should_skip(path) or not path.is_file():
            continue
        try:
            text = path.read_text(encoding="utf-8")
        except UnicodeDecodeError:
            continue
        for name, pattern in PATTERNS.items():
            if pattern.search(text):
                findings.append(f"{name}: {path.relative_to(ROOT)}")
    if findings:
        print("Potential secrets found:")
        print("\n".join(findings))
        return 1
    print("Secret scan clean")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

