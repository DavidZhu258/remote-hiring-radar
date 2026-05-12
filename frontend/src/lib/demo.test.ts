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
});
