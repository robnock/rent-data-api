import Link from "next/link";
import type { ReactElement } from "react";

export default function DatasetNotFound(): ReactElement {
  return (
    <div className="space-y-4">
      <h1 className="text-2xl font-semibold text-zinc-900 dark:text-zinc-50">
        Dataset not found
      </h1>
      <p className="text-sm text-zinc-600 dark:text-zinc-400">
        That catalog id is not published in the warehouse yet.
      </p>
      <Link
        href="/datasets"
        className="inline-flex text-sm font-medium text-zinc-900 underline-offset-4 hover:underline dark:text-zinc-100"
      >
        Back to datasets
      </Link>
    </div>
  );
}
