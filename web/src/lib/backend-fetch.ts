/** Server-side fetch helpers: forwards `ECON_API_KEY` to the FastAPI origin. */

export function withBackendApiHeaders(init: RequestInit = {}): RequestInit {
  const headers = new Headers(init.headers ?? undefined);
  if (!headers.has("Accept")) {
    headers.set("Accept", "application/json");
  }
  const key = process.env.ECON_API_KEY?.trim();
  if (key) {
    headers.set("X-API-Key", key);
  }
  return { ...init, headers, cache: init.cache ?? "no-store" };
}
