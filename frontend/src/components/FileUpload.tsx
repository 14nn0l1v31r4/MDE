import { useState, type FormEvent } from "react";
import { uploadDataset } from "../api/client";
import type { Dataset } from "../types";

type Props = {
  onUploaded: (dataset: Dataset) => void;
};

type TemplateColumn = {
  name: string;
  table: string;
  type: string;
  required: "Sim" | "Não";
  example: string;
};

const TEMPLATE_COLUMNS: TemplateColumn[] = [
  { name: "unidade", table: "registros_educacionais", type: "Texto", required: "Não", example: "IFF Campos Centro" },
  { name: "curso", table: "registros_educacionais", type: "Texto", required: "Não", example: "Sistemas de Informação" },
  { name: "grande_area_do_curso", table: "registros_educacionais", type: "Categoria", required: "Não", example: "Ciências Exatas e da Terra" },
  { name: "turno", table: "registros_educacionais", type: "Categoria", required: "Não", example: "Noturno" },
  { name: "semestre", table: "registros_educacionais", type: "Categoria/Número", required: "Não", example: "2024.1" },
  { name: "sexo", table: "registros_educacionais", type: "Categoria", required: "Não", example: "Feminino" },
  { name: "faixa_etaria", table: "registros_educacionais", type: "Categoria", required: "Não", example: "18 a 24 anos" },
  { name: "cor_ou_raca", table: "registros_educacionais", type: "Categoria", required: "Não", example: "Parda" },
  { name: "estado_civil", table: "registros_educacionais", type: "Categoria", required: "Não", example: "Solteiro(a)" },
  { name: "uf_candidato", table: "registros_educacionais", type: "UF", required: "Não", example: "RJ" },
  { name: "cidade_candidato", table: "registros_educacionais", type: "Texto", required: "Não", example: "Campos dos Goytacazes" },
  { name: "tipo_vaga", table: "registros_educacionais", type: "Categoria", required: "Não", example: "Ampla concorrência" },
  { name: "forma_de_ingresso", table: "registros_educacionais", type: "Categoria", required: "Não", example: "SISU" },
  { name: "periodo_fundamental", table: "registros_educacionais", type: "Categoria", required: "Não", example: "Todo em escola pública" },
  { name: "escola_publica", table: "registros_educacionais", type: "Categoria", required: "Não", example: "Sim" },
  { name: "renda_mensal_familia", table: "registros_educacionais", type: "Categoria/Número", required: "Não", example: "1 a 2 salários mínimos" },
  { name: "atividade_remunerada", table: "registros_educacionais", type: "Categoria", required: "Não", example: "Não" },
  { name: "participacao_economia_familia", table: "registros_educacionais", type: "Categoria", required: "Não", example: "Não participa" },
  { name: "situacao_superior", table: "registros_educacionais", type: "Categoria", required: "Não", example: "Não possui" },
];

function buildTemplateCsv(): string {
  const header = TEMPLATE_COLUMNS.map((column) => column.name).join(",");
  const example = TEMPLATE_COLUMNS.map((column) => column.example).join(",");
  return `${header}\n${example}\n`;
}

function downloadTemplateCsv() {
  const csv = `\uFEFF${buildTemplateCsv()}`;
  const blob = new Blob([csv], { type: "text/csv;charset=utf-8" });
  const url = URL.createObjectURL(blob);
  const link = document.createElement("a");

  link.href = url;
  link.download = "modelo_base_educacional.csv";
  link.click();

  URL.revokeObjectURL(url);
}

export function FileUpload({ onUploaded }: Props) {
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [fileName, setFileName] = useState<string>("Nenhum arquivo selecionado");

  async function handleSubmit(event: FormEvent<HTMLFormElement>) {
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
      <p className="hint">
        Envie uma base CSV para armazenar e disponibilizar a base como pré-processada.
      </p>

      <div className="template-card">
        <div className="template-header">
          <div>
            <h3>Template do arquivo importado</h3>
            <p className="hint">
              O arquivo deve ser uma tabela única em CSV, com cabeçalho na primeira linha.
              As colunas abaixo são recomendadas para reproduzir os gráficos e análises da plataforma.
            </p>
          </div>

          <button type="button" className="btn-outline" onClick={downloadTemplateCsv}>
            Baixar modelo CSV
          </button>
        </div>

        <div className="template-summary-grid">
          <div>
            <span>Tabela esperada</span>
            <strong>registros_educacionais</strong>
          </div>
          <div>
            <span>Formato</span>
            <strong>CSV UTF-8</strong>
          </div>
          <div>
            <span>Separador sugerido</span>
            <strong>Vírgula (,)</strong>
          </div>
        </div>

        <details className="template-details">
          <summary>Ver tabelas e colunas esperadas</summary>

          <div className="tabela-container template-table">
            <table>
              <thead>
                <tr>
                  <th>Tabela</th>
                  <th>Coluna</th>
                  <th>Tipo esperado</th>
                  <th>Exemplo</th>
                </tr>
              </thead>
              <tbody>
                {TEMPLATE_COLUMNS.map((column) => (
                  <tr key={column.name}>
                    <td>{column.table}</td>
                    <td>{column.name}</td>
                    <td>{column.type}</td>
                    <td>{column.example}</td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        </details>
      </div>

      <form onSubmit={handleSubmit}>
        <div className="form-group">
          <label htmlFor="file" className="custom-label">
            Selecionar arquivo CSV
          </label>

          <input
            id="file"
            name="file"
            type="file"
            accept=".csv"
            className="inputfile"
            required
            onChange={(event) => setFileName(event.target.files?.[0]?.name ?? "Nenhum arquivo selecionado")}
          />

          <label htmlFor="file" className="file-upload-button">
            Escolher arquivo
          </label>

          <span className="selected-file-name">{fileName}</span>
        </div>

        <button type="submit" disabled={loading}>
          {loading ? "Enviando..." : "Enviar arquivo"}
        </button>
      </form>

      {error && <p className="feedback-message error">{error}</p>}
    </div>
  );
}
