/** JSON payloads returned by `/datasets*` endpoints. */

export type DatasetSummary = {
  id: string;
  display_name: string;
  unit: string;
  row_count: number | null;
  earliest_period: string | null;
  latest_period: string | null;
  current_release_date: string | null;
};

export type ObservationColumn = {
  name: string;
  logical_type: string;
  nullable: boolean;
  description: string;
};

export type DatasetDetail = DatasetSummary & {
  description: string;
  observation_columns: ObservationColumn[];
};
