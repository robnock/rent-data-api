/** Resolved public API origin for server + browser bundles. */

export function apiBaseUrl(): string {
  const raw = process.env.NEXT_PUBLIC_API_BASE_URL?.trim();
  if (!raw) {
    return "http://localhost:8000";
  }
  const trimmed = raw.replace(/\/+$/, "");
  // Vercel env vars are sometimes entered without a scheme (e.g. `foo.up.railway.app`).
  // `fetch()` requires an absolute URL with protocol.
  if (/^https?:\/\//i.test(trimmed)) {
    return trimmed;
  }
  return `https://${trimmed}`;
}
