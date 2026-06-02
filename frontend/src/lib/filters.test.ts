import { describe, expect, it } from "vitest";

import { buildApiQuery, needsCanonicalQuery, readFilters } from "./filters";

describe("buildApiQuery", () => {
  it("serializes dashboard filters into shareable API query params", () => {
    const query = buildApiQuery({
      days: "3",
      tags: ["vision", "agent"],
      remoteQuality: "worldwide",
      salaryStatus: "has_salary",
      source: "foorilla.com",
      q: "OCR",
      hideReposts: true,
      limit: 25,
      offset: 50,
      sort: "best_for_me",
    });

    expect(query.toString()).toBe(
      "days=3&tags=vision%2Cagent&remote_quality=worldwide&salary_status=has_salary&source=foorilla.com&q=OCR&hide_reposts=true&limit=25&offset=50&sort=best_for_me",
    );
  });

  it("uses configured defaults when the URL omits pagination and sort", () => {
    const filters = readFilters(new URLSearchParams("days=30&source=foorilla.com"));

    expect(filters.limit).toBe(500);
    expect(filters.offset).toBe(0);
    expect(filters.sort).toBe("best_for_me");
  });

  it("caps explicit URL limits at the dashboard page size", () => {
    const filters = readFilters(new URLSearchParams("limit=999"));

    expect(filters.limit).toBe(500);
  });

  it("detects empty URLs that need the canonical default page query", () => {
    const filters = readFilters(new URLSearchParams(""));

    expect(needsCanonicalQuery(new URLSearchParams(""), filters)).toBe(true);
    expect(buildApiQuery(filters).toString()).toBe("days=7&limit=500&offset=0&sort=best_for_me");
  });
});
