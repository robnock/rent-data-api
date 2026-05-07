import Link from "next/link";
import type { ReactElement } from "react";

export default function Home(): ReactElement {
  return (
    <div className="flex flex-1 flex-col justify-center font-sans">
      <div className="mx-auto w-full max-w-4xl px-8 py-24">
        <p className="mb-3 text-xs font-medium uppercase tracking-widest text-zinc-500 dark:text-zinc-400">
          v1 &middot; experimental
        </p>
        <h1 className="text-5xl font-semibold tracking-tight text-zinc-900 dark:text-zinc-50">
          Econ Data API
        </h1>
        <p className="mt-6 max-w-2xl text-lg leading-8 text-zinc-600 dark:text-zinc-300">
          A public catalog and API for rental market data. Browse datasets,
          inspect their schema, download the latest CSVs, or query the data
          programmatically.
        </p>
        <div className="mt-10 flex flex-col gap-4 sm:flex-row sm:items-center">
          <Link
            href="/datasets"
            className="inline-flex items-center justify-center rounded-md bg-zinc-900 px-5 py-2.5 text-sm font-semibold text-white shadow-sm transition hover:bg-zinc-800 dark:bg-zinc-100 dark:text-zinc-900 dark:hover:bg-white"
          >
            Browse datasets
          </Link>
          <span className="text-sm text-zinc-600 dark:text-zinc-400">
            JSON + CSV endpoints are documented under{" "}
            <strong className="font-medium text-zinc-800 dark:text-zinc-200">
              API docs
            </strong>{" "}
            above.
          </span>
        </div>
      </div>
    </div>
  );
}
