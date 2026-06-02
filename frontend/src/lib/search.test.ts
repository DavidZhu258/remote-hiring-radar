import { describe, expect, it } from "vitest";

import { normalizeSearchInput, searchQueryChanged } from "./search";

describe("search query helpers", () => {
  it("normalizes keyword input before committing it to the URL", () => {
    expect(normalizeSearchInput("  OCR  ")).toBe("OCR");
  });

  it("does not commit a new search when only whitespace changed", () => {
    expect(searchQueryChanged("OCR", " OCR ")).toBe(false);
    expect(searchQueryChanged("OCR", "robotics")).toBe(true);
  });
});
