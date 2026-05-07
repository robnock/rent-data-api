import type { Metadata } from "next";
import Link from "next/link";
import { notFound } from "next/navigation";
import type { ReactElement } from "react";

import {
  datasetBrowserCsvPath,
  datasetBrowserObservationsSamplePath,
  fetchDatasetDetail,
} from "@/lib/datasets-api";
import { formatIsoDate } from "@/lib/format";

type PageProps = {
  params: Promise<{
    datasetId: string;
  }>;
};

export async function generateMetadata({
  params,
}: PageProps): Promise<Metadata> {
  const { datasetId } = await params;

  try {
    const detail = await fetchDatasetDetail(datasetId);
    if (!detail) {
      return { title: "Dataset not found" };
    }
    return {
      title: `${detail.display_name} · Econ Data API`,
      description: detail.description,
    };
  } catch {
    return { title: `${datasetId} · Econ Data API` };
  }
}

export default async function DatasetDetailPage({
  params,
}: PageProps): Promise<ReactElement> {
  const { datasetId } = await params;
  let detail;
  try {
    detail = await fetchDatasetDetail(datasetId);
  } catch (err) {
    const message = err instanceof Error ? err.message : "Unknown error";
    return (
      <div className="space-y-6">
        <Link
          href="/datasets"
          className="text-sm text-zinc-600 hover:text-zinc-900 dark:text-zinc-400 dark:hover:text-zinc-100"
        >
          ← All datasets
        </Link>
        <div className="rounded-lg border border-amber-200 bg-amber-50 p-4 text-sm text-amber-950 dark:border-amber-900/60 dark:bg-amber-950/30 dark:text-amber-100">
          Could not load dataset: {message}
        </div>
      </div>
    );
  }

  if (!detail) {
    notFound();
  }

  const csvPath = datasetBrowserCsvPath(detail.id);
  const sampleJsonPath = datasetBrowserObservationsSamplePath(detail.id);

  return (
    <div className="space-y-10">
      <div className="flex flex-col gap-4 sm:flex-row sm:items-start sm:justify-between">
        <div className="min-w-0 space-y-2">
          <Link
            href="/datasets"
            className="text-sm text-zinc-600 hover:text-zinc-900 dark:text-zinc-400 dark:hover:text-zinc-100"
          >
            ← All datasets
          </Link>
          <h1 className="text-3xl font-semibold tracking-tight text-zinc-900 dark:text-zinc-50">
            {detail.display_name}
          </h1>
          <p className="font-mono text-xs text-zinc-500 dark:text-zinc-500">
            {detail.id}
          </p>
        </div>
        <div className="flex shrink-0 flex-col gap-2 sm:items-end">
          <a
            href={csvPath}
            className="inline-flex items-center justify-center rounded-md bg-zinc-900 px-4 py-2 text-sm font-semibold text-white shadow-sm transition hover:bg-zinc-800 dark:bg-zinc-100 dark:text-zinc-900 dark:hover:bg-white"
          >
            Download CSV
          </a>
          <a
            href={sampleJsonPath}
            target="_blank"
            rel="noreferrer"
            className="text-xs text-zinc-600 underline-offset-2 hover:underline dark:text-zinc-400"
          >
            Sample JSON (API)
          </a>
        </div>
      </div>

      <p className="max-w-3xl text-sm leading-7 text-zinc-600 dark:text-zinc-300">
        {detail.description}
      </p>

      <section className="rounded-lg border border-zinc-200 bg-white p-6 dark:border-zinc-800 dark:bg-zinc-950">
        <h2 className="text-sm font-semibold uppercase tracking-wide text-zinc-500 dark:text-zinc-400">
          Catalog snapshot
        </h2>
        <dl className="mt-4 grid gap-4 sm:grid-cols-2">
          <div>
            <dt className="text-xs font-medium uppercase tracking-wide text-zinc-500 dark:text-zinc-500">
              Unit
            </dt>
            <dd className="mt-1 text-sm text-zinc-900 dark:text-zinc-100">
              {detail.unit}
            </dd>
          </div>
          <div>
            <dt className="text-xs font-medium uppercase tracking-wide text-zinc-500 dark:text-zinc-500">
              Rows
            </dt>
            <dd className="mt-1 text-sm text-zinc-900 dark:text-zinc-100">
              {detail.row_count !== null ? detail.row_count.toLocaleString() : "—"}
            </dd>
          </div>
          <div>
            <dt className="text-xs font-medium uppercase tracking-wide text-zinc-500 dark:text-zinc-500">
              Period range
            </dt>
            <dd className="mt-1 text-sm text-zinc-900 dark:text-zinc-100">
              {formatIsoDate(detail.earliest_period)} →{" "}
              {formatIsoDate(detail.latest_period)}
            </dd>
          </div>
          <div>
            <dt className="text-xs font-medium uppercase tracking-wide text-zinc-500 dark:text-zinc-500">
              Release date
            </dt>
            <dd className="mt-1 text-sm text-zinc-900 dark:text-zinc-100">
              {formatIsoDate(detail.current_release_date)}
            </dd>
          </div>
        </dl>
      </section>

      <section className="space-y-4">
        <div>
          <h2 className="text-lg font-semibold text-zinc-900 dark:text-zinc-50">
            Observation schema
          </h2>
          <p className="mt-1 text-sm text-zinc-600 dark:text-zinc-400">
            Columns included in JSON and CSV exports for this dataset.
          </p>
        </div>

        <div className="overflow-x-auto rounded-lg border border-zinc-200 bg-white dark:border-zinc-800 dark:bg-zinc-950">
          <table className="min-w-full border-collapse text-left text-sm">
            <thead className="bg-zinc-50 text-xs font-semibold uppercase tracking-wide text-zinc-500 dark:bg-zinc-900 dark:text-zinc-400">
              <tr>
                <th className="px-4 py-3">Column</th>
                <th className="px-4 py-3">Type</th>
                <th className="px-4 py-3">Nullable</th>
                <th className="px-4 py-3">Description</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-zinc-200 dark:divide-zinc-800">
              {detail.observation_columns.map((col) => (
                <tr key={col.name} className="align-top">
                  <td className="px-4 py-3 font-mono text-xs text-zinc-900 dark:text-zinc-100">
                    {col.name}
                  </td>
                  <td className="px-4 py-3 text-zinc-700 dark:text-zinc-300">
                    {col.logical_type}
                  </td>
                  <td className="px-4 py-3 text-zinc-700 dark:text-zinc-300">
                    {col.nullable ? "Yes" : "No"}
                  </td>
                  <td className="px-4 py-3 text-zinc-600 dark:text-zinc-400">
                    {col.description}
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      </section>
    </div>
  );
}
