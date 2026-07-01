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
    if (!dataset) {
      setPreview(null);
      setError(null);
      return;
    }

    setPreview(null);
    setError(null);

    previewDataset(dataset.id)
      .then(setPreview)
      .catch((err) => setError(err instanceof Error ? err.message : "Erro ao carregar pré-visualização"));
  }, [dataset]);

  if (!dataset) {
    return (
      <section className="section-block full-width-card" id="pre-visualizacao">
        <h2>Pré-visualização da Base</h2>
        <p className="hint">
          Selecione uma base pré-processada para conferir as primeiras linhas antes de executar a mineração de dados.
        </p>
      </section>
    );
  }

  return (
    <section className="section-block full-width-card" id="pre-visualizacao">
      <h2>Pré-visualização da Base</h2>

      <div className="dataset-summary">
        <strong>{dataset.filename}</strong>
        <span>{dataset.rows} linhas</span>
        <span>{dataset.columns.length} colunas</span>
      </div>

      <p className="hint">
        Confira se o cabeçalho, os valores e a separação das colunas foram interpretados corretamente.
      </p>

      {error && <p className="feedback-message error">{error}</p>}
      {!preview && !error && <p className="feedback-message">Carregando pré-visualização...</p>}

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
