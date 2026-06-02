"use client";

import {
  flexRender,
  getCoreRowModel,
  useReactTable,
  type ColumnDef,
} from "@tanstack/react-table";
import { ExternalLink, RefreshCw, Search, X } from "lucide-react";
import { useRouter, useSearchParams } from "next/navigation";
import { useCallback, useEffect, useMemo, useState } from "react";

import {
  fetchFacets,
  fetchHealth,
  fetchJobs,
  fetchOverview,
  type FacetsResponse,
  type HealthResponse,
  type JobItem,
  type JobsResponse,
  type OverviewResponse,
  type RankedCount,
} from "../lib/api";
import {
  buildApiQuery,
  DEFAULT_FILTERS,
  needsCanonicalQuery,
  readFilters,
  type DashboardFilters,
} from "../lib/filters";
import { normalizeSearchInput, SEARCH_COMMIT_DELAY_MS, searchQueryChanged } from "../lib/search";

const TAG_OPTIONS = [
  { value: "vision", label: "Vision / Image Recognition" },
  { value: "ai", label: "AI" },
  { value: "data", label: "Data" },
  { value: "agent", label: "Agent" },
  { value: "security", label: "Security" },
  { value: "infra", label: "Infra" },
];
const DAY_OPTIONS = [
  { value: "1", label: "24h" },
  { value: "3", label: "3d" },
  { value: "7", label: "7d" },
  { value: "30", label: "30d" },
] as const;
const REMOTE_OPTIONS = ["worldwide", "country-limited", "hybrid-suspect", "unknown"];
const SALARY_OPTIONS = ["has_salary", "no_salary"];
const METADATA_REFRESH_DELAY_MS = 700;
const BEST_FOR_ME_SIGNALS = [
  "Global / Travel",
  "Customer-facing",
  "Implementation",
  "Field / Application",
  "Consulting",
  "Training / Enablement",
  "Pre-sales / Post-sales",
  "Vision / Machine Vision",
  "Robotics",
  "Edge AI",
  "AI Platform / MLOps",
  "Data Platform / Cloud",
];
const DOWNRANK_SIGNALS = [
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
];

export function Dashboard() {
  const router = useRouter();
  const searchParams = useSearchParams();
  const filters = useMemo(() => readFilters(searchParams), [searchParams]);
  const [jobs, setJobs] = useState<JobsResponse | null>(null);
  const [facets, setFacets] = useState<FacetsResponse | null>(null);
  const [health, setHealth] = useState<HealthResponse | null>(null);
  const [overview, setOverview] = useState<OverviewResponse | null>(null);
  const [selectedJob, setSelectedJob] = useState<JobItem | null>(null);
  const [draftQuery, setDraftQuery] = useState(filters.q);
  const [error, setError] = useState("");
  const [loading, setLoading] = useState(true);

  const queryKey = buildApiQuery(filters).toString();
  const keywordActive = filters.q.trim().length > 0;

  const updateFilters = useCallback(
    (patch: Partial<DashboardFilters>) => {
      const next = {
        ...filters,
        ...patch,
        offset: patch.offset ?? 0,
      };
      router.replace(`?${buildApiQuery(next).toString()}`, { scroll: false });
    },
    [filters, router],
  );

  useEffect(() => {
    if (needsCanonicalQuery(searchParams, filters)) {
      router.replace(`?${queryKey}`, { scroll: false });
    }
  }, [filters, queryKey, router, searchParams]);

  useEffect(() => {
    setDraftQuery(filters.q);
  }, [filters.q]);

  useEffect(() => {
    if (!searchQueryChanged(filters.q, draftQuery)) {
      return;
    }
    const handle = window.setTimeout(() => {
      updateFilters({ q: normalizeSearchInput(draftQuery) });
    }, SEARCH_COMMIT_DELAY_MS);
    return () => window.clearTimeout(handle);
  }, [draftQuery, filters.q, updateFilters]);

  useEffect(() => {
    const controller = new AbortController();
    let active = true;
    fetchHealth(controller.signal)
      .then((healthResponse) => {
        if (active) {
          setHealth(healthResponse);
        }
      })
      .catch((requestError: unknown) => {
        if (requestError instanceof DOMException && requestError.name === "AbortError") {
          return;
        }
        if (active) {
          setHealth(null);
        }
      });
    return () => {
      active = false;
      controller.abort();
    };
  }, []);

  useEffect(() => {
    const controller = new AbortController();
    let active = true;
    setLoading(true);
    setError("");
    fetchJobs(filters, controller.signal)
      .then((jobsResponse) => {
        if (!active) {
          return;
        }
        setJobs(jobsResponse);
      })
      .catch((requestError: unknown) => {
        if (requestError instanceof DOMException && requestError.name === "AbortError") {
          return;
        }
        if (active) {
          setError(requestError instanceof Error ? requestError.message : "Unable to load jobs");
        }
      })
      .finally(() => {
        if (active) {
          setLoading(false);
        }
      });
    return () => {
      active = false;
      controller.abort();
    };
  }, [queryKey, filters]);

  useEffect(() => {
    if (keywordActive) {
      return;
    }
    const controller = new AbortController();
    let active = true;
    const handle = window.setTimeout(() => {
      void (async () => {
        try {
          const facetsResponse = await fetchFacets(
            { days: filters.days, q: "" },
            controller.signal,
          );
          if (!active) {
            return;
          }
          setFacets(facetsResponse);
          const overviewResponse = await fetchOverview(
            { days: filters.days, q: "", source: filters.source },
            controller.signal,
          );
          if (!active) {
            return;
          }
          setOverview(overviewResponse);
        } catch (requestError: unknown) {
          if (requestError instanceof DOMException && requestError.name === "AbortError") {
            return;
          }
          if (active) {
            setError(
              requestError instanceof Error ? requestError.message : "Unable to load data summary",
            );
          }
        }
      })();
    }, METADATA_REFRESH_DELAY_MS);
    return () => {
      active = false;
      window.clearTimeout(handle);
      controller.abort();
    };
  }, [filters.days, filters.source, keywordActive]);

  const table = useReactTable({
    data: jobs?.items ?? [],
    columns: useMemo(() => createColumns(setSelectedJob), []),
    getCoreRowModel: getCoreRowModel(),
  });

  return (
    <main className="shell">
      <header className="topbar">
        <div>
          <p className="eyebrow">Remote Hiring Radar</p>
          <h1>Fresh Remote AI/Data/Agent/Vision Jobs</h1>
        </div>
        <div className="status-strip">
          <span>
            {!keywordActive && overview
              ? `${formatNumber(overview.total_observed)} observed`
              : `${jobs?.total ?? 0} matches`}
          </span>
          <span>Latest {health?.latest_posted_date ?? "unknown"}</span>
          {health?.stale ? <strong>Stale data</strong> : <span>Fresh feed</span>}
        </div>
      </header>

      <TargetSignalGuide overview={overview} />
      {!keywordActive && overview ? <DataAudit overview={overview} source={filters.source} /> : null}

      <section className="filters" aria-label="Job filters">
        <div className="segment">
          {DAY_OPTIONS.map((option) => (
            <button
              key={option.value}
              className={filters.days === option.value ? "active" : ""}
              onClick={() => updateFilters({ days: option.value })}
              type="button"
            >
              {option.label}
            </button>
          ))}
        </div>

        <div className="tag-row">
          {TAG_OPTIONS.map((option) => {
            const active = filters.tags.includes(option.value);
            const count = facets?.role_tags[option.value];
            return (
              <button
                key={option.value}
                className={active ? "chip active" : "chip"}
                onClick={() =>
                  updateFilters({
                    tags: active
                      ? filters.tags.filter((tag) => tag !== option.value)
                      : [...filters.tags, option.value],
                  })
                }
                type="button"
              >
                {option.label}
                {count ? <span>{count}</span> : null}
              </button>
            );
          })}
        </div>

        <div className="filter-grid">
          <label>
            Remote
            <select
              value={filters.remoteQuality}
              onChange={(event) => updateFilters({ remoteQuality: event.target.value })}
            >
              <option value="">All</option>
              {REMOTE_OPTIONS.map((option) => (
                <option key={option} value={option}>
                  {option}
                </option>
              ))}
            </select>
          </label>
          <label>
            Salary
            <select
              value={filters.salaryStatus}
              onChange={(event) => updateFilters({ salaryStatus: event.target.value })}
            >
              <option value="">All</option>
              {SALARY_OPTIONS.map((option) => (
                <option key={option} value={option}>
                  {option}
                </option>
              ))}
            </select>
          </label>
          <label>
            Source
            <select
              value={filters.source}
              onChange={(event) => updateFilters({ source: event.target.value })}
            >
              <option value="">All</option>
              {Object.keys(facets?.sources ?? {}).map((source) => (
                <option key={source} value={source}>
                  {source}
                </option>
              ))}
            </select>
          </label>
          <label>
            Sort
            <select
              value={filters.sort}
              onChange={(event) =>
                updateFilters({ sort: event.target.value as DashboardFilters["sort"] })
              }
            >
              <option value="fresh">Fresh</option>
              <option value="best_for_me">Best for me</option>
              <option value="target_fit">Title fit</option>
              <option value="company">Company</option>
              <option value="source">Source</option>
            </select>
          </label>
          <label className="search-box">
            Keyword
            <span>
              <Search size={16} />
              <input
                value={draftQuery}
                onChange={(event) => setDraftQuery(event.target.value)}
                onKeyDown={(event) => {
                  if (event.key === "Enter" && searchQueryChanged(filters.q, draftQuery)) {
                    event.preventDefault();
                    updateFilters({ q: normalizeSearchInput(draftQuery) });
                  }
                }}
                placeholder="OCR, robotics, agents..."
              />
            </span>
          </label>
          <label className="toggle">
            <input
              checked={filters.hideReposts}
              onChange={(event) => updateFilters({ hideReposts: event.target.checked })}
              type="checkbox"
            />
            Hide reposts
          </label>
          <button
            className="icon-button"
            onClick={() => {
              setDraftQuery(DEFAULT_FILTERS.q);
              updateFilters(DEFAULT_FILTERS);
            }}
            type="button"
          >
            <RefreshCw size={16} />
            Reset
          </button>
        </div>
      </section>

      {health?.stale ? (
        <div className="notice">Latest posted_date is {health.latest_posted_date}; use 30d if the feed is behind.</div>
      ) : null}
      {error ? <div className="error">{error}</div> : null}

      <section className="results" aria-label="Jobs">
        <div className="results-head">
          <span>{resultWindowText(jobs, loading)}</span>
          <div className="pager">
            <button
              disabled={filters.offset <= 0 || loading}
              onClick={() => updateFilters({ offset: Math.max(0, filters.offset - filters.limit) })}
              type="button"
            >
              Previous
            </button>
            <button
              disabled={!jobs || filters.offset + filters.limit >= jobs.total || loading}
              onClick={() => updateFilters({ offset: filters.offset + filters.limit })}
              type="button"
            >
              Next
            </button>
          </div>
        </div>
        <div className="table-wrap desktop-table">
          <table>
            <thead>
              {table.getHeaderGroups().map((headerGroup) => (
                <tr key={headerGroup.id}>
                  {headerGroup.headers.map((header) => (
                    <th key={header.id}>
                      {flexRender(header.column.columnDef.header, header.getContext())}
                    </th>
                  ))}
                </tr>
              ))}
            </thead>
            <tbody>
              {loading ? (
                <tr>
                  <td colSpan={table.getAllColumns().length}>Loading jobs...</td>
                </tr>
              ) : table.getRowModel().rows.length === 0 ? (
                <tr>
                  <td colSpan={table.getAllColumns().length}>No matching jobs.</td>
                </tr>
              ) : (
                table.getRowModel().rows.map((row) => (
                  <tr key={row.id} onClick={() => setSelectedJob(row.original)}>
                    {row.getVisibleCells().map((cell) => (
                      <td key={cell.id}>
                        {flexRender(cell.column.columnDef.cell, cell.getContext())}
                      </td>
                    ))}
                  </tr>
                ))
              )}
            </tbody>
          </table>
        </div>

        <div className="mobile-cards">
          {(jobs?.items ?? []).map((job) => (
            <button className="job-card" key={job.source_url || job.duplicate_key} onClick={() => setSelectedJob(job)} type="button">
              <span className="job-title">{job.title}</span>
              <span>{job.company}</span>
              <span>
                {job.freshness_bucket} · {job.remote_quality} · {job.target_bucket}{" "}
                {job.target_score}
              </span>
              <span className="pill-row">{job.role_tags.map((tag) => <b key={tag}>{tag}</b>)}</span>
              <PersonalTagChips job={job} />
            </button>
          ))}
        </div>
      </section>

      {selectedJob ? <JobDrawer job={selectedJob} onClose={() => setSelectedJob(null)} /> : null}
    </main>
  );
}

function TargetSignalGuide({ overview }: { overview: OverviewResponse | null }) {
  const fitCounts = overview?.personal_fit ?? {};
  const strongCount = fitCounts.strong_match ?? 0;
  const goodCount = fitCounts.good_match ?? 0;
  return (
    <section className="target-signals" aria-label="Target role signals">
      <div className="signal-group priority">
        <div className="signal-title">
          <span>Best for me signals</span>
          <b>{formatNumber(strongCount + goodCount)} strong/good rows</b>
        </div>
        <SignalTerms terms={BEST_FOR_ME_SIGNALS} tone="positive" />
      </div>
      <div className="signal-group downrank">
        <div className="signal-title">
          <span>Non-priority signals</span>
          <b>{formatNumber(fitCounts.downranked ?? 0)} downranked rows</b>
        </div>
        <SignalTerms terms={DOWNRANK_SIGNALS} tone="negative" />
      </div>
    </section>
  );
}

function SignalTerms({ terms, tone }: { terms: string[]; tone: "positive" | "negative" }) {
  return (
    <div className="term-list">
      {terms.map((term) => (
        <span className={`term ${tone}`} key={term}>
          {term}
        </span>
      ))}
    </div>
  );
}

function DataAudit({ overview, source }: { overview: OverviewResponse; source: string }) {
  const subtitle = source ? `${source} · ${overview.days}d window` : `All sources · ${overview.days}d window`;
  return (
    <section className="data-audit" aria-label="Current job data overview">
      <div className="audit-head">
        <div>
          <p className="eyebrow">Current data</p>
          <h2>{formatNumber(overview.total_observed)} observed jobs</h2>
          <span>{subtitle}</span>
        </div>
        <div className="audit-status">
          <span>Latest {overview.latest_posted_date ?? "unknown"}</span>
          {overview.sample_limit_reached ? (
            <strong>Sample capped at {formatNumber(overview.sample_limit)}</strong>
          ) : (
            <span>Full sampled window</span>
          )}
        </div>
      </div>

      <div className="metric-grid">
        <Metric
          label="Source evidence"
          value={formatPercent(overview.coverage.source_url.ratio)}
          detail={`${formatNumber(overview.coverage.source_url.count)} rows with URL`}
        />
        <Metric
          label="Direct-source"
          value={formatPercent(overview.coverage.direct_source.ratio)}
          detail={`${formatNumber(overview.coverage.direct_source.count)} direct rows`}
        />
        <Metric
          label="Remote-friendly"
          value={formatPercent(overview.coverage.remote_friendly.ratio)}
          detail={`${formatNumber(overview.coverage.remote_friendly.count)} rows`}
        />
        <Metric
          label="Salary signal"
          value={formatPercent(overview.coverage.salary.ratio)}
          detail={`${formatNumber(overview.coverage.salary.count)} rows`}
        />
        <Metric
          label="Repost groups"
          value={formatNumber(overview.quality.duplicate_groups)}
          detail={`${formatNumber(overview.quality.repost_like_records)} repost-like rows`}
        />
      </div>

      <div className="audit-columns">
        <Distribution
          data={overview.freshness}
          order={["0-24h", "1-3d", "4-7d", "8-30d", "stale", "unknown"]}
          title="Freshness"
        />
        <Distribution
          data={overview.remote_quality}
          order={["worldwide", "country-limited", "hybrid-suspect", "unknown"]}
          title="Remote quality"
        />
        <Distribution
          data={overview.role_tags}
          order={["vision", "ai", "data", "agent", "security", "infra"]}
          title="Role signals"
        />
        <TopList items={overview.top_sources} title="Top sources" />
        <TopList items={overview.top_companies} title="Top companies" />
      </div>

      <div className="data-warnings">
        <span>{formatNumber(overview.quality.no_salary)} rows without salary</span>
        <span>{formatNumber(overview.quality.needs_remote_evidence)} need remote evidence</span>
        <span>{formatNumber(overview.quality.missing_source_url)} missing source URLs</span>
      </div>
    </section>
  );
}

function Metric({ label, value, detail }: { label: string; value: string; detail: string }) {
  return (
    <div className="metric">
      <span>{label}</span>
      <strong>{value}</strong>
      <small>{detail}</small>
    </div>
  );
}

function Distribution({
  data,
  order,
  title,
}: {
  data: Record<string, number>;
  order: string[];
  title: string;
}) {
  const entries = orderedEntries(data, order);
  const total = entries.reduce((sum, [, count]) => sum + count, 0);
  return (
    <div className="audit-panel">
      <h3>{title}</h3>
      <div className="bar-list">
        {entries.map(([name, count]) => {
          const share = total > 0 ? count / total : 0;
          return (
            <div className="bar-row" key={name}>
              <span>{name}</span>
              <div>
                <i style={{ width: `${Math.max(share * 100, count > 0 ? 4 : 0)}%` }} />
              </div>
              <b>{formatNumber(count)}</b>
            </div>
          );
        })}
      </div>
    </div>
  );
}

function TopList({ items, title }: { items: RankedCount[]; title: string }) {
  return (
    <div className="audit-panel">
      <h3>{title}</h3>
      <ol className="rank-list">
        {items.map((item) => (
          <li key={item.name}>
            <span>{item.name}</span>
            <b>{formatNumber(item.count)}</b>
          </li>
        ))}
      </ol>
    </div>
  );
}

function createColumns(onSelect: (job: JobItem) => void): ColumnDef<JobItem>[] {
  return [
    {
      header: "Title",
      accessorKey: "title",
      cell: ({ row }) => (
        <button className="title-button" onClick={() => onSelect(row.original)} type="button">
          <strong>{row.original.title}</strong>
          <span>{row.original.location || "Location unknown"}</span>
        </button>
      ),
    },
    {
      header: "Company",
      accessorKey: "company",
    },
    {
      header: "Best For Me",
      accessorKey: "personal_fit_score",
      cell: ({ row }) => (
        <div className="fit-cell">
          <FitBadge bucket={row.original.personal_fit_bucket} score={row.original.personal_fit_score} />
          <PersonalTagChips job={row.original} limit={4} />
        </div>
      ),
    },
    {
      header: "Freshness",
      accessorKey: "freshness_bucket",
      cell: ({ row }) => <Badge tone="green">{row.original.freshness_bucket}</Badge>,
    },
    {
      header: "Remote",
      accessorKey: "remote_quality",
      cell: ({ row }) => <Badge tone="blue">{row.original.remote_quality}</Badge>,
    },
    {
      header: "Tags",
      accessorKey: "role_tags",
      cell: ({ row }) => (
        <div className="pill-row">
          {row.original.role_tags.map((tag) => (
            <b key={tag}>{tag}</b>
          ))}
        </div>
      ),
    },
    {
      header: "Salary",
      accessorKey: "salary_status",
      cell: ({ row }) => row.original.salary || row.original.salary_status,
    },
    {
      header: "Source",
      accessorKey: "source",
    },
    {
      header: "Repost",
      accessorKey: "repost_count",
      cell: ({ row }) => (row.original.repost_count > 1 ? `${row.original.repost_count}x` : "-"),
    },
    {
      header: "Reason",
      accessorKey: "quality_reasons",
      cell: ({ row }) => row.original.quality_reasons.slice(0, 2).join(", "),
    },
    {
      header: "Links",
      accessorKey: "source_url",
      cell: ({ row }) => (
        <div className="link-row">
          <a href={row.original.source_link_url || row.original.source_url} onClick={(event) => event.stopPropagation()} rel="noreferrer" target="_blank">
            <ExternalLink size={15} /> Source
          </a>
          {row.original.apply_link_url ? (
            <a href={row.original.apply_link_url} onClick={(event) => event.stopPropagation()} rel="noreferrer" target="_blank">
              Apply
            </a>
          ) : null}
        </div>
      ),
    },
  ];
}

function resultWindowText(jobs: JobsResponse | null, loading: boolean): string {
  if (loading) {
    return "Loading jobs...";
  }
  if (!jobs || jobs.total === 0) {
    return "No matching jobs";
  }
  const start = jobs.offset + 1;
  const end = Math.min(jobs.offset + jobs.items.length, jobs.total);
  return `Showing ${formatNumber(start)}-${formatNumber(end)} of ${formatNumber(jobs.total)} matches`;
}

function orderedEntries(data: Record<string, number>, order: string[]) {
  const known = order
    .filter((name) => data[name] !== undefined)
    .map((name) => [name, data[name]] as [string, number]);
  const rest = Object.entries(data)
    .filter(([name]) => !order.includes(name))
    .sort(([leftName, leftCount], [rightName, rightCount]) =>
      rightCount === leftCount ? leftName.localeCompare(rightName) : rightCount - leftCount,
    );
  return [...known, ...rest];
}

function formatNumber(value: number): string {
  return new Intl.NumberFormat("en-US").format(value);
}

function formatPercent(value: number): string {
  return `${Math.round(value * 100)}%`;
}

function Badge({ children, tone }: { children: React.ReactNode; tone: "green" | "blue" }) {
  return <span className={`badge ${tone}`}>{children}</span>;
}

function FitBadge({ bucket, score }: { bucket: string; score: number }) {
  return (
    <span className={`fit-badge ${bucket}`}>
      {formatTag(bucket)} {score}
    </span>
  );
}

function PersonalTagChips({ job, limit }: { job: JobItem; limit?: number }) {
  const positive = [
    ...job.mobility_tags,
    ...job.people_facing_tags,
    ...job.domain_tags,
    ...job.priority_terms,
  ].slice(0, limit);
  const negative = job.risk_tags.length > 0 ? job.risk_tags.slice(0, limit ? 2 : undefined) : job.downrank_terms;
  return <TermChips negative={negative} positive={positive} />;
}

function TermChips({ positive, negative }: { positive: string[]; negative: string[] }) {
  if (positive.length === 0 && negative.length === 0) {
    return null;
  }
  return (
    <div className="term-chip-row">
      {positive.map((term) => (
        <span className="term positive" key={`positive-${term}`}>
          {formatTag(term)}
        </span>
      ))}
      {negative.map((term) => (
        <span className="term negative" key={`negative-${term}`}>
          {formatTag(term)}
        </span>
      ))}
    </div>
  );
}

function formatTag(value: string): string {
  return value
    .split("_")
    .map((part) => (part.length <= 3 ? part.toUpperCase() : part[0].toUpperCase() + part.slice(1)))
    .join(" ");
}

function JobDrawer({ job, onClose }: { job: JobItem; onClose: () => void }) {
  const rawEntries = Object.entries(job.raw ?? {});
  return (
    <aside className="drawer" aria-label="Job details">
      <div className="drawer-head">
        <div>
          <h2>{job.title}</h2>
          <p>{job.company} · {job.location || "Location unknown"}</p>
        </div>
        <button className="icon-only" onClick={onClose} type="button" aria-label="Close details">
          <X size={18} />
        </button>
      </div>
      <div className="drawer-links">
        <a href={job.source_link_url || job.source_url} rel="noreferrer" target="_blank">
          <ExternalLink size={16} /> Source evidence
        </a>
        {job.apply_link_url ? <a href={job.apply_link_url} rel="noreferrer" target="_blank">Apply</a> : null}
      </div>
      <section>
        <h3>Signals</h3>
        <div className="pill-row">
          {[job.freshness_bucket, job.remote_quality, job.salary_status, job.source_trust].map((item) => (
            <b key={item}>{item}</b>
          ))}
        </div>
        <p>{job.quality_reasons.join(", ") || "No positive reasons recorded."}</p>
        {job.exclude_reasons.length > 0 ? <p className="muted">{job.exclude_reasons.join(", ")}</p> : null}
      </section>
      <section>
        <h3>Best For Me</h3>
        <div className="fit-detail">
          <FitBadge bucket={job.personal_fit_bucket} score={job.personal_fit_score} />
          <PersonalTagChips job={job} />
        </div>
        <p>{job.fit_reasons.join(", ") || "No personal-fit reasons recorded."}</p>
      </section>
      <section>
        <h3>Title Fit</h3>
        <div className="fit-detail">
          <FitBadge bucket={job.target_bucket} score={job.target_score} />
          <TermChips negative={job.downrank_terms} positive={job.priority_terms} />
        </div>
      </section>
      <section>
        <h3>Description</h3>
        <p>{job.description || "No description available."}</p>
      </section>
      <section>
        <h3>Requirements</h3>
        <p>{job.requirements || job.skills || "No requirements available."}</p>
      </section>
      <section>
        <h3>Duplicate / Repost</h3>
        <p>{job.repost_count} matching record(s) for key {job.duplicate_key}</p>
      </section>
      <section>
        <h3>Raw Fields</h3>
        <dl>
          <div>
            <dt>job_id</dt>
            <dd>{job.job_id || "unknown"}</dd>
          </div>
          {rawEntries.map(([key, value]) => (
            <div key={key}>
              <dt>{key}</dt>
              <dd>{String(value ?? "")}</dd>
            </div>
          ))}
        </dl>
      </section>
    </aside>
  );
}
