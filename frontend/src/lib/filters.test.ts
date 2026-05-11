import { describe, expect, it } from "vitest";

import { buildApiQuery } from "./filters";

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
      sort: "fresh",
    });

    expect(query.toString()).toBe(
      "days=3&tags=vision%2Cagent&remote_quality=worldwide&salary_status=has_salary&source=foorilla.com&q=OCR&hide_reposts=true&limit=25&offset=50&sort=fresh",
    );
  });
});
