"use client";

import {
  flexRender,
  getCoreRowModel,
  useReactTable,
  type ColumnDef,
} from "@tanstack/react-table";
import { ExternalLink, RefreshCw, Search, X } from "lucide-react";
import { useRouter, useSearchParams } from "next/navigation";
import { useEffect, useMemo, useState } from "react";

import {
  fetchFacets,
  fetchHealth,
  fetchJobs,
  type FacetsResponse,
  type HealthResponse,
  type JobItem,
  type JobsResponse,
} from "../lib/api";
import { buildApiQuery, DEFAULT_FILTERS, readFilters, type DashboardFilters } from "../lib/filters";

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

export function Dashboard() {
  const router = useRouter();
  const searchParams = useSearchParams();
  const filters = useMemo(() => readFilters(searchParams), [searchParams]);
  const [jobs, setJobs] = useState<JobsResponse | null>(null);
  const [facets, setFacets] = useState<FacetsResponse | null>(null);
  const [health, setHealth] = useState<HealthResponse | null>(null);
  const [selectedJob, setSelectedJob] = useState<JobItem | null>(null);
  const [error, setError] = useState("");
  const [loading, setLoading] = useState(true);

  const queryKey = buildApiQuery(filters).toString();

  useEffect(() => {
    const controller = new AbortController();
    setLoading(true);
    setError("");
    Promise.all([
      fetchJobs(filters, controller.signal),
      fetchFacets({ days: filters.days, q: filters.q }, controller.signal),
      fetchHealth(controller.signal),
    ])
      .then(([jobsResponse, facetsResponse, healthResponse]) => {
        setJobs(jobsResponse);
        setFacets(facetsResponse);
        setHealth(healthResponse);
      })
      .catch((requestError: unknown) => {
        if (requestError instanceof DOMException && requestError.name === "AbortError") {
          return;
        }
        setError(requestError instanceof Error ? requestError.message : "Unable to load jobs");
      })
      .finally(() => setLoading(false));
    return () => controller.abort();
  }, [queryKey, filters]);

  const updateFilters = (patch: Partial<DashboardFilters>) => {
    const next = {
      ...filters,
      ...patch,
      offset: patch.offset ?? 0,
    };
    router.replace(`?${buildApiQuery(next).toString()}`, { scroll: false });
  };

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
          <span>{jobs?.total ?? 0} matches</span>
          <span>Latest {health?.latest_posted_date ?? "unknown"}</span>
          {health?.stale ? <strong>Stale data</strong> : <span>Fresh feed</span>}
        </div>
      </header>

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
              <option value="company">Company</option>
              <option value="source">Source</option>
            </select>
          </label>
          <label className="search-box">
            Keyword
            <span>
              <Search size={16} />
              <input
                value={filters.q}
                onChange={(event) => updateFilters({ q: event.target.value })}
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
          <button className="icon-button" onClick={() => updateFilters(DEFAULT_FILTERS)} type="button">
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
              <span>{job.freshness_bucket} · {job.remote_quality}</span>
              <span className="pill-row">{job.role_tags.map((tag) => <b key={tag}>{tag}</b>)}</span>
            </button>
          ))}
        </div>
      </section>

      {selectedJob ? <JobDrawer job={selectedJob} onClose={() => setSelectedJob(null)} /> : null}
    </main>
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

function Badge({ children, tone }: { children: React.ReactNode; tone: "green" | "blue" }) {
  return <span className={`badge ${tone}`}>{children}</span>;
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
