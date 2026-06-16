export type Dataset = {
  id: string;
  filename: string;
  rows: number;
  columns: string[];
  created_at: string;
};

export type DatasetPreview = {
  dataset_id: string;
  columns: string[];
  rows: Record<string, unknown>[];
};

export type AnalysisResult = {
  id: string;
  dataset_id: string;
  analysis_type: string;
  payload: Record<string, unknown>;
};
