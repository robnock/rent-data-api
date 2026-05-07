"""Authoritative metric catalog shared by ingest + API.

Observation CSV convention (every metric file):

- Columns: ``location_fips_code``, ``period``, ``value``, ``date_updated_at``
  (same shapes as ``rent_growth_yoy.csv``).
- Stable filenames ``{dataset_id}.csv`` in ``data/`` (release date stays in-file).
"""

from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class MetricCatalogEntry:
    dataset_id: str
    display_name: str
    description: str
    unit: str
    value_description: str

    def csv_filename(self) -> str:
        return f"{self.dataset_id}.csv"


METRICS: tuple[MetricCatalogEntry, ...] = (
    MetricCatalogEntry(
        dataset_id="rent_growth_yoy",
        display_name="Rent growth (year-over-year)",
        description=(
            "Year-over-year change in rents by geography and calendar month "
            "(decimal fraction)."
        ),
        unit="YoY change (decimal)",
        value_description=(
            "Year-over-year rent change as a decimal fraction (for example 0.05 ≈ "
            "+5%)."
        ),
    ),
    MetricCatalogEntry(
        dataset_id="rent_growth_mom",
        display_name="Rent growth (month-over-month)",
        description=(
            "Month-over-month change in rents by geography and calendar month "
            "(decimal fraction)."
        ),
        unit="MoM change (decimal)",
        value_description=(
            "Month-over-month rent change as a decimal fraction (for example 0.01 ≈ "
            "+1%)."
        ),
    ),
    MetricCatalogEntry(
        dataset_id="median_rent",
        display_name="Median rent",
        description=(
            "Estimated median contract rent by geography and month (model-output "
            "level, nominal units from source extract)."
        ),
        unit="USD (nominal median)",
        value_description=(
            "Median rent level encoded as the raw numeric estimate from the published "
            "extract (decimals allowed)."
        ),
    ),
    MetricCatalogEntry(
        dataset_id="vacancy_rate",
        display_name="Vacancy rate",
        description=(
            "Estimated rental vacancy rate by geography and month (fraction of "
            "inventory vacant)."
        ),
        unit="Share (decimal)",
        value_description=(
            "Vacant share of rental inventory encoded as a decimal fraction between "
            "0 and 1."
        ),
    ),
    MetricCatalogEntry(
        dataset_id="rent_index",
        display_name="Rent index",
        description=(
            "Seasonally-adjusted rent index benchmarked to January 2017 = 100, by "
            "geography and month."
        ),
        unit="Index (Jan 2017 = 100)",
        value_description="Index level; compare across months within a location.",
    ),
)

METRICS_BY_ID: dict[str, MetricCatalogEntry] = {
    row.dataset_id: row for row in METRICS
}

EXPECTED_METRIC_CSV_FILENAMES: frozenset[str] = frozenset(
    m.csv_filename() for m in METRICS
)


def allowed_data_csv_filenames() -> frozenset[str]:
    return EXPECTED_METRIC_CSV_FILENAMES | frozenset({"locations.csv"})
