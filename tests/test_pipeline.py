from remote_hiring_radar.models import JobListing
from remote_hiring_radar.pipeline import build_report, dedupe_jobs, score_job


def test_remote_ai_job_scores_high() -> None:
    job = JobListing(
        source="foorilla",
        source_url="https://foorilla.com/hiring/example",
        title="Remote AI Agent Engineer",
        company="Example Labs",
        location="Remote",
        description="Build LLM agents and RAG automations.",
        salary_text="$100k+",
    )

    scored = score_job(job)

    assert scored.score >= 80
    assert "remote-friendly" in scored.reasons


def test_dedupe_uses_title_and_company() -> None:
    jobs = [
        JobListing("a", "https://a", "AI Engineer", "Example", "Remote", "agent work"),
        JobListing("b", "https://b", "ai engineer", "example", "Remote", "duplicate"),
    ]

    assert len(dedupe_jobs(jobs)) == 1


def test_report_shortlists_only_good_matches() -> None:
    report = build_report(
        [
            JobListing("a", "https://a", "Remote AI Engineer", "A", "Remote", "LLM work"),
            JobListing("b", "https://b", "Office Manager", "B", "Onsite", "facilities"),
        ],
        threshold=60,
    )

    assert report.total_seen == 2
    assert len(report.shortlisted) == 1

