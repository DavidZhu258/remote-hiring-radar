import { describe, expect, it } from "vitest";

import { apiBaseUrls } from "./api";

describe("apiBaseUrls", () => {
  it("tries the current-code local API before older local defaults", () => {
    expect(apiBaseUrls(undefined)).toEqual([
      "http://127.0.0.1:8011",
      "http://127.0.0.1:8010",
      "http://localhost:8000",
    ]);
  });

  it("prefers a configured API URL while keeping local fallbacks", () => {
    expect(apiBaseUrls("http://127.0.0.1:8011/")).toEqual([
      "http://127.0.0.1:8011",
      "http://127.0.0.1:8010",
      "http://localhost:8000",
    ]);
  });
});
