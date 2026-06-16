import { useEffect, useState } from "react";
import { listDatasets } from "./api/client";
import { AnalysisPanel } from "./components/AnalysisPanel";
import { DatasetPreview } from "./components/DatasetPreview";
import { FileUpload } from "./components/FileUpload";
import { ResultViewer } from "./components/ResultViewer";
import type { AnalysisResult, Dataset } from "./types";
import "./styles.css";

export default function App() {
  const [datasets, setDatasets] = useState<Dataset[]>([]);
  const [selectedDataset, setSelectedDataset] = useState<Dataset | null>(null);
  const [result, setResult] = useState<AnalysisResult | null>(null);

  useEffect(() => {
    listDatasets().then(setDatasets).catch(() => setDatasets([]));
  }, []);

  function handleUploaded(dataset: Dataset) {
    setDatasets((current) => [dataset, ...current.filter((item) => item.id !== dataset.id)]);
    setSelectedDataset(dataset);
    setResult(null);
  }

  function selectDataset(id: string) {
    const dataset = datasets.find((item) => item.id === id) ?? null;
    setSelectedDataset(dataset);
    setResult(null);
  }

  return (
    <div className="app-shell">
      <nav className="top-nav" aria-label="Navegação principal">
        <a href="#preprocessamento">Pré-processamento</a>
        <a href="#mineracao">Mineração</a>
        <a href="#resultados">Resultados</a>
      </nav>

      <main className="container">
        <header className="page-header">
          <h1>Sistema de Mineração de Dados Educacionais</h1>
          <p>
            Envie bases CSV, visualize a prévia dos dados e execute estatística,
            clusterização, detecção de anomalias e regras de associação.
          </p>
        </header>

        <div className="main-sections-wrapper">
          <section className="section-block" id="preprocessamento">
            <FileUpload onUploaded={handleUploaded} />

            {datasets.length > 0 && (
              <div className="form-group dataset-selector">
                <label htmlFor="dataset-select" className="custom-label">Base carregada</label>
                <select
                  id="dataset-select"
                  value={selectedDataset?.id ?? ""}
                  onChange={(event) => selectDataset(event.target.value)}
                >
                  <option value="">Selecione uma base</option>
                  {datasets.map((dataset) => (
                    <option key={dataset.id} value={dataset.id}>
                      {dataset.filename} - {dataset.rows} linhas
                    </option>
                  ))}
                </select>
              </div>
            )}
          </section>

          <section className="section-block" id="mineracao">
            <AnalysisPanel dataset={selectedDataset} onResult={setResult} />
          </section>
        </div>

        <DatasetPreview dataset={selectedDataset} />
        <ResultViewer result={result} />
      </main>

      <footer>
      </footer>
    </div>
  );
}
