export const SEARCH_COMMIT_DELAY_MS = 450;

export function normalizeSearchInput(value: string): string {
  return value.trim();
}

export function searchQueryChanged(currentQuery: string, draftQuery: string): boolean {
  return normalizeSearchInput(currentQuery) !== normalizeSearchInput(draftQuery);
}
