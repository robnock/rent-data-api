import type { ReactElement } from "react";
import Link from "next/link";

import { fetchDatasetSummaries } from "@/lib/datasets-api";
import { formatIsoDate } from "@/lib/format";

export default async function DatasetsIndexPage(): Promise<ReactElement> {
  let datasets;
  try {
    datasets = await fetchDatasetSummaries();
  } catch (err) {
    const detail = err instanceof Error ? err.message : "Unknown error";
    return (
      <div className="space-y-6">
        <div>
          <h1 className="text-3xl font-semibold tracking-tight text-zinc-900 dark:text-zinc-50">
            Datasets
          </h1>
          <p className="mt-2 max-w-2xl text-sm leading-7 text-zinc-600 dark:text-zinc-400">
            Published rental-market metrics mirrored from `/data/` into Postgres,
            surfaced here and via GET endpoints.
          </p>
        </div>
        <div className="rounded-lg border border-amber-200 bg-amber-50 p-4 text-sm text-amber-950 dark:border-amber-900/60 dark:bg-amber-950/30 dark:text-amber-100">
          Could not load datasets: {detail}
        </div>
      </div>
    );
  }

  return (
    <div className="space-y-8">
      <div>
        <h1 className="text-3xl font-semibold tracking-tight text-zinc-900 dark:text-zinc-50">
          Datasets
        </h1>
        <p className="mt-2 max-w-2xl text-sm leading-7 text-zinc-600 dark:text-zinc-400">
          Monthly releases keyed by catalog id. Rows and period bounds summarize
          the ingested warehouse snapshot.
        </p>
      </div>

      {datasets.length === 0 ? (
        <div className="rounded-lg border border-zinc-200 bg-white p-6 text-sm text-zinc-600 dark:border-zinc-800 dark:bg-zinc-950 dark:text-zinc-400">
          No datasets yet — run Postgres migrations plus ingest (`python -m ingest`)
          from the repo root, then reload.
        </div>
      ) : (
        <ul className="divide-y divide-zinc-200 rounded-lg border border-zinc-200 bg-white dark:divide-zinc-800 dark:border-zinc-800 dark:bg-zinc-950">
          {datasets.map((d) => (
            <li key={d.id}>
              <Link
                href={`/datasets/${d.id}`}
                className="block px-6 py-5 transition-colors hover:bg-zinc-50 dark:hover:bg-zinc-900"
              >
                <div className="flex flex-col gap-3 sm:flex-row sm:items-baseline sm:justify-between">
                  <div className="min-w-0">
                    <div className="truncate text-lg font-semibold text-zinc-900 dark:text-zinc-50">
                      {d.display_name}
                    </div>
                    <div className="mt-1 font-mono text-xs text-zinc-500 dark:text-zinc-500">
                      {d.id}
                    </div>
                  </div>
                  <div className="shrink-0 text-xs text-zinc-500 dark:text-zinc-500">
                    {d.row_count !== null ? (
                      <>
                        <span>{d.row_count.toLocaleString()} rows</span>
                        <span aria-hidden className="px-2 text-zinc-300 dark:text-zinc-700">
                          ·
                        </span>
                        <span>{formatIsoDate(d.earliest_period)} → </span>
                        <span>{formatIsoDate(d.latest_period)}</span>
                      </>
                    ) : (
                      <span>No row stats</span>
                    )}
                  </div>
                </div>
                <p className="mt-3 text-xs uppercase tracking-wide text-zinc-500 dark:text-zinc-500">
                  Unit:{" "}
                  <span className="font-semibold tracking-normal normal-case text-zinc-700 dark:text-zinc-300">
                    {d.unit}
                  </span>
                </p>
              </Link>
            </li>
          ))}
        </ul>
      )}
    </div>
  );
}
