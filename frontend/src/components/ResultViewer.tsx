import type { CSSProperties } from "react";
import type { AnalysisResult } from "../types";

import { downloadChartAsPng, downloadAllChartsAsZip } from "../utils/ChartExport";

function getAnalysisTitle(analysisType: string): string {
  const titles: Record<string, string> = {
    statistics: "Análise Estatística",
    kmeans: "Clusterização KMeans",
    dbscan: "Clusterização DBSCAN",
    isolation_forest: "Detecção de Anomalias",
    association_rules: "Regras de Associação",
  };

  return titles[analysisType] ?? analysisType;
}

type MetricCard = {
  label: string;
  value: string | number;
  hint?: string;
};

type ChartDatum = {
  label: string;
  value: number;
  count?: number;
  percentage?: number;
};

type NotebookChartValue = {
  label: string;
  count?: number;
  percentage?: number;
};

type NotebookChart = {
  id?: string;
  kind?: string;
  title?: string;
  column?: string;
  value_mode?: string;
  values?: NotebookChartValue[];
};

type NotebookCrosstab = {
  id?: string;
  title?: string;
  index?: string;
  columns_label?: string;
  columns?: string[];
  rows?: Array<{ label: string; values: Record<string, number> }>;
  unit?: string;
};

type ClusterProfile = {
  column?: string;
  type?: string;
  title?: string;
  values?: Array<{ cluster: string; label: string; value: number; metric?: string }>;
};

type RuleRow = {
  antecedents?: unknown;
  consequents?: unknown;
  support?: unknown;
  confidence?: unknown;
  lift?: unknown;
};

type PreviewRow = Record<string, unknown>;

type Props = {
  result: AnalysisResult | null;
};

const chartPalette = [
  "#006633",
  "#cc0000",
  "#0f766e",
  "#64748b",
  "#16a34a",
  "#b91c1c",
  "#15803d",
  "#475569",
  "#22c55e",
  "#ef4444",
  "#0d9488",
  "#94a3b8",
];
function slugifyChartId(value: string): string {
  return value
    .normalize("NFD")
    .replace(/[\u0300-\u036f]/g, "")
    .replace(/[^a-zA-Z0-9-_ ]/g, "")
    .trim()
    .replace(/\s+/g, "-")
    .toLowerCase();
}

function getChartElementId(title: string): string {
  return `chart-${slugifyChartId(title)}`;
}

async function handleDownloadChart(elementId: string, title: string) {
  try {
    await downloadChartAsPng(elementId, title);
  } catch (error) {
    alert(error instanceof Error ? error.message : "Erro ao baixar gráfico.");
  }
}

async function handleDownloadAllCharts() {
  try {
    await downloadAllChartsAsZip();
  } catch (error) {
    alert(error instanceof Error ? error.message : "Erro ao baixar gráficos.");
  }
}

function asRecord(value: unknown): Record<string, unknown> {
  return value && typeof value === "object" && !Array.isArray(value) ? value as Record<string, unknown> : {};
}

function asNumber(value: unknown): number | null {
  if (typeof value === "number" && Number.isFinite(value)) return value;
  if (typeof value === "string" && value.trim() !== "") {
    const parsed = Number(value);
    return Number.isFinite(parsed) ? parsed : null;
  }
  return null;
}

function asArray(value: unknown): unknown[] {
  return Array.isArray(value) ? value : [];
}

function formatNumber(value: unknown, decimals = 2): string {
  const numeric = asNumber(value);
  if (numeric === null) return "-";
  return numeric.toLocaleString("pt-BR", { maximumFractionDigits: decimals });
}

function formatPercent(value: unknown): string {
  const numeric = asNumber(value);
  if (numeric === null) return "-";
  return `${numeric.toLocaleString("pt-BR", { maximumFractionDigits: 1 })}%`;
}

function formatRatioAsPercent(value: unknown): string {
  const numeric = asNumber(value);
  if (numeric === null) return "-";
  return `${(numeric * 100).toLocaleString("pt-BR", { maximumFractionDigits: 1 })}%`;
}

function objectToChartData(value: unknown, limit = 12): ChartDatum[] {
  const record = asRecord(value);
  return Object.entries(record)
    .map(([label, raw]) => ({ label, value: asNumber(raw) ?? 0 }))
    .filter((item) => Number.isFinite(item.value))
    .sort((a, b) => b.value - a.value)
    .slice(0, limit);
}

function numericMeanData(numericSummary: unknown, limit = 12): ChartDatum[] {
  const summary = asRecord(numericSummary);
  return Object.entries(summary)
    .map(([column, stats]) => {
      const mean = asNumber(asRecord(stats).mean);
      return mean === null ? null : { label: column, value: mean };
    })
    .filter((item): item is ChartDatum => item !== null)
    .sort((a, b) => Math.abs(b.value) - Math.abs(a.value))
    .slice(0, limit);
}

function previewRows(value: unknown): PreviewRow[] {
  return asArray(value).filter((item): item is PreviewRow => typeof item === "object" && item !== null && !Array.isArray(item)).slice(0, 30);
}

function firstCategoricalSummaries(value: unknown): Array<{ column: string; data: ChartDatum[] }> {
  const summary = asRecord(value);
  return Object.entries(summary)
    .map(([column, counts]) => ({ column, data: objectToChartData(counts, 8) }))
    .filter((item) => item.data.length > 0)
    .slice(0, 3);
}

function normalizeList(value: unknown): string {
  if (Array.isArray(value)) return value.map(String).join(" + ");
  return String(value ?? "-");
}

function notebookChartData(chart: NotebookChart): ChartDatum[] {
  return (chart.values ?? [])
    .map((item) => ({
      label: String(item.label),
      value: chart.value_mode === "percentage" ? Number(item.percentage ?? 0) : Number(item.count ?? item.percentage ?? 0),
      count: Number(item.count ?? 0),
      percentage: Number(item.percentage ?? 0),
    }))
    .filter((item) => Number.isFinite(item.value));
}

function MetricGrid({ cards }: { cards: MetricCard[] }) {
  return (
    <div className="metric-grid">
      {cards.map((card) => (
        <div className="metric-card" key={card.label}>
          <span>{card.label}</span>
          <strong>{card.value}</strong>
          {card.hint && <small>{card.hint}</small>}
        </div>
      ))}
    </div>
  );
}

function BarChart({
  title,
  data,
  valueSuffix = "",
  showCount = false,
}: {
  title: string;
  data: ChartDatum[];
  valueSuffix?: string;
  showCount?: boolean;
}) {
  if (data.length === 0) return null;

  const max = Math.max(...data.map((item) => Math.abs(item.value)), 1);
  const chartId = getChartElementId(title);

  return (
    <div className="chart-card-wrapper">
      <div
        id={chartId}
        className="chart-card"
        data-chart-export="true"
        data-chart-title={title}
      >
        <h3>{title}</h3>

        <div className="bar-chart" role="img" aria-label={title}>
          {data.map((item) => {
            const width = Math.max((Math.abs(item.value) / max) * 100, 2);

            return (
              <div className="bar-row" key={item.label}>
                <span className="bar-label" title={item.label}>
                  {item.label}
                </span>

                <div className="bar-track">
                  <div className="bar-fill" style={{ width: `${width}%` }} />
                </div>

                <strong>
                  {formatNumber(item.value)}
                  {valueSuffix}
                  {showCount && item.count !== undefined ? (
                    <small> ({formatNumber(item.count, 0)})</small>
                  ) : null}
                </strong>
              </div>
            );
          })}
        </div>
      </div>

      <button
        type="button"
        className="btn-outline chart-download-button"
        onClick={() => handleDownloadChart(chartId, title)}
      >
        Baixar gráfico
      </button>
    </div>
  );
}

function PieChart({ title, data }: { title: string; data: ChartDatum[] }) {
  if (data.length === 0) return null;

  const total = data.reduce(
    (sum, item) => sum + Math.max(item.count ?? item.value, 0),
    0
  );

  let cursor = 0;

  const gradient = data
    .map((item, index) => {
      const raw = Math.max(item.count ?? item.value, 0);
      const start = cursor;
      const end = total > 0 ? cursor + (raw / total) * 360 : cursor;
      cursor = end;

      return `${chartPalette[index % chartPalette.length]} ${start}deg ${end}deg`;
    })
    .join(", ");

  const chartId = getChartElementId(title);

  return (
    <div className="chart-card-wrapper">
      <div
        id={chartId}
        className="chart-card pie-card"
        data-chart-export="true"
        data-chart-title={title}
      >
        <h3>{title}</h3>

        <div className="pie-layout">
          <div
            className="pie-visual"
            style={{ background: `conic-gradient(${gradient})` }}
            role="img"
            aria-label={title}
          />

          <div className="pie-legend">
            {data.map((item, index) => (
              <div className="pie-legend-row" key={item.label}>
                <span
                  className="legend-dot"
                  style={
                    {
                      "--slice-color":
                        chartPalette[index % chartPalette.length],
                    } as CSSProperties
                  }
                />

                <span title={item.label}>{item.label}</span>

                <strong>{formatPercent(item.percentage ?? item.value)}</strong>

                {item.count !== undefined ? (
                  <small>{formatNumber(item.count, 0)} registros</small>
                ) : null}
              </div>
            ))}
          </div>
        </div>
      </div>

      <button
        type="button"
        className="btn-outline chart-download-button"
        onClick={() => handleDownloadChart(chartId, title)}
      >
        Baixar gráfico
      </button>
    </div>
  );
}

function LineChart({
  title,
  data,
}: {
  title: string;
  data: Array<{ label: string; value: number }>;
}) {
  if (data.length === 0) return null;

  const width = 560;
  const height = 260;
  const padding = 34;
  const values = data.map((item) => item.value);
  const min = Math.min(...values);
  const max = Math.max(...values);
  const range = max - min || 1;
  const step = data.length > 1 ? (width - padding * 2) / (data.length - 1) : 0;

  const points = data.map((item, index) => {
    const x = padding + index * step;
    const y =
      height -
      padding -
      ((item.value - min) / range) * (height - padding * 2);

    return { ...item, x, y };
  });

  const polyline = points.map((point) => `${point.x},${point.y}`).join(" ");
  const chartId = getChartElementId(title);

  return (
    <div className="chart-card-wrapper">
      <div
        id={chartId}
        className="chart-card line-card"
        data-chart-export="true"
        data-chart-title={title}
      >
        <h3>{title}</h3>

        <svg
          viewBox={`0 0 ${width} ${height}`}
          className="line-chart"
          role="img"
          aria-label={title}
        >
          <line
            x1={padding}
            y1={height - padding}
            x2={width - padding}
            y2={height - padding}
            className="axis-line"
          />

          <line
            x1={padding}
            y1={padding}
            x2={padding}
            y2={height - padding}
            className="axis-line"
          />

          <polyline points={polyline} className="line-path" />

          {points.map((point) => (
            <g key={point.label}>
              <circle
                cx={point.x}
                cy={point.y}
                r="4"
                className="line-point"
              />

              <text
                x={point.x}
                y={height - 8}
                textAnchor="middle"
                className="axis-label"
              >
                {point.label}
              </text>
            </g>
          ))}
        </svg>

        <div className="line-values">
          {data.map((item) => (
            <span key={item.label}>
              {item.label}: {formatNumber(item.value)}
            </span>
          ))}
        </div>
      </div>

      <button
        type="button"
        className="btn-outline chart-download-button"
        onClick={() => handleDownloadChart(chartId, title)}
      >
        Baixar gráfico
      </button>
    </div>
  );
}

function ResultTable({ rows, title }: { rows: PreviewRow[]; title: string }) {
  if (rows.length === 0) return null;
  const columns = Array.from(new Set(rows.flatMap((row) => Object.keys(row)))).slice(0, 12);

  return (
    <div className="chart-card table-card">
      <h3>{title}</h3>
      <div className="tabela-container compact-table">
        <table>
          <thead>
            <tr>{columns.map((column) => <th key={column}>{column}</th>)}</tr>
          </thead>
          <tbody>
            {rows.map((row, index) => (
              <tr key={index}>
                {columns.map((column) => <td key={column}>{String(row[column] ?? "")}</td>)}
              </tr>
            ))}
          </tbody>
        </table>
      </div>
    </div>
  );
}

function CrosstabTable({ table }: { table: NotebookCrosstab }) {
  const columns = table.columns ?? [];
  const rows = table.rows ?? [];
  if (columns.length === 0 || rows.length === 0) return null;

  return (
    <div className="chart-card table-card">
      <h3>{table.title ?? "Tabela cruzada"}</h3>
      <p className="chart-subtitle">Percentual calculado sobre o total da base, seguindo a lógica dos notebooks.</p>
      <div className="tabela-container compact-table">
        <table>
          <thead>
            <tr>
              <th>{table.index ?? "Categoria"}</th>
              {columns.map((column) => <th key={column}>{column}</th>)}
            </tr>
          </thead>
          <tbody>
            {rows.map((row) => (
              <tr key={row.label}>
                <td>{row.label}</td>
                {columns.map((column) => <td key={column}>{formatPercent(row.values?.[column] ?? 0)}</td>)}
              </tr>
            ))}
          </tbody>
        </table>
      </div>
    </div>
  );
}

function NotebookCharts({ charts, crosstabs }: { charts: NotebookChart[]; crosstabs: NotebookCrosstab[] }) {
  const pieCharts = charts.filter((chart) => chart.kind === "pie");
  const barCharts = charts.filter((chart) => chart.kind === "bar");

  if (charts.length === 0 && crosstabs.length === 0) return null;

  return (
    <div className="notebook-visualizations">
      <div className="subsection-heading">
        <p>Gráficos de análise estatística.</p>
      </div>

      <div className="charts-grid">
        {pieCharts.map((chart) => (
          <PieChart key={chart.id ?? chart.title} title={chart.title ?? "Gráfico de pizza"} data={notebookChartData(chart)} />
        ))}
        {barCharts.map((chart) => (
          <BarChart
            key={chart.id ?? chart.title}
            title={chart.title ?? "Gráfico de barras"}
            data={notebookChartData(chart)}
            valueSuffix="%"
            showCount
          />
        ))}
        {crosstabs.map((table) => <CrosstabTable key={table.id ?? table.title} table={table} />)}
      </div>
    </div>
  );
}

function ClusterProfiles({ profiles }: { profiles: ClusterProfile[] }) {
  if (profiles.length === 0) return null;
  return (
    <div className="notebook-visualizations">
      <div className="subsection-heading">
        <span>Perfil dos clusters</span>
        <p>Equivalente à leitura percentual/média por cluster que era impressa no notebook de modelagem.</p>
      </div>
      <div className="cluster-profile-grid">
        {profiles.map((profile) => {
          const values = profile.values ?? [];
          return (
            <div className="chart-card table-card" key={profile.column ?? profile.title}>
              <h3>{profile.title ?? profile.column}</h3>
              <div className="tabela-container compact-table small-table">
                <table>
                  <thead>
                    <tr>
                      <th>Cluster</th>
                      <th>Categoria / Métrica</th>
                      <th>Valor</th>
                    </tr>
                  </thead>
                  <tbody>
                    {values.map((item, index) => (
                      <tr key={`${item.cluster}-${item.label}-${index}`}>
                        <td>{item.cluster}</td>
                        <td>{item.label}</td>
                        <td>{item.metric === "percentage" ? formatPercent(item.value) : formatNumber(item.value)}</td>
                      </tr>
                    ))}
                  </tbody>
                </table>
              </div>
            </div>
          );
        })}
      </div>
    </div>
  );
}

function StatisticsResult({ payload }: { payload: Record<string, unknown> }) {
  const missingValues = objectToChartData(payload.missing_values, 12);
  const means = numericMeanData(payload.numeric_summary, 12);
  const categoricalSummaries = firstCategoricalSummaries(payload.categorical_summary);
  const notebookCharts = asArray(payload.notebook_charts).filter((item): item is NotebookChart => typeof item === "object" && item !== null);
  const crosstabs = asArray(payload.notebook_crosstabs).filter((item): item is NotebookCrosstab => typeof item === "object" && item !== null);

  return (
    <>
      <MetricGrid
        cards={[
          { label: "Linhas", value: formatNumber(payload.rows, 0) },
          { label: "Colunas", value: asArray(payload.columns).length },
          { label: "Colunas numéricas", value: Object.keys(asRecord(payload.numeric_summary)).length },
          { label: "Colunas categóricas", value: Object.keys(asRecord(payload.categorical_summary)).length },
          { label: "Gráficos do notebook", value: notebookCharts.length },
          { label: "Tabelas cruzadas", value: crosstabs.length },
        ]}
      />

      <div className="charts-grid">
        <BarChart title="Valores ausentes por coluna" data={missingValues} />
        <BarChart title="Média das principais colunas numéricas" data={means} />
        {categoricalSummaries.map((item) => (
          <BarChart key={item.column} title={`Distribuição: ${item.column}`} data={item.data} />
        ))}
      </div>

      <NotebookCharts charts={notebookCharts} crosstabs={crosstabs} />
    </>
  );
}

function ClusteringResult({ payload }: { payload: Record<string, unknown> }) {
  const clusterCounts = objectToChartData(payload.cluster_counts, 20).sort((a, b) => a.label.localeCompare(b.label));
  const clusterPercentagesRecord = asRecord(payload.cluster_percentages);
  const clusterPieData = clusterCounts.map((item) => ({
    ...item,
    count: item.value,
    percentage: asNumber(clusterPercentagesRecord[item.label]) ?? 0,
  }));
  const elbowData = asArray(payload.elbow_curve)
    .map((item) => asRecord(item))
    .map((item) => ({ label: String(item.n_clusters ?? ""), value: asNumber(item.distortion) ?? 0 }))
    .filter((item) => item.label !== "" && Number.isFinite(item.value));
  const profiles = asArray(payload.cluster_profiles).filter((item): item is ClusterProfile => typeof item === "object" && item !== null);
  const rows = previewRows(payload.preview);

  return (
    <>
      <MetricGrid
        cards={[
          { label: "Algoritmo", value: String(payload.algorithm ?? "Clusterização") },
          { label: "Linhas usadas", value: formatNumber(payload.rows_used, 0) },
          { label: "Features usadas", value: asArray(payload.features_used).length },
          { label: "Features codificadas", value: formatNumber(payload.encoded_features_count, 0) },
          ...(payload.inertia !== undefined ? [{ label: "Inércia", value: formatNumber(payload.inertia, 2) }] : []),
          ...(payload.noise_count !== undefined ? [{ label: "Ruído", value: formatNumber(payload.noise_count, 0) }] : []),
        ]}
      />

      <div className="charts-grid">
        <BarChart title="Distribuição de registros por cluster" data={clusterCounts} />
        <PieChart title="Participação percentual dos clusters" data={clusterPieData} />
        <LineChart title="Método do cotovelo — distorção por quantidade de clusters" data={elbowData} />
        <ResultTable title="Prévia dos registros classificados" rows={rows} />
      </div>
      <ClusterProfiles profiles={profiles} />
    </>
  );
}

function AnomalyResult({ payload }: { payload: Record<string, unknown> }) {
  const normalCount = asNumber(payload.normal_count) ?? 0;
  const anomalyCount = asNumber(payload.anomaly_count) ?? 0;
  const total = normalCount + anomalyCount;
  const distribution = [
    { label: "Normais", value: normalCount, count: normalCount, percentage: total ? (normalCount / total) * 100 : 0 },
    { label: "Anomalias", value: anomalyCount, count: anomalyCount, percentage: total ? (anomalyCount / total) * 100 : 0 },
  ];
  const rows = previewRows(payload.preview);

  return (
    <>
      <MetricGrid
        cards={[
          { label: "Algoritmo", value: String(payload.algorithm ?? "Isolation Forest") },
          { label: "Linhas usadas", value: formatNumber(payload.rows_used, 0) },
          { label: "Anomalias", value: formatNumber(payload.anomaly_count, 0) },
          { label: "Contaminação", value: formatRatioAsPercent(payload.contamination) },
        ]}
      />

      <div className="charts-grid">
        <BarChart title="Distribuição entre registros normais e anômalos" data={distribution} />
        <PieChart title="Percentual de anomalias" data={distribution} />
        <ResultTable title="Registros com menor score de anomalia" rows={rows} />
      </div>
    </>
  );
}

function AssociationRulesResult({ payload }: { payload: Record<string, unknown> }) {
  const rules = asArray(payload.rules).filter((item): item is RuleRow => typeof item === "object" && item !== null).slice(0, 20);
  const liftData = rules.slice(0, 10).map((rule, index) => ({
    label: `Regra ${index + 1}`,
    value: asNumber(rule.lift) ?? 0,
  }));
  const confidenceData = rules.slice(0, 10).map((rule, index) => ({
    label: `Regra ${index + 1}`,
    value: (asNumber(rule.confidence) ?? 0) * 100,
  }));

  return (
    <>
      <MetricGrid
        cards={[
          { label: "Algoritmo", value: String(payload.algorithm ?? "Apriori") },
          { label: "Linhas usadas", value: formatNumber(payload.rows_used, 0) },
          { label: "Regras encontradas", value: formatNumber(payload.rules_count, 0) },
          { label: "Suporte mínimo", value: formatRatioAsPercent(payload.min_support) },
          { label: "Confiança mínima", value: formatRatioAsPercent(payload.min_confidence) },
        ]}
      />

      <div className="charts-grid">
        <BarChart title="Lift das principais regras" data={liftData} />
        <BarChart title="Confiança das principais regras" data={confidenceData} valueSuffix="%" />
        {rules.length > 0 && (
          <div className="chart-card table-card">
            <h3>Principais regras de associação</h3>
            <div className="tabela-container compact-table">
              <table>
                <thead>
                  <tr>
                    <th>Antecedentes</th>
                    <th>Consequentes</th>
                    <th>Suporte</th>
                    <th>Confiança</th>
                    <th>Lift</th>
                  </tr>
                </thead>
                <tbody>
                  {rules.map((rule, index) => (
                    <tr key={index}>
                      <td>{normalizeList(rule.antecedents)}</td>
                      <td>{normalizeList(rule.consequents)}</td>
                      <td>{formatRatioAsPercent(rule.support)}</td>
                      <td>{formatRatioAsPercent(rule.confidence)}</td>
                      <td>{formatNumber(rule.lift, 2)}</td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          </div>
        )}
      </div>
    </>
  );
}

function RawResult({ payload }: { payload: Record<string, unknown> }) {
  return (
    <details className="raw-json">
      <summary>Ver JSON bruto retornado pela API</summary>
      <pre>{JSON.stringify(payload, null, 2)}</pre>
    </details>
  );
}

export function ResultViewer({ result }: Props) {
  if (!result) return null;

  const payload = asRecord(result.payload);
  const type = result.analysis_type.toLowerCase();

return (
  <section className="section-block full-width-card" id="resultados">
    <div className="result-header">
      <div>
        <span className="result-kicker">Resultado da análise</span>
        <h2>{getAnalysisTitle(result.analysis_type)}</h2>
      </div>

      <div className="result-actions">
        <button
          type="button"
          className="btn-outline"
          onClick={handleDownloadAllCharts}
        >
          Baixar todos os gráficos
        </button>
      </div>
    </div>

    {type.includes("statistics") ||
    type.includes("statistic") ||
    type.includes("estat") ? (
      <StatisticsResult payload={payload} />
    ) : type.includes("kmeans") ||
      type.includes("dbscan") ||
      payload.cluster_counts ? (
      <ClusteringResult payload={payload} />
    ) : type.includes("anomal") ||
      type.includes("isolation") ||
      payload.anomaly_count !== undefined ? (
      <AnomalyResult payload={payload} />
    ) : type.includes("association") || type.includes("rule") || payload.rules ? (
      <AssociationRulesResult payload={payload} />
    ) : (
      <RawResult payload={payload} />
    )}

    <RawResult payload={payload} />
  </section>
);
}