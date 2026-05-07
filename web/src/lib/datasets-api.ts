import { cache } from "react";

import { apiBaseUrl } from "@/lib/api-base";
import { withBackendApiHeaders } from "@/lib/backend-fetch";
import type { DatasetDetail, DatasetSummary } from "@/lib/types";

export async function fetchDatasetSummaries(): Promise<DatasetSummary[]> {
  const url = `${apiBaseUrl()}/datasets`;
  const response = await fetch(url, withBackendApiHeaders());

  if (!response.ok) {
    throw new Error(
      `Dataset list failed (HTTP ${response.status}). Is the API running at ${apiBaseUrl()}?`,
    );
  }

  return (await response.json()) as DatasetSummary[];
}

async function loadDatasetDetail(
  datasetId: string,
): Promise<DatasetDetail | null> {
  const url = `${apiBaseUrl()}/datasets/${encodeURIComponent(datasetId)}`;
  const response = await fetch(url, withBackendApiHeaders());

  if (response.status === 404) {
    return null;
  }

  if (!response.ok) {
    throw new Error(
      `Dataset detail failed (HTTP ${response.status}). Is the API running at ${apiBaseUrl()}?`,
    );
  }

  return (await response.json()) as DatasetDetail;
}

/** Deduplicates detail fetches inside a single React request (metadata + page). */
export const fetchDatasetDetail = cache(loadDatasetDetail);

/** Same-origin proxy so browser downloads work when the API requires `X-API-Key`. */
export function datasetBrowserCsvPath(datasetId: string): string {
  return `/api/datasets/${encodeURIComponent(datasetId)}/csv`;
}

export function datasetBrowserObservationsSamplePath(datasetId: string): string {
  const query = new URLSearchParams({ limit: "25" }).toString();
  return `/api/datasets/${encodeURIComponent(datasetId)}/observations?${query}`;
}
