/** Resolved public API origin for server + browser bundles. */

export function apiBaseUrl(): string {
  const raw = process.env.NEXT_PUBLIC_API_BASE_URL?.trim();
  if (!raw) {
    return "http://localhost:8000";
  }
  return raw.replace(/\/+$/, "");
}
