import { buildApiQuery, type DashboardFilters } from "./filters";
import { getDemoResponse } from "./demo";

const DEFAULT_API_BASE_URLS = [
  "http://127.0.0.1:8011",
  "http://127.0.0.1:8010",
  "http://localhost:8000",
];
const ENABLE_DEMO_FALLBACK = process.env.NEXT_PUBLIC_ENABLE_DEMO_FALLBACK === "true";

export type JobItem = {
  job_id: string;
  title: string;
  company: string;
  location: string;
  description: string;
  requirements: string;
  responsibilities: string;
  benefits: string;
  skills: string;
  posted_at: string | null;
  salary: string;
  salary_detail: string;
  budget_min: number | null;
  budget_max: number | null;
  budget_currency: string;
  source: string;
  source_url: string;
  apply_url: string;
  source_link_url: string;
  apply_link_url: string;
  freshness_bucket: string;
  source_trust: string;
  remote_quality: string;
  role_tags: string[];
  salary_status: string;
  duplicate_key: string;
  repost_count: number;
  target_bucket: string;
  target_score: number;
  priority_terms: string[];
  downrank_terms: string[];
  personal_fit_bucket: string;
  personal_fit_score: number;
  mobility_tags: string[];
  people_facing_tags: string[];
  domain_tags: string[];
  risk_tags: string[];
  fit_reasons: string[];
  quality_reasons: string[];
  exclude_reasons: string[];
  raw: Record<string, unknown>;
};

export type JobsResponse = {
  total: number;
  limit: number;
  offset: number;
  items: JobItem[];
};

export type FacetsResponse = {
  sources: Record<string, number>;
  role_tags: Record<string, number>;
  remote_quality: Record<string, number>;
  salary_status: Record<string, number>;
  freshness: Record<string, number>;
  target_fit: Record<string, number>;
  personal_fit: Record<string, number>;
};

export type CountRatio = {
  count: number;
  ratio: number;
};

export type RankedCount = CountRatio & {
  name: string;
};

export type OverviewResponse = {
  days: number;
  total_observed: number;
  sample_limit: number;
  sample_limit_reached: boolean;
  latest_posted_date: string | null;
  coverage: {
    source_url: CountRatio;
    apply_url: CountRatio;
    salary: CountRatio;
    remote_friendly: CountRatio;
    direct_source: CountRatio;
  };
  quality: {
    duplicate_groups: number;
    repost_like_records: number;
    missing_source_url: number;
    no_salary: number;
    needs_remote_evidence: number;
  };
  top_sources: RankedCount[];
  top_companies: RankedCount[];
  freshness: Record<string, number>;
  remote_quality: Record<string, number>;
  salary_status: Record<string, number>;
  target_fit: Record<string, number>;
  personal_fit: Record<string, number>;
  role_tags: Record<string, number>;
};

export type HealthResponse = {
  status: string;
  clickhouse: string;
  latest_posted_date: string | null;
  stale: boolean;
  warnings: string[];
};

export async function fetchJobs(filters: DashboardFilters, signal?: AbortSignal): Promise<JobsResponse> {
  return fetchJson<JobsResponse>(`/api/jobs?${buildApiQuery(filters).toString()}`, signal);
}

export async function fetchFacets(filters: Pick<DashboardFilters, "days" | "q">, signal?: AbortSignal): Promise<FacetsResponse> {
  const params = new URLSearchParams();
  params.set("days", filters.days);
  if (filters.q.trim()) {
    params.set("q", filters.q.trim());
  }
  return fetchJson<FacetsResponse>(`/api/facets?${params.toString()}`, signal);
}

export async function fetchOverview(filters: Pick<DashboardFilters, "days" | "q" | "source">, signal?: AbortSignal): Promise<OverviewResponse> {
  const params = new URLSearchParams();
  params.set("days", filters.days);
  if (filters.source.trim()) {
    params.set("source", filters.source.trim());
  }
  if (filters.q.trim()) {
    params.set("q", filters.q.trim());
  }
  return fetchJson<OverviewResponse>(`/api/overview?${params.toString()}`, signal);
}

export async function fetchHealth(signal?: AbortSignal): Promise<HealthResponse> {
  return fetchJson<HealthResponse>("/api/health", signal);
}

async function fetchJson<T>(path: string, signal?: AbortSignal): Promise<T> {
  let lastError: unknown = new Error("No API base URL configured");
  for (const baseUrl of apiBaseUrls()) {
    try {
      const response = await fetch(`${baseUrl}${path}`, {
        signal,
        headers: {
          Accept: "application/json",
        },
      });
      if (!response.ok) {
        const detail = await response.text();
        throw new Error(detail || `Request failed with ${response.status}`);
      }
      return response.json() as Promise<T>;
    } catch (error) {
      if (error instanceof DOMException && error.name === "AbortError") {
        throw error;
      }
      lastError = error;
    }
  }

  const demoResponse = getDemoResponse(path);
  if (ENABLE_DEMO_FALLBACK && demoResponse) {
    return demoResponse as T;
  }
  throw lastError;
}

export function apiBaseUrls(configuredUrl = process.env.NEXT_PUBLIC_API_BASE_URL): string[] {
  const configured = configuredUrl ? [configuredUrl] : [];
  return uniqueUrls([...configured, ...DEFAULT_API_BASE_URLS]);
}

function uniqueUrls(urls: string[]): string[] {
  return [...new Set(urls.map((url) => url.trim().replace(/\/+$/, "")).filter(Boolean))];
}
