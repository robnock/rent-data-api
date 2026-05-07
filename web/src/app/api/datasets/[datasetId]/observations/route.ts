import { NextResponse } from "next/server";

import { apiBaseUrl } from "@/lib/api-base";

type RouteContext = { params: Promise<{ datasetId: string }> };

export async function GET(
  request: Request,
  context: RouteContext,
): Promise<Response> {
  const { datasetId } = await context.params;
  const incoming = new URL(request.url);
  const qs = incoming.search;

  const base = apiBaseUrl();
  const key = process.env.ECON_API_KEY?.trim();
  const headers = new Headers();
  headers.set("Accept", "application/json");
  if (key) {
    headers.set("X-API-Key", key);
  }

  const upstream = await fetch(
    `${base}/datasets/${encodeURIComponent(datasetId)}/observations${qs}`,
    { headers, cache: "no-store" },
  );

  const text = await upstream.text();
  return new NextResponse(text, {
    status: upstream.status,
    headers: {
      "content-type":
        upstream.headers.get("content-type") ?? "application/json; charset=utf-8",
    },
  });
}
