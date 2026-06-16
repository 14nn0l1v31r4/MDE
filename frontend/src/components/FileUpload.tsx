import { useState } from "react";
import { uploadDataset } from "../api/client";
import type { Dataset } from "../types";

type Props = {
  onUploaded: (dataset: Dataset) => void;
};

export function FileUpload({ onUploaded }: Props) {
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [fileName, setFileName] = useState<string>("Nenhum arquivo selecionado");

  async function handleSubmit(event: React.FormEvent<HTMLFormElement>) {
    event.preventDefault();
    const form = new FormData(event.currentTarget);
    const file = form.get("file");
    if (!(file instanceof File)) return;

    setLoading(true);
    setError(null);
    try {
      const dataset = await uploadDataset(file);
      onUploaded(dataset);
      event.currentTarget.reset();
      setFileName("Nenhum arquivo selecionado");
    } catch (err) {
      setError(err instanceof Error ? err.message : "Erro ao enviar arquivo");
    } finally {
      setLoading(false);
    }
  }

  return (
    <div>
      <h2>Pré-processamento dos dados</h2>
      <p className="hint">Envie uma base CSV para armazenar no PostgreSQL e liberar as análises.</p>

      <form onSubmit={handleSubmit}>
        <div className="form-group">
          <label htmlFor="file" className="custom-label">Selecionar arquivo CSV</label>
          <input
            id="file"
            name="file"
            type="file"
            accept=".csv"
            className="inputfile"
            required
            onChange={(event) => setFileName(event.target.files?.[0]?.name ?? "Nenhum arquivo selecionado")}
          />
          <label htmlFor="file" className="file-upload-button">Escolher arquivo</label>
          <span className="selected-file-name">{fileName}</span>
        </div>

        <button type="submit" disabled={loading}>{loading ? "Enviando..." : "Enviar arquivo"}</button>
      </form>
      {error && <p className="feedback-message error">{error}</p>}
    </div>
  );
}
