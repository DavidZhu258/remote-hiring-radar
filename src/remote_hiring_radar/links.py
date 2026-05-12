from __future__ import annotations

import os
from urllib.parse import parse_qsl, urlencode, urlparse, urlunparse

from .models import JobListing


def source_link_url(job: JobListing) -> str:
    return link_for_job(job, job.source_url)


def apply_link_url(job: JobListing) -> str:
    target = job.apply_url or job.source_url
    return link_for_job(job, target)


def link_for_job(job: JobListing, target_url: str) -> str:
    target = target_url.strip()
    if not target:
        return ""
    if not is_foorilla_job(job, target):
        return target

    template = os.getenv("FOORILLA_LINK_TEMPLATE", "").strip()
    if template:
        return template.replace("{url}", target)

    auth_url = os.getenv("FOORILLA_AUTH_URL", "").strip()
    if not auth_url:
        return target
    return append_next(auth_url, target)


def is_foorilla_job(job: JobListing, target_url: str) -> bool:
    host = urlparse(target_url).netloc.lower()
    source = job.source.lower()
    return "foorilla.com" in host or "foorilla" in source


def append_next(auth_url: str, target_url: str) -> str:
    parsed = urlparse(auth_url)
    query = [
        (key, value)
        for key, value in parse_qsl(parsed.query, keep_blank_values=True)
        if key != "next"
    ]
    query.append(("next", target_url))
    return urlunparse(parsed._replace(query=urlencode(query)))
