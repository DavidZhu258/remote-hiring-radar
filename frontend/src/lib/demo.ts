import type { FacetsResponse, HealthResponse, JobItem, JobsResponse } from "./api";

const DEMO_JOBS: JobItem[] = [
  {
    job_id: "demo-vision-1",
    title: "Remote Computer Vision Engineer",
    company: "Northstar Robotics",
    location: "Remote (US / Canada)",
    description:
      "Build OCR, image recognition, and multimodal inspection pipelines for robotics perception workflows.",
    requirements:
      "Production Python, OpenCV, YOLO, SAM, data labeling loops, and comfort owning model quality diagnostics.",
    responsibilities: "Ship reliable perception features with reviewable source evidence.",
    benefits: "Remote-first team, async engineering culture.",
    posted_at: "2026-05-12",
    salary: "$150k-$190k",
    salary_detail: "$150k-$190k base",
    budget_min: 150000,
    budget_max: 190000,
    budget_currency: "USD",
    source: "foorilla.com",
    source_url: "https://foorilla.com/hiring/jobs/demo-vision-engineer/",
    apply_url: "https://foorilla.com/hiring/jobs/demo-vision-engineer/",
    freshness_bucket: "0-24h",
    source_trust: "direct_source",
    remote_quality: "country-limited",
    role_tags: ["vision", "ai"],
    salary_status: "has_salary",
    duplicate_key: "remote computer vision engineer|northstar robotics|remote us canada",
    repost_count: 1,
    quality_reasons: [
      "broad vision match",
      "ai role signal",
      "fresh posting",
      "direct source signal",
      "has compensation signal",
    ],
    exclude_reasons: [],
    raw: {
      preview: "GitHub Pages demo fallback",
      source_name: "foorilla.com",
      posted_date: "2026-05-12",
    },
    skills: "OpenCV, YOLO, SAM, OCR, Python",
  },
  {
    job_id: "demo-agent-1",
    title: "Founding AI Agent Engineer",
    company: "Workflow Foundry",
    location: "Remote",
    description:
      "Design agentic workflows with tool calling, evals, RAG, and human-in-the-loop review surfaces.",
    requirements: "LLM apps, TypeScript, Python, distributed systems, and pragmatic product sense.",
    responsibilities: "Own agent reliability, diagnostics, and fast customer-facing iteration.",
    benefits: "",
    posted_at: "2026-05-11",
    salary: "$140k-$210k",
    salary_detail: "$140k-$210k plus equity",
    budget_min: 140000,
    budget_max: 210000,
    budget_currency: "USD",
    source: "greenhouse",
    source_url: "https://boards.greenhouse.io/demo/jobs/agent",
    apply_url: "https://boards.greenhouse.io/demo/jobs/agent",
    freshness_bucket: "1-3d",
    source_trust: "direct_source",
    remote_quality: "worldwide",
    role_tags: ["ai", "agent", "infra"],
    salary_status: "has_salary",
    duplicate_key: "founding ai agent engineer|workflow foundry|remote",
    repost_count: 2,
    quality_reasons: [
      "ai role signal",
      "agent role signal",
      "infra role signal",
      "fresh posting",
      "direct source signal",
    ],
    exclude_reasons: [],
    raw: {
      preview: "GitHub Pages demo fallback",
      source_name: "greenhouse",
      posted_date: "2026-05-11",
    },
    skills: "LLM, agents, RAG, evals, TypeScript",
  },
  {
    job_id: "demo-data-1",
    title: "Remote Data Platform Engineer",
    company: "SignalLake",
    location: "Remote (Europe)",
    description:
      "Build data warehouse pipelines, analytics models, and quality checks for AI product telemetry.",
    requirements: "SQL, dbt, Spark, ClickHouse, Python, and strong debugging habits.",
    responsibilities: "Improve freshness, lineage, and dashboard reliability.",
    benefits: "",
    posted_at: "2026-05-09",
    salary: "",
    salary_detail: "",
    budget_min: null,
    budget_max: null,
    budget_currency: "",
    source: "jobsdb",
    source_url: "https://jobsdb.com/demo/data-platform",
    apply_url: "",
    freshness_bucket: "1-3d",
    source_trust: "aggregator",
    remote_quality: "country-limited",
    role_tags: ["data", "infra", "ai"],
    salary_status: "no_salary",
    duplicate_key: "remote data platform engineer|signallake|remote europe",
    repost_count: 1,
    quality_reasons: ["data role signal", "infra role signal", "fresh posting"],
    exclude_reasons: ["no salary signal"],
    raw: {
      preview: "GitHub Pages demo fallback",
      source_name: "jobsdb",
      posted_date: "2026-05-09",
    },
    skills: "SQL, dbt, Spark, ClickHouse",
  },
  {
    job_id: "demo-security-1",
    title: "Hybrid AI Security Analyst",
    company: "SecureModel Labs",
    location: "San Francisco, CA",
    description:
      "Hybrid role focused on model threat monitoring, vulnerability triage, and security analytics.",
    requirements: "Security operations, Python, model risk review, and analytics.",
    responsibilities: "Investigate threats and document remediation evidence.",
    benefits: "",
    posted_at: "2026-05-06",
    salary: "",
    salary_detail: "",
    budget_min: null,
    budget_max: null,
    budget_currency: "",
    source: "linkedin",
    source_url: "https://linkedin.com/jobs/view/demo-security",
    apply_url: "",
    freshness_bucket: "4-7d",
    source_trust: "aggregator",
    remote_quality: "hybrid-suspect",
    role_tags: ["ai", "security", "data"],
    salary_status: "no_salary",
    duplicate_key: "hybrid ai security analyst|securemodel labs|san francisco ca",
    repost_count: 1,
    quality_reasons: ["ai role signal", "security role signal", "fresh posting"],
    exclude_reasons: ["hybrid or onsite language", "no salary signal"],
    raw: {
      preview: "GitHub Pages demo fallback",
      source_name: "linkedin",
      posted_date: "2026-05-06",
    },
    skills: "Security, Python, analytics",
  },
];

export function getDemoResponse(path: string): JobsResponse | FacetsResponse | HealthResponse | null {
  const url = new URL(path, "https://demo.local");
  if (url.pathname === "/api/health") {
    return {
      status: "ok",
      clickhouse: "demo-fallback",
      latest_posted_date: "2026-05-12",
      stale: false,
      warnings: ["GitHub Pages preview is using demo data until the local API is reachable."],
    };
  }
  if (url.pathname === "/api/facets") {
    return buildFacets(DEMO_JOBS);
  }
  if (url.pathname === "/api/jobs") {
    return buildJobs(url.searchParams);
  }
  return null;
}

function buildJobs(params: URLSearchParams): JobsResponse {
  const tags = (params.get("tags") ?? "").split(",").filter(Boolean);
  const remoteQuality = params.get("remote_quality") ?? "";
  const salaryStatus = params.get("salary_status") ?? "";
  const source = params.get("source") ?? "";
  const query = (params.get("q") ?? "").toLowerCase();
  const hideReposts = params.get("hide_reposts") === "true";
  const limit = Number(params.get("limit") ?? 50);
  const offset = Number(params.get("offset") ?? 0);
  const seen = new Set<string>();

  const items = DEMO_JOBS.filter((job) => {
    if (tags.length > 0 && !tags.every((tag) => job.role_tags.includes(tag))) {
      return false;
    }
    if (remoteQuality && job.remote_quality !== remoteQuality) {
      return false;
    }
    if (salaryStatus && job.salary_status !== salaryStatus) {
      return false;
    }
    if (source && job.source !== source) {
      return false;
    }
    if (query && !searchableText(job).toLowerCase().includes(query)) {
      return false;
    }
    if (hideReposts && seen.has(job.duplicate_key)) {
      return false;
    }
    seen.add(job.duplicate_key);
    return true;
  });

  return {
    total: items.length,
    limit,
    offset,
    items: items.slice(offset, offset + limit),
  };
}

function buildFacets(jobs: JobItem[]): FacetsResponse {
  return {
    sources: count(jobs.map((job) => job.source)),
    role_tags: count(jobs.flatMap((job) => job.role_tags)),
    remote_quality: count(jobs.map((job) => job.remote_quality)),
    salary_status: count(jobs.map((job) => job.salary_status)),
    freshness: count(jobs.map((job) => job.freshness_bucket)),
  };
}

function count(values: string[]): Record<string, number> {
  return values.reduce<Record<string, number>>((accumulator, value) => {
    accumulator[value] = (accumulator[value] ?? 0) + 1;
    return accumulator;
  }, {});
}

function searchableText(job: JobItem): string {
  return [
    job.title,
    job.company,
    job.location,
    job.description,
    job.requirements,
    job.skills,
    ...job.role_tags,
  ].join(" ");
}
