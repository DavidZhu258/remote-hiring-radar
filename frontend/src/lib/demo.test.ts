import { describe, expect, it } from "vitest";

import { getDemoResponse } from "./demo";

describe("getDemoResponse", () => {
  it("filters demo jobs with the same query shape as the API", () => {
    const response = getDemoResponse(
      "/api/jobs?tags=vision&remote_quality=country-limited&salary_status=has_salary&limit=10",
    );

    expect(response).toMatchObject({
      total: 1,
      items: [
        {
          title: "Remote Computer Vision Engineer",
          role_tags: ["vision", "ai"],
        },
      ],
    });
  });

  it("returns a demo health response for static GitHub Pages preview", () => {
    const response = getDemoResponse("/api/health");

    expect(response).toMatchObject({
      clickhouse: "demo-fallback",
      stale: false,
    });
  });

  it("returns demo overview counts for the data audit panel", () => {
    const response = getDemoResponse("/api/overview?days=30");

    expect(response).toMatchObject({
      total_observed: 4,
      coverage: {
        salary: {
          count: 2,
          ratio: 0.5,
        },
      },
    });
    expect(response && "top_sources" in response ? response.top_sources[0] : null).toEqual({
      name: "foorilla.com",
      count: 1,
      ratio: 0.25,
    });
  });

  it("uses the dashboard default page size for demo jobs", () => {
    const response = getDemoResponse("/api/jobs?days=7");

    expect(response).toMatchObject({
      limit: 500,
      offset: 0,
    });
  });
});
