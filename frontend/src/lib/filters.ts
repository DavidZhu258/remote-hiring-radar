export type DayWindow = "1" | "3" | "7" | "30";
export type DashboardSort = "best_for_me" | "fresh" | "target_fit" | "company" | "source";

export type DashboardFilters = {
  days: DayWindow;
  tags: string[];
  remoteQuality: string;
  salaryStatus: string;
  source: string;
  q: string;
  hideReposts: boolean;
  limit: number;
  offset: number;
  sort: DashboardSort;
};

export const DEFAULT_FILTERS: DashboardFilters = {
  days: "7",
  tags: [],
  remoteQuality: "",
  salaryStatus: "",
  source: "",
  q: "",
  hideReposts: false,
  limit: 500,
  offset: 0,
  sort: "best_for_me",
};

export function buildApiQuery(filters: DashboardFilters): URLSearchParams {
  const params = new URLSearchParams();
  params.set("days", filters.days);
  if (filters.tags.length > 0) {
    params.set("tags", filters.tags.join(","));
  }
  if (filters.remoteQuality) {
    params.set("remote_quality", filters.remoteQuality);
  }
  if (filters.salaryStatus) {
    params.set("salary_status", filters.salaryStatus);
  }
  if (filters.source) {
    params.set("source", filters.source);
  }
  if (filters.q.trim()) {
    params.set("q", filters.q.trim());
  }
  if (filters.hideReposts) {
    params.set("hide_reposts", "true");
  }
  params.set("limit", String(filters.limit));
  params.set("offset", String(filters.offset));
  params.set("sort", filters.sort);
  return params;
}

export function needsCanonicalQuery(params: URLSearchParams, filters: DashboardFilters): boolean {
  return params.toString() !== buildApiQuery(filters).toString();
}

export function readFilters(params: URLSearchParams): DashboardFilters {
  const days = normalizeDays(params.get("days"));
  const sort = normalizeSort(params.get("sort"));
  const tags = (params.get("tags") ?? "")
    .split(",")
    .map((tag) => tag.trim())
    .filter(Boolean);

  return {
    days,
    tags,
    remoteQuality: params.get("remote_quality") ?? "",
    salaryStatus: params.get("salary_status") ?? "",
    source: params.get("source") ?? "",
    q: params.get("q") ?? "",
    hideReposts: params.get("hide_reposts") === "true",
    limit: normalizeNumber(params.get("limit"), DEFAULT_FILTERS.limit, 1, 500),
    offset: normalizeNumber(params.get("offset"), DEFAULT_FILTERS.offset, 0, 10000),
    sort,
  };
}

function normalizeDays(value: string | null): DayWindow {
  if (value === "1" || value === "3" || value === "7" || value === "30") {
    return value;
  }
  return DEFAULT_FILTERS.days;
}

function normalizeSort(value: string | null): DashboardSort {
  if (
    value === "best_for_me" ||
    value === "fresh" ||
    value === "target_fit" ||
    value === "company" ||
    value === "source"
  ) {
    return value;
  }
  return DEFAULT_FILTERS.sort;
}

function normalizeNumber(value: string | null, fallback: number, min: number, max: number): number {
  if (value === null || value.trim() === "") {
    return fallback;
  }
  const parsed = Number(value);
  if (!Number.isFinite(parsed)) {
    return fallback;
  }
  return Math.min(Math.max(Math.trunc(parsed), min), max);
}
