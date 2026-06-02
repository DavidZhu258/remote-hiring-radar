from __future__ import annotations

import re
from dataclasses import dataclass
from datetime import date
from functools import lru_cache
from urllib.parse import urlparse

from .models import JobListing

PersonalFitResult = tuple[
    str,
    int,
    tuple[str, ...],
    tuple[str, ...],
    tuple[str, ...],
    tuple[str, ...],
    tuple[str, ...],
]

TAG_ORDER = ("vision", "ai", "data", "agent", "security", "infra")
TARGET_TITLE_PRIORITIES = (
    "AI Solutions Engineer",
    "Computer Vision Solutions Engineer",
    "Vision Engineer",
    "Computer Vision Engineer",
    "Machine Vision Engineer",
    "AI Consultant",
    "AI Implementation Engineer",
    "Computer Vision Field Application Engineer",
    "Machine Vision Field Application Engineer",
    "Robotics Vision Engineer",
    "Robotics Application Engineer",
    "Robotics Software Engineer",
    "Industrial AI Engineer",
    "Edge AI Engineer",
    "AI Automation Engineer",
    "MLOps Solutions Engineer",
    "AI Platform Engineer",
    "Software Integration Engineer",
    "Implementation Engineer",
    "Implementation Consultant",
    "Professional Services Engineer",
    "Technical Consultant - AI",
    "Technical Consultant - Computer Vision",
    "Solutions Engineer",
    "Pre-Sales AI Engineer",
    "Field Service Engineer - Machine Vision",
    "Data Consultant",
    "Cloud Consultant",
    "Data Platform Engineer",
    "Technical Account Manager - AI Platform",
)
TARGET_UP_TERMS = (
    "Solutions",
    "Implementation",
    "Field",
    "Application",
    "Consultant",
    "Professional Services",
    "Customer",
    "Deployment",
    "Integration",
    "Onsite",
    "Travel",
    "Pre-sales",
    "Post-sales",
    "Industrial",
    "Robotics",
    "Vision",
    "Automation",
    "Edge AI",
)
TARGET_DOWN_TERMS = (
    "Backend",
    "Frontend",
    "Full Stack",
    "Java",
    ".NET",
    "QA",
    "Tester",
    "IT Support",
    "Security",
    "Marketing",
    "Recruiter",
    "Associate",
    "Analyst",
    "Admin",
)
TARGET_TITLE_SCORE = 8
TARGET_UP_TERM_SCORE = 3
TARGET_DOWN_TERM_SCORE = -4
DOMAIN_TAG_TERMS: dict[str, tuple[str, ...]] = {
    "vision": (
        "computer vision",
        "image recognition",
        "visual recognition",
        "vision engineer",
        "vision systems",
        "vision system",
        "vision model",
        "vision ai",
        "visual ai",
        "ocr",
        "opencv",
        "yolo",
        "sam",
    ),
    "machine_vision": ("machine vision", "industrial vision", "visual inspection"),
    "robotics": ("robotics", "robotic", "perception"),
    "edge_ai": ("edge ai", "edge ml", "on-device ai", "embedded ai"),
    "ai_platform": ("ai platform", "ml platform", "model platform", "enterprise ai"),
    "mlops": ("mlops", "model deployment", "model monitoring", "model ops"),
    "data_platform": ("data platform", "data warehouse", "lakehouse", "etl", "dbt"),
    "cloud": ("cloud", "aws", "azure", "gcp"),
    "ai": ("ai", "artificial intelligence", "machine learning", "llm", "genai"),
    "data": ("data", "analytics", "sql", "spark"),
}
PEOPLE_FACING_TERMS: dict[str, tuple[str, ...]] = {
    "solutions": ("solutions", "solution engineer", "solution consultant"),
    "implementation": ("implementation", "implement", "post implementation"),
    "field_application": ("field application", "field applications", "application engineer"),
    "consulting": ("consultant", "consulting", "technical consultant"),
    "professional_services": ("professional services", "services engineer"),
    "customer": ("customer", "customer facing", "client facing", "customer success"),
    "deployment": ("deployment", "deploy", "rollout", "go live"),
    "integration": ("integration", "integrate", "systems integration"),
    "training": ("training", "train", "instructor", "workshop"),
    "enablement": ("enablement", "enable", "workshop"),
    "pre_sales": ("pre sales", "presales", "pre-sales", "sales engineer"),
    "post_sales": ("post sales", "post-sales", "after sales"),
    "technical_account": ("technical account", "technical account manager", "tam"),
}
MOBILITY_TERMS: dict[str, tuple[str, ...]] = {
    "global": ("global", "worldwide", "international"),
    "travel": ("travel", "travelling", "traveling"),
    "customer_site": ("customer site", "client site", "customer sites", "client sites"),
    "onsite": ("onsite", "on site", "on-site"),
    "field": ("field",),
    "overseas": ("overseas", "abroad", "outside china"),
}
RISK_TAG_TERMS: dict[str, tuple[str, ...]] = {
    "pure_backend": ("backend", "back end"),
    "pure_frontend": ("frontend", "front end"),
    "full_stack": ("full stack", "fullstack"),
    "qa_tester": ("qa", "tester", "test automation", "quality assurance"),
    "it_support": ("it support", "help desk", "desktop support"),
    "marketing": ("marketing", "campaign", "growth marketer"),
    "recruiter": ("recruiter", "talent acquisition", "sourcer"),
    "admin": ("admin", "administrator", "office assistant"),
}
DOMAIN_TAG_SCORES = {
    "vision": 12,
    "machine_vision": 12,
    "robotics": 10,
    "edge_ai": 10,
    "ai_platform": 9,
    "mlops": 9,
    "data_platform": 9,
    "cloud": 6,
    "ai": 6,
    "data": 5,
}
PEOPLE_TAG_SCORES = {
    "field_application": 12,
    "solutions": 10,
    "implementation": 10,
    "consulting": 9,
    "professional_services": 9,
    "customer": 8,
    "pre_sales": 8,
    "post_sales": 8,
    "deployment": 7,
    "integration": 7,
    "training": 7,
    "enablement": 7,
    "technical_account": 7,
}
MOBILITY_TAG_SCORE = 8
RISK_TAG_SCORES = {
    "pure_backend": -12,
    "pure_frontend": -12,
    "full_stack": -10,
    "qa_tester": -12,
    "it_support": -12,
    "marketing": -14,
    "recruiter": -14,
    "admin": -14,
    "analyst_only": -8,
    "associate": -6,
    "security_only": -8,
    "malware_research": -30,
    "missing_source": -6,
    "missing_apply": -3,
    "no_salary": -1,
    "remote_evidence_missing": -2,
    "hybrid_suspect": -3,
}

TAG_TERMS: dict[str, tuple[str, ...]] = {
    "vision": (
        "image recognition",
        "computer vision",
        "visual recognition",
        "ocr",
        "video",
        "multimodal",
        "robotics perception",
        "opencv",
        "yolo",
        "sam",
        "segment anything",
        "vision engineer",
        "vision systems",
        "vision system",
        "vision model",
        "vision ai",
        "visual ai",
    ),
    "ai": (
        "ai",
        "artificial intelligence",
        "machine learning",
        "ml",
        "llm",
        "genai",
        "generative ai",
        "rag",
        "model training",
        "deep learning",
    ),
    "data": (
        "data",
        "analytics",
        "etl",
        "elt",
        "warehouse",
        "lakehouse",
        "bi",
        "sql",
        "spark",
        "dbt",
    ),
    "agent": (
        "agent",
        "agents",
        "agentic",
        "autonomous workflow",
        "tool calling",
        "multi-agent",
        "multi agent",
    ),
    "security": (
        "security",
        "cybersecurity",
        "infosec",
        "appsec",
        "soc",
        "threat",
        "vulnerability",
    ),
    "infra": (
        "infra",
        "infrastructure",
        "platform",
        "devops",
        "sre",
        "kubernetes",
        "k8s",
        "terraform",
        "cloud",
    ),
}

DIRECT_SOURCE_TERMS = (
    "foorilla",
    "greenhouse",
    "lever",
    "ashby",
    "workday",
    "smartrecruiters",
    "recruitee",
    "bamboohr",
    "wellfound",
    "jobs.ashbyhq",
)
AGGREGATOR_TERMS = (
    "linkedin",
    "indeed",
    "glassdoor",
    "jobsdb",
    "jobstreet",
    "ziprecruiter",
    "hiring.cafe",
    "hiringcafe",
)
WORLDWIDE_REMOTE_TERMS = (
    "worldwide",
    "anywhere",
    "work from anywhere",
    "global remote",
    "fully distributed",
    "distributed team",
)
LIMITED_REMOTE_TERMS = (
    "remote (us",
    "remote us",
    "united states",
    "usa",
    "u.s.",
    "canada",
    "uk",
    "united kingdom",
    "europe",
    "emea",
    "apac",
    "latin america",
    "latam",
    "timezone",
    "time zone",
)
HYBRID_TERMS = (
    "hybrid",
    "onsite",
    "on-site",
    "in office",
    "in-office",
    "office based",
    "days in office",
)


@dataclass(frozen=True)
class JobQuality:
    freshness_bucket: str
    source_trust: str
    remote_quality: str
    role_tags: tuple[str, ...]
    salary_status: str
    duplicate_key: str
    repost_count: int
    target_bucket: str
    target_score: int
    priority_terms: tuple[str, ...]
    downrank_terms: tuple[str, ...]
    personal_fit_bucket: str
    personal_fit_score: int
    mobility_tags: tuple[str, ...]
    people_facing_tags: tuple[str, ...]
    domain_tags: tuple[str, ...]
    risk_tags: tuple[str, ...]
    fit_reasons: tuple[str, ...]
    quality_reasons: tuple[str, ...]
    exclude_reasons: tuple[str, ...]


def normalize_text(value: object) -> str:
    text = str(value or "").lower()
    text = re.sub(r"[^a-z0-9]+", " ", text)
    return re.sub(r"\s+", " ", text).strip()


def normalize_duplicate_key(job: JobListing) -> str:
    return "|".join(
        [
            normalize_text(job.title),
            normalize_text(job.company),
            normalize_text(job.location),
        ]
    )


def evaluate_job_quality(
    job: JobListing,
    *,
    today: date | None = None,
    repost_count: int = 1,
) -> JobQuality:
    today = today or date.today()
    role_tags = detect_role_tags(job)
    freshness_bucket = detect_freshness_bucket(job, today)
    source_trust = detect_source_trust(job)
    remote_quality = detect_remote_quality(job)
    salary_status = detect_salary_status(job)
    duplicate_key = normalize_duplicate_key(job)
    target_bucket, target_score, priority_terms, downrank_terms = detect_target_fit(job)
    (
        personal_fit_bucket,
        personal_fit_score,
        mobility_tags,
        people_facing_tags,
        domain_tags,
        risk_tags,
        fit_reasons,
    ) = detect_personal_fit(
        job,
        role_tags=role_tags,
        source_trust=source_trust,
        freshness_bucket=freshness_bucket,
        remote_quality=remote_quality,
        salary_status=salary_status,
        downrank_terms=downrank_terms,
    )

    quality_reasons = build_quality_reasons(
        role_tags=role_tags,
        freshness_bucket=freshness_bucket,
        source_trust=source_trust,
        remote_quality=remote_quality,
        salary_status=salary_status,
        repost_count=repost_count,
        target_bucket=target_bucket,
        priority_terms=priority_terms,
    )
    exclude_reasons = build_exclude_reasons(
        job=job,
        freshness_bucket=freshness_bucket,
        remote_quality=remote_quality,
        salary_status=salary_status,
        downrank_terms=downrank_terms,
    )

    return JobQuality(
        freshness_bucket=freshness_bucket,
        source_trust=source_trust,
        remote_quality=remote_quality,
        role_tags=role_tags,
        salary_status=salary_status,
        duplicate_key=duplicate_key,
        repost_count=repost_count,
        target_bucket=target_bucket,
        target_score=target_score,
        priority_terms=priority_terms,
        downrank_terms=downrank_terms,
        personal_fit_bucket=personal_fit_bucket,
        personal_fit_score=personal_fit_score,
        mobility_tags=mobility_tags,
        people_facing_tags=people_facing_tags,
        domain_tags=domain_tags,
        risk_tags=risk_tags,
        fit_reasons=fit_reasons,
        quality_reasons=quality_reasons,
        exclude_reasons=exclude_reasons,
    )


def detect_role_tags(job: JobListing) -> tuple[str, ...]:
    text = normalized_job_blob(job)
    detected: list[str] = []
    for tag in TAG_ORDER:
        if any(term_matches(text, term) for term in TAG_TERMS[tag]):
            detected.append(tag)
    return tuple(detected)


def detect_freshness_bucket(job: JobListing, today: date) -> str:
    if job.posted_at is None:
        return "unknown"
    age_days = max((today - job.posted_at).days, 0)
    if age_days <= 1:
        return "0-24h"
    if age_days <= 3:
        return "1-3d"
    if age_days <= 7:
        return "4-7d"
    if age_days <= 30:
        return "8-30d"
    return "stale"


def detect_source_trust(job: JobListing) -> str:
    source = " ".join([job.source, job.source_url, parsed_hostname(job.source_url)]).lower()
    if any(term in source for term in DIRECT_SOURCE_TERMS):
        return "direct_source"
    if any(term in source for term in AGGREGATOR_TERMS):
        return "aggregator"
    return "unknown"


def detect_remote_quality(job: JobListing) -> str:
    raw_text = raw_job_blob(job)
    normalized = normalize_text(raw_text)
    if any(term in raw_text.lower() or term_matches(normalized, term) for term in HYBRID_TERMS):
        return "hybrid-suspect"
    if not term_matches(normalized, "remote"):
        return "unknown"
    if any(
        term in raw_text.lower() or term_matches(normalized, term) for term in LIMITED_REMOTE_TERMS
    ):
        return "country-limited"
    if normalize_text(job.location) == "remote":
        return "worldwide"
    if any(
        term in raw_text.lower() or term_matches(normalized, term)
        for term in WORLDWIDE_REMOTE_TERMS
    ):
        return "worldwide"
    return "unknown"


def detect_salary_status(job: JobListing) -> str:
    if job.salary_text.strip() or job.salary_detail.strip():
        return "has_salary"
    if positive_number(job.budget_min) or positive_number(job.budget_max):
        return "has_salary"
    return "no_salary"


def detect_target_fit(job: JobListing) -> tuple[str, int, tuple[str, ...], tuple[str, ...]]:
    title = normalize_text(job.title)
    priority_terms: list[str] = []
    downrank_terms: list[str] = []
    score = 0

    for title_priority in TARGET_TITLE_PRIORITIES:
        if term_matches(title, title_priority):
            priority_terms.append(title_priority)
            score += TARGET_TITLE_SCORE
    for term in TARGET_UP_TERMS:
        if term_matches(title, term):
            priority_terms.append(term)
            score += TARGET_UP_TERM_SCORE
    for term in TARGET_DOWN_TERMS:
        if term_matches(title, term):
            downrank_terms.append(term)
            score += TARGET_DOWN_TERM_SCORE

    bucket = "standard"
    if score >= TARGET_TITLE_SCORE or priority_terms and score >= TARGET_UP_TERM_SCORE * 2:
        bucket = "priority"
    elif downrank_terms and score < TARGET_UP_TERM_SCORE:
        bucket = "downranked"

    return bucket, score, tuple(dict.fromkeys(priority_terms)), tuple(dict.fromkeys(downrank_terms))


def detect_personal_fit(
    job: JobListing,
    *,
    role_tags: tuple[str, ...],
    source_trust: str,
    freshness_bucket: str,
    remote_quality: str,
    salary_status: str,
    downrank_terms: tuple[str, ...],
) -> PersonalFitResult:
    text = normalized_job_blob(job)
    title = normalize_text(job.title)
    domain_tags = detect_named_tags(text, DOMAIN_TAG_TERMS)
    people_tags = detect_named_tags(text, PEOPLE_FACING_TERMS)
    title_people_tags = detect_named_tags(title, PEOPLE_FACING_TERMS)
    mobility_tags = detect_named_tags(text, MOBILITY_TERMS)
    risk_tags = list(detect_named_tags(title, RISK_TAG_TERMS))

    if "security" in role_tags and not set(domain_tags) & {"vision", "robotics", "edge_ai"}:
        risk_tags.append("security_only")
    if any(term_matches(title, term) for term in ("malware", "threat", "vulnerability")):
        risk_tags.append("malware_research")
    if term_matches(title, "analyst") and not people_tags:
        risk_tags.append("analyst_only")
    if term_matches(title, "associate") and not people_tags:
        risk_tags.append("associate")
    if not job.source_url.strip():
        risk_tags.append("missing_source")
    if not job.apply_url.strip():
        risk_tags.append("missing_apply")
    if salary_status == "no_salary":
        risk_tags.append("no_salary")
    if remote_quality == "unknown" and "remote" not in text and not mobility_tags:
        risk_tags.append("remote_evidence_missing")
    if remote_quality == "hybrid-suspect" and not mobility_tags:
        risk_tags.append("hybrid_suspect")
    for term in downrank_terms:
        normalized = normalize_text(term)
        if normalized in {"frontend", "front end"}:
            risk_tags.append("pure_frontend")
        elif normalized in {"backend", "back end"}:
            risk_tags.append("pure_backend")
        elif normalized == "full stack":
            risk_tags.append("full_stack")
        elif normalized in {"qa", "tester"}:
            risk_tags.append("qa_tester")
        elif normalized == "marketing":
            risk_tags.append("marketing")
        elif normalized == "recruiter":
            risk_tags.append("recruiter")
        elif normalized == "admin":
            risk_tags.append("admin")
        elif normalized == "analyst" and not people_tags:
            risk_tags.append("analyst_only")
        elif normalized == "associate" and not people_tags:
            risk_tags.append("associate")

    deduped_risk_tags = tuple(dict.fromkeys(risk_tags))
    score = sum(DOMAIN_TAG_SCORES[tag] for tag in domain_tags)
    score += sum(PEOPLE_TAG_SCORES[tag] for tag in people_tags)
    score += len(mobility_tags) * MOBILITY_TAG_SCORE
    score += sum(RISK_TAG_SCORES[tag] for tag in deduped_risk_tags)
    if source_trust == "direct_source":
        score += 2
    if job.apply_url.strip():
        score += 2
    if salary_status == "has_salary":
        score += 2
    if freshness_bucket in {"0-24h", "1-3d", "4-7d"}:
        score += 2
    if remote_quality in {"worldwide", "country-limited"}:
        score += 1

    bucket = personal_fit_bucket(
        score,
        domain_tags,
        people_tags,
        mobility_tags,
        deduped_risk_tags,
        title_people_tags=title_people_tags,
    )
    return (
        bucket,
        score,
        mobility_tags,
        people_tags,
        domain_tags,
        deduped_risk_tags,
        personal_fit_reasons(bucket, domain_tags, people_tags, mobility_tags, deduped_risk_tags),
    )


def detect_named_tags(text: str, taxonomy: dict[str, tuple[str, ...]]) -> tuple[str, ...]:
    return tuple(
        name for name, terms in taxonomy.items() if any(term_matches(text, term) for term in terms)
    )


def personal_fit_bucket(
    score: int,
    domain_tags: tuple[str, ...],
    people_tags: tuple[str, ...],
    mobility_tags: tuple[str, ...],
    risk_tags: tuple[str, ...],
    *,
    title_people_tags: tuple[str, ...] = (),
) -> str:
    severe_risks = {
        "pure_backend",
        "pure_frontend",
        "qa_tester",
        "marketing",
        "recruiter",
        "admin",
        "malware_research",
    }
    if severe_risks & set(risk_tags) and not (domain_tags and people_tags):
        return "downrank"
    if "malware_research" in risk_tags:
        return "downrank"
    target_domains = {"vision", "machine_vision", "robotics", "edge_ai"}
    core_transition_domains = target_domains | {"ai_platform", "mlops", "data_platform", "ai"}
    if "security_only" in risk_tags and not target_domains & set(domain_tags):
        return "downrank"
    if (
        score >= 45
        and domain_tags
        and people_tags
        and (mobility_tags or "field_application" in people_tags)
        and (core_transition_domains & set(domain_tags) or title_people_tags)
    ):
        return "strong_match"
    if score >= 18 and domain_tags:
        return "good_match"
    if score >= 12 and {"vision", "machine_vision", "robotics", "edge_ai"} & set(domain_tags):
        return "good_match"
    if score >= 0:
        return "maybe"
    return "downrank"


def personal_fit_reasons(
    bucket: str,
    domain_tags: tuple[str, ...],
    people_tags: tuple[str, ...],
    mobility_tags: tuple[str, ...],
    risk_tags: tuple[str, ...],
) -> tuple[str, ...]:
    reasons: list[str] = []
    if domain_tags and people_tags:
        reasons.append("technical transition fit")
    if people_tags:
        reasons.append("customer-facing delivery role")
    if mobility_tags:
        reasons.append("global travel or field signal")
    if {"vision", "machine_vision", "robotics", "edge_ai"} & set(domain_tags):
        reasons.append("AI/CV/robotics domain fit")
    if risk_tags:
        reasons.append("role appears outside the target transition path")
    if bucket == "downrank" and not reasons:
        reasons.append("role appears outside the target transition path")
    return tuple(dict.fromkeys(reasons))


def positive_number(value: float | None) -> bool:
    return value is not None and value > 0


def build_quality_reasons(
    *,
    role_tags: tuple[str, ...],
    freshness_bucket: str,
    source_trust: str,
    remote_quality: str,
    salary_status: str,
    repost_count: int,
    target_bucket: str,
    priority_terms: tuple[str, ...],
) -> tuple[str, ...]:
    reasons: list[str] = []
    if target_bucket == "priority":
        reasons.append("target role fit")
    if "vision" in role_tags:
        reasons.append("broad vision match")
    for tag in role_tags:
        if tag != "vision":
            reasons.append(f"{tag} role signal")
    if freshness_bucket in {"0-24h", "1-3d", "4-7d"}:
        reasons.append("fresh posting")
    if source_trust == "direct_source":
        reasons.append("direct source signal")
    if remote_quality in {"worldwide", "country-limited"}:
        reasons.append("remote-friendly")
    if salary_status == "has_salary":
        reasons.append("has compensation signal")
    if repost_count > 1:
        reasons.append(f"{repost_count} repost-like records")
    if priority_terms:
        reasons.append(f"priority terms: {', '.join(priority_terms[:3])}")
    return tuple(reasons)


def build_exclude_reasons(
    *,
    job: JobListing,
    freshness_bucket: str,
    remote_quality: str,
    salary_status: str,
    downrank_terms: tuple[str, ...],
) -> tuple[str, ...]:
    reasons: list[str] = []
    if downrank_terms:
        reasons.append(f"downrank title terms: {', '.join(downrank_terms)}")
    if remote_quality == "hybrid-suspect":
        reasons.append("hybrid or onsite language")
    if remote_quality == "unknown" and "remote" not in normalize_text(raw_job_blob(job)):
        reasons.append("remote evidence missing")
    if salary_status == "no_salary":
        reasons.append("no salary signal")
    if freshness_bucket == "stale":
        reasons.append("stale posting")
    if not job.source_url:
        reasons.append("source URL missing")
    return tuple(reasons)


def normalized_job_blob(job: JobListing) -> str:
    return normalize_text(raw_job_blob(job))


def raw_job_blob(job: JobListing) -> str:
    return " ".join(
        [
            job.title,
            job.company,
            job.location,
            job.description,
            job.requirements,
            job.responsibilities,
            job.benefits,
            job.skills,
            job.job_type,
            " ".join(job.tags),
        ]
    )


def parsed_hostname(url: str) -> str:
    try:
        return urlparse(url).netloc
    except ValueError:
        return ""


def term_matches(text: str, term: str) -> bool:
    normalized_term = normalized_search_term(term)
    if not normalized_term:
        return False
    if text == normalized_term:
        return True
    if text.startswith(f"{normalized_term} ") or text.endswith(f" {normalized_term}"):
        return True
    return f" {normalized_term} " in text


@lru_cache(maxsize=4096)
def normalized_search_term(term: str) -> str:
    return normalize_text(term)
