import type { AnalysisResult, Dataset, DatasetPreview } from "../types";

const API_BASE_URL = import.meta.env.VITE_API_BASE_URL ?? "http://localhost:8000/api";

async function request<T>(path: string, options?: RequestInit): Promise<T> {
  const response = await fetch(`${API_BASE_URL}${path}`, options);
  if (!response.ok) {
    const error = await response.json().catch(() => ({ detail: "Erro desconhecido" }));
    throw new Error(error.detail ?? "Erro na requisição");
  }
  return response.json();
}

export async function uploadDataset(file: File): Promise<Dataset> {
  const form = new FormData();
  form.append("file", file);
  return request<Dataset>("/datasets/upload", { method: "POST", body: form });
}

export async function listDatasets(): Promise<Dataset[]> {
  return request<Dataset[]>("/datasets");
}

export async function previewDataset(datasetId: string): Promise<DatasetPreview> {
  return request<DatasetPreview>(`/datasets/${datasetId}/preview?limit=10`);
}

export async function runStatistics(datasetId: string): Promise<AnalysisResult> {
  return request<AnalysisResult>("/analysis/statistics", {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ dataset_id: datasetId }),
  });
}

export async function runKMeans(datasetId: string, columns: string[], nClusters: number): Promise<AnalysisResult> {
  return request<AnalysisResult>("/analysis/clustering/kmeans", {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ dataset_id: datasetId, columns, n_clusters: nClusters }),
  });
}

export async function runDBSCAN(datasetId: string, columns: string[], eps: number, minSamples: number): Promise<AnalysisResult> {
  return request<AnalysisResult>("/analysis/clustering/dbscan", {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ dataset_id: datasetId, columns, eps, min_samples: minSamples }),
  });
}

export async function runIsolationForest(datasetId: string, columns: string[], contamination: number): Promise<AnalysisResult> {
  return request<AnalysisResult>("/analysis/anomalies/isolation-forest", {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ dataset_id: datasetId, columns, contamination }),
  });
}

export async function runAssociationRules(datasetId: string, columns: string[], minSupport: number, minConfidence: number): Promise<AnalysisResult> {
  return request<AnalysisResult>("/analysis/association-rules", {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ dataset_id: datasetId, columns, min_support: minSupport, min_confidence: minConfidence }),
  });
}
