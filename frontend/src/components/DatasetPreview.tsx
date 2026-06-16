import { useEffect, useState } from "react";
import { previewDataset } from "../api/client";
import type { Dataset, DatasetPreview as Preview } from "../types";

type Props = {
  dataset: Dataset | null;
};

export function DatasetPreview({ dataset }: Props) {
  const [preview, setPreview] = useState<Preview | null>(null);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    if (!dataset) return;
    setPreview(null);
    setError(null);
    previewDataset(dataset.id)
      .then(setPreview)
      .catch((err) => setError(err instanceof Error ? err.message : "Erro ao carregar prévia"));
  }, [dataset]);

  if (!dataset) return null;

  return (
    <section className="section-block full-width-card">
      <h2>Prévia da base</h2>
      <p><strong>Arquivo:</strong> {dataset.filename}</p>
      <p><strong>Linhas:</strong> {dataset.rows} | <strong>Colunas:</strong> {dataset.columns.length}</p>
      {error && <p className="feedback-message error">{error}</p>}
      {preview && (
        <div className="tabela-container">
          <table className="table-metrics">
            <thead>
              <tr>{preview.columns.map((column) => <th key={column}>{column}</th>)}</tr>
            </thead>
            <tbody>
              {preview.rows.map((row, index) => (
                <tr key={index}>
                  {preview.columns.map((column) => <td key={column}>{String(row[column] ?? "")}</td>)}
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      )}
    </section>
  );
}
