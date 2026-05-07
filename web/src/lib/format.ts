export function formatIsoDate(iso: string | null | undefined): string {
  if (!iso) {
    return "—";
  }

  const d = new Date(`${iso}T00:00:00Z`);
  if (Number.isNaN(+d)) {
    return iso;
  }

  return new Intl.DateTimeFormat(undefined, {
    year: "numeric",
    month: "short",
    day: "numeric",
    timeZone: "UTC",
  }).format(d);
}
