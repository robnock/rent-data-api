import type { ReactNode } from "react";

export const dynamic = "force-dynamic";

export default function DatasetsLayout({
  children,
}: Readonly<{
  children: ReactNode;
}>) {
  return (
    <div className="mx-auto w-full max-w-4xl flex-1 px-8 py-12">{children}</div>
  );
}
