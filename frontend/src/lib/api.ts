import { buildApiQuery, type DashboardFilters } from "./filters";
import { getDemoResponse } from "./demo";

const API_BASE_URL = process.env.NEXT_PUBLIC_API_BASE_URL ?? "http://localhost:8000";
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
  freshness_bucket: string;
  source_trust: string;
  remote_quality: string;
  role_tags: string[];
  salary_status: string;
  duplicate_key: string;
  repost_count: number;
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

export async function fetchHealth(signal?: AbortSignal): Promise<HealthResponse> {
  return fetchJson<HealthResponse>("/api/health", signal);
}

async function fetchJson<T>(path: string, signal?: AbortSignal): Promise<T> {
  try {
    const response = await fetch(`${API_BASE_URL}${path}`, {
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
    const demoResponse = getDemoResponse(path);
    if (ENABLE_DEMO_FALLBACK && demoResponse) {
      return demoResponse as T;
    }
    throw error;
  }
}
