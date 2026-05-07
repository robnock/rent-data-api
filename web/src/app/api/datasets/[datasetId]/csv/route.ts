import { NextResponse } from "next/server";

import { apiBaseUrl } from "@/lib/api-base";

type RouteContext = { params: Promise<{ datasetId: string }> };

export async function GET(
  _request: Request,
  context: RouteContext,
): Promise<Response> {
  const { datasetId } = await context.params;
  const base = apiBaseUrl();
  const key = process.env.ECON_API_KEY?.trim();
  const headers = new Headers();
  if (key) {
    headers.set("X-API-Key", key);
  }

  const upstream = await fetch(
    `${base}/datasets/${encodeURIComponent(datasetId)}/observations.csv`,
    { headers },
  );

  if (!upstream.ok) {
    const text = await upstream.text();
    return new NextResponse(text, {
      status: upstream.status,
      headers: { "content-type": upstream.headers.get("content-type") ?? "text/plain" },
    });
  }

  const out = new Headers();
  const cd = upstream.headers.get("content-disposition");
  if (cd) {
    out.set("content-disposition", cd);
  }
  out.set(
    "content-type",
    upstream.headers.get("content-type") ?? "text/csv; charset=utf-8",
  );

  return new NextResponse(upstream.body, {
    status: upstream.status,
    headers: out,
  });
}
