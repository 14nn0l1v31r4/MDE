import { useEffect, useState } from "react";
import {
  runAssociationRules,
  runDBSCAN,
  runIsolationForest,
  runKMeans,
  runStatistics,
} from "../api/client";
import type { AnalysisResult, Dataset } from "../types";
import { ColumnSelector } from "./ColumnSelector";

type Props = {
  dataset: Dataset | null;
  onResult: (result: AnalysisResult) => void;
};

export function AnalysisPanel({ dataset, onResult }: Props) {
  const [selectedColumns, setSelectedColumns] = useState<string[]>([]);
  const [loading, setLoading] = useState<string | null>(null);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    setSelectedColumns([]);
    setError(null);
  }, [dataset?.id]);

  function scrollToResults() {
    window.setTimeout(() => {
      document.getElementById("resultados")?.scrollIntoView({
        behavior: "smooth",
        block: "start",
      });
    }, 120);
  }

  async function execute(label: string, fn: () => Promise<AnalysisResult>) {
    setLoading(label);
    setError(null);

    try {
      const result = await fn();
      onResult(result);
      scrollToResults();
    } catch (err) {
      setError(err instanceof Error ? err.message : "Erro ao executar análise");
    } finally {
      setLoading(null);
    }
  }

  return (
    <div>
      <h2>Mineração de Dados</h2>
      <p className="hint">
        Execute as técnicas de análise somente depois de conferir a pré-visualização da base.
      </p>

      {!dataset && (
        <p className="feedback-message">
          Selecione ou envie uma base CSV para habilitar as análises.
        </p>
      )}

      {dataset && (
        <>
          <div className="dataset-summary">
            <strong>{dataset.filename}</strong>
            <span>{dataset.rows} linhas</span>
            <span>{dataset.columns.length} colunas</span>
          </div>

          <ColumnSelector dataset={dataset} selectedColumns={selectedColumns} onChange={setSelectedColumns} />

          <div className="actions-grid">
            <button type="button" onClick={() => execute("Estatística", () => runStatistics(dataset.id))}>
              Análise Estatística
            </button>

            <button
              type="button"
              className="btn-danger"
              onClick={() => execute("KMeans", () => runKMeans(dataset.id, selectedColumns, 3))}
            >
              Clusterização KMeans
            </button>

            <button
              type="button"
              className="btn-danger"
              onClick={() => execute("DBSCAN", () => runDBSCAN(dataset.id, selectedColumns, 1.5, 5))}
            >
              Clusterização DBSCAN
            </button>

            <button
              type="button"
              onClick={() => execute("Isolation Forest", () => runIsolationForest(dataset.id, selectedColumns, 0.05))}
            >
              Isolation Forest
            </button>

            <button
              type="button"
              onClick={() => execute("Regras", () => runAssociationRules(dataset.id, selectedColumns, 0.2, 0.6))}
            >
              Regras de Associação
            </button>
          </div>

          {loading && <p className="feedback-message">Executando: {loading}...</p>}
          {error && <p className="feedback-message error">{error}</p>}

          <p className="hint">
            Para clusterização e anomalias, selecione colunas relevantes para comparação entre registros.
            Para regras de associação, prefira colunas categóricas.
          </p>
        </>
      )}
    </div>
  );
}
