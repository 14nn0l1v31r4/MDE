import { useEffect, useState } from "react";
import { listDatasets } from "./api/client";
import { AnalysisPanel } from "./components/AnalysisPanel";
import { DatasetPreview } from "./components/DatasetPreview";
import { FileUpload } from "./components/FileUpload";
import { ResultViewer } from "./components/ResultViewer";
import { Sidebar } from "./components/Sidebar";
import { UserGuide } from "./components/UserGuide";
import type { AnalysisResult, Dataset } from "./types";
import "./styles.css";

type AppPage = "home" | "guide";

export default function App() {
  const [datasets, setDatasets] = useState<Dataset[]>([]);
  const [selectedDataset, setSelectedDataset] = useState<Dataset | null>(null);
  const [result, setResult] = useState<AnalysisResult | null>(null);
  const [currentPage, setCurrentPage] = useState<AppPage>("home");

  useEffect(() => {
    listDatasets().then(setDatasets).catch(() => setDatasets([]));
  }, []);

  function scrollToSection(sectionId: string) {
    window.setTimeout(() => {
      document.getElementById(sectionId)?.scrollIntoView({
        behavior: "smooth",
        block: "start",
      });
    }, 100);
  }

  function handleNavigate(sectionId: string) {
    setCurrentPage("home");
    scrollToSection(sectionId);
  }

  function handleOpenGuide() {
    setCurrentPage("guide");

    window.setTimeout(() => {
      window.scrollTo({
        top: 0,
        behavior: "smooth",
      });
    }, 80);
  }

  function handleUploaded(dataset: Dataset) {
    setDatasets((current) => [
      dataset,
      ...current.filter((item) => item.id !== dataset.id),
    ]);

    setSelectedDataset(dataset);
    setResult(null);
    setCurrentPage("home");
    scrollToSection("bases-pre-processadas");
  }

  function selectDataset(id: string) {
    const dataset = datasets.find((item) => item.id === id) ?? null;

    setSelectedDataset(dataset);
    setResult(null);

    if (dataset) {
      setCurrentPage("home");
      scrollToSection("pre-visualizacao");
    }
  }

  return (
    <div className="app-shell">
      <Sidebar
        currentPage={currentPage}
        onNavigate={handleNavigate}
        onOpenGuide={handleOpenGuide}
      />

      <div className="app-content">
        <main className="container">
          {currentPage === "guide" ? (
            <UserGuide />
          ) : (
            <>
              <header className="page-header" id="inicio">
                

                <h1>Sistema de Mineração de Dados Educacionais</h1>

                <p>
                  Envie bases CSV, confira as bases pré-processadas, visualize
                  os dados antes da mineração e execute estatística,
                  clusterização, detecção de anomalias e regras de associação.
                </p>
              </header>

              <section className="section-block" id="preprocessamento">
                <FileUpload onUploaded={handleUploaded} />
              </section>

              <section
                className="section-block full-width-card"
                id="bases-pre-processadas"
              >
                <div className="section-title-row">
                  <div>
                    <h2>Bases Pré-Processadas</h2>

                    <p className="hint">
                      Selecione uma base já importada para visualizar seus dados
                      e liberar as opções de mineração.
                    </p>
                  </div>
                </div>

                {datasets.length > 0 ? (
                  <div className="form-group dataset-selector">
                    <label htmlFor="dataset-select" className="custom-label">
                      Base disponível para análise
                    </label>

                    <select
                      id="dataset-select"
                      value={selectedDataset?.id ?? ""}
                      onChange={(event) => selectDataset(event.target.value)}
                    >
                      <option value="">Selecione uma base</option>

                      {datasets.map((dataset) => (
                        <option key={dataset.id} value={dataset.id}>
                          {dataset.filename} - {dataset.rows} linhas -{" "}
                          {dataset.columns.length} colunas
                        </option>
                      ))}
                    </select>

                    {selectedDataset && (
                      <div className="dataset-summary dataset-summary-spaced">
                        <strong>{selectedDataset.filename}</strong>
                        <span>{selectedDataset.rows} linhas</span>
                        <span>{selectedDataset.columns.length} colunas</span>
                        <span>Pronta para pré-visualização e mineração</span>
                      </div>
                    )}
                  </div>
                ) : (
                  <p className="feedback-message">
                    Nenhuma base pré-processada encontrada. Envie um arquivo CSV
                    na seção de pré-processamento.
                  </p>
                )}
              </section>

              <DatasetPreview dataset={selectedDataset} />

              <section className="section-block full-width-card" id="mineracao">
                <AnalysisPanel dataset={selectedDataset} onResult={setResult} />
              </section>

              <ResultViewer result={result} />
            </>
          )}
        </main>

        <footer>
          <p>Plataforma de Mineração de Dados Educacionais.</p>
        </footer>
      </div>
    </div>
  );
}