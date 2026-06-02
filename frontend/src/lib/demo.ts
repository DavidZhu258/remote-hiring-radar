import type { FacetsResponse, HealthResponse, JobItem, JobsResponse, OverviewResponse } from "./api";

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
    source_link_url: "https://foorilla.com/hiring/jobs/demo-vision-engineer/",
    apply_link_url: "https://foorilla.com/hiring/jobs/demo-vision-engineer/",
    freshness_bucket: "0-24h",
    source_trust: "direct_source",
    remote_quality: "country-limited",
    role_tags: ["vision", "ai"],
    salary_status: "has_salary",
    duplicate_key: "remote computer vision engineer|northstar robotics|remote us canada",
    repost_count: 1,
    target_bucket: "priority",
    target_score: 19,
    priority_terms: ["Computer Vision Engineer", "Vision Engineer", "Vision"],
    downrank_terms: [],
    personal_fit_bucket: "good_match",
    personal_fit_score: 28,
    mobility_tags: [],
    people_facing_tags: [],
    domain_tags: ["vision", "robotics", "ai"],
    risk_tags: [],
    fit_reasons: ["AI/CV/robotics domain fit"],
    quality_reasons: [
      "target role fit",
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
    source_link_url: "https://boards.greenhouse.io/demo/jobs/agent",
    apply_link_url: "https://boards.greenhouse.io/demo/jobs/agent",
    freshness_bucket: "1-3d",
    source_trust: "direct_source",
    remote_quality: "worldwide",
    role_tags: ["ai", "agent", "infra"],
    salary_status: "has_salary",
    duplicate_key: "founding ai agent engineer|workflow foundry|remote",
    repost_count: 2,
    target_bucket: "standard",
    target_score: 0,
    priority_terms: [],
    downrank_terms: [],
    personal_fit_bucket: "maybe",
    personal_fit_score: 12,
    mobility_tags: [],
    people_facing_tags: ["customer"],
    domain_tags: ["ai"],
    risk_tags: [],
    fit_reasons: ["technical transition fit", "customer-facing delivery role"],
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
    source_link_url: "https://jobsdb.com/demo/data-platform",
    apply_link_url: "",
    freshness_bucket: "1-3d",
    source_trust: "aggregator",
    remote_quality: "country-limited",
    role_tags: ["data", "infra", "ai"],
    salary_status: "no_salary",
    duplicate_key: "remote data platform engineer|signallake|remote europe",
    repost_count: 1,
    target_bucket: "priority",
    target_score: 8,
    priority_terms: ["Data Platform Engineer"],
    downrank_terms: [],
    personal_fit_bucket: "maybe",
    personal_fit_score: 13,
    mobility_tags: [],
    people_facing_tags: [],
    domain_tags: ["data_platform", "data"],
    risk_tags: ["missing_apply", "no_salary"],
    fit_reasons: ["role appears outside the target transition path"],
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
    source_link_url: "https://linkedin.com/jobs/view/demo-security",
    apply_link_url: "",
    freshness_bucket: "4-7d",
    source_trust: "aggregator",
    remote_quality: "hybrid-suspect",
    role_tags: ["ai", "security", "data"],
    salary_status: "no_salary",
    duplicate_key: "hybrid ai security analyst|securemodel labs|san francisco ca",
    repost_count: 1,
    target_bucket: "downranked",
    target_score: -8,
    priority_terms: [],
    downrank_terms: ["Security", "Analyst"],
    personal_fit_bucket: "downrank",
    personal_fit_score: -16,
    mobility_tags: [],
    people_facing_tags: [],
    domain_tags: ["ai", "data"],
    risk_tags: ["security_only", "analyst_only", "missing_apply", "no_salary", "hybrid_suspect"],
    fit_reasons: ["role appears outside the target transition path"],
    quality_reasons: ["ai role signal", "security role signal", "fresh posting"],
    exclude_reasons: [
      "downrank title terms: Security, Analyst",
      "hybrid or onsite language",
      "no salary signal",
    ],
    raw: {
      preview: "GitHub Pages demo fallback",
      source_name: "linkedin",
      posted_date: "2026-05-06",
    },
    skills: "Security, Python, analytics",
  },
];

export function getDemoResponse(
  path: string,
): JobsResponse | FacetsResponse | HealthResponse | OverviewResponse | null {
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
  if (url.pathname === "/api/overview") {
    return buildOverview(DEMO_JOBS);
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
  const limit = Number(params.get("limit") ?? 500);
  const offset = Number(params.get("offset") ?? 0);
  const sort = params.get("sort") ?? "best_for_me";
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
  if (sort === "best_for_me") {
    items.sort((left, right) => right.personal_fit_score - left.personal_fit_score);
  } else if (sort === "target_fit") {
    items.sort((left, right) => right.target_score - left.target_score);
  }

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
    target_fit: count(jobs.map((job) => job.target_bucket)),
    personal_fit: count(jobs.map((job) => job.personal_fit_bucket)),
  };
}

function buildOverview(jobs: JobItem[]): OverviewResponse {
  const total = jobs.length;
  const salaryCount = jobs.filter((job) => job.salary_status === "has_salary").length;
  const remoteFriendlyCount = jobs.filter((job) =>
    ["worldwide", "country-limited"].includes(job.remote_quality),
  ).length;
  const directSourceCount = jobs.filter((job) => job.source_trust === "direct_source").length;
  const sourceUrlCount = jobs.filter((job) => job.source_url).length;
  const applyUrlCount = jobs.filter((job) => job.apply_url).length;
  const duplicateCounts = count(jobs.map((job) => job.duplicate_key));
  const duplicateValues = Object.values(duplicateCounts);

  return {
    days: 30,
    total_observed: total,
    sample_limit: 10000,
    sample_limit_reached: false,
    latest_posted_date: "2026-05-12",
    coverage: {
      source_url: countRatio(sourceUrlCount, total),
      apply_url: countRatio(applyUrlCount, total),
      salary: countRatio(salaryCount, total),
      remote_friendly: countRatio(remoteFriendlyCount, total),
      direct_source: countRatio(directSourceCount, total),
    },
    quality: {
      duplicate_groups: duplicateValues.filter((value) => value > 1).length,
      repost_like_records: duplicateValues
        .filter((value) => value > 1)
        .reduce((sum, value) => sum + value, 0),
      missing_source_url: total - sourceUrlCount,
      no_salary: total - salaryCount,
      needs_remote_evidence: jobs.filter((job) =>
        job.exclude_reasons.includes("remote evidence missing"),
      ).length,
    },
    top_sources: topCounts(count(jobs.map((job) => job.source)), total),
    top_companies: topCounts(count(jobs.map((job) => job.company)), total),
    freshness: count(jobs.map((job) => job.freshness_bucket)),
    remote_quality: count(jobs.map((job) => job.remote_quality)),
    salary_status: count(jobs.map((job) => job.salary_status)),
    target_fit: count(jobs.map((job) => job.target_bucket)),
    personal_fit: count(jobs.map((job) => job.personal_fit_bucket)),
    role_tags: count(jobs.flatMap((job) => job.role_tags)),
  };
}

function count(values: string[]): Record<string, number> {
  return values.reduce<Record<string, number>>((accumulator, value) => {
    accumulator[value] = (accumulator[value] ?? 0) + 1;
    return accumulator;
  }, {});
}

function countRatio(countValue: number, total: number) {
  return {
    count: countValue,
    ratio: total <= 0 ? 0 : Math.round((countValue / total) * 10000) / 10000,
  };
}

function topCounts(counter: Record<string, number>, total: number) {
  return Object.entries(counter)
    .sort(([leftName, leftCount], [rightName, rightCount]) =>
      rightCount === leftCount ? leftName.localeCompare(rightName) : rightCount - leftCount,
    )
    .slice(0, 6)
    .map(([name, countValue]) => ({
      name,
      count: countValue,
      ratio: total <= 0 ? 0 : Math.round((countValue / total) * 10000) / 10000,
    }));
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
    ...job.mobility_tags,
    ...job.people_facing_tags,
    ...job.domain_tags,
  ].join(" ");
}
