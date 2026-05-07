import type { ReactElement } from "react";
import Link from "next/link";

import { apiBaseUrl } from "@/lib/api-base";

export function SiteHeader(): ReactElement {
  const docsHref = `${apiBaseUrl()}/docs`;

  return (
    <header className="border-b border-zinc-200 bg-white/80 backdrop-blur dark:border-zinc-800 dark:bg-zinc-950/80">
      <div className="mx-auto flex w-full max-w-4xl items-center justify-between gap-4 px-8 py-4">
        <Link
          href="/"
          className="font-semibold tracking-tight text-zinc-900 dark:text-zinc-50"
        >
          Econ Data API
        </Link>
        <nav className="flex items-center gap-4 text-sm font-medium text-zinc-600 dark:text-zinc-400">
          <Link
            href="/datasets"
            className="rounded-md px-2 py-1 hover:bg-zinc-100 hover:text-zinc-900 dark:hover:bg-zinc-900 dark:hover:text-zinc-100"
          >
            Datasets
          </Link>
          <a
            href={docsHref}
            target="_blank"
            rel="noreferrer"
            className="rounded-md px-2 py-1 hover:bg-zinc-100 hover:text-zinc-900 dark:hover:bg-zinc-900 dark:hover:text-zinc-100"
          >
            API docs
          </a>
        </nav>
      </div>
    </header>
  );
}
