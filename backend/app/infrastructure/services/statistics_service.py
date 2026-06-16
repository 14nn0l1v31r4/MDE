from typing import Any
import pandas as pd


PIE_CHART_SPECS = [
    {"id": "cor_ou_raca", "title": "Distribuição por Cor ou Raça", "column": "cor_ou_raca", "legend_title": "Cor ou Raça"},
    {"id": "forma_ingresso", "title": "Distribuição Forma de Ingresso", "column": "Forma de Ingresso", "legend_title": "Legenda"},
    {"id": "renda_mensal", "title": "Distribuição Renda Mensal", "column": "renda_mensal_familia", "legend_title": "Legenda"},
    {"id": "periodo_fundamental", "title": "Distribuição por Período", "column": "periodo_fundamental", "legend_title": "Período"},
    {"id": "escola", "title": "Distribuição por escola", "column": "escola_publica", "legend_title": "Tipo"},
    {"id": "sexo", "title": "Distribuição por Sexo", "column": "sexo", "legend_title": "Sexo"},
    {"id": "faixa_etaria", "title": "Distribuição por Faixa Etária", "column": "faixa_etaria", "legend_title": "Idade"},
    {"id": "semestre", "title": "Distribuição por Semestre", "column": "semestre", "legend_title": "Semestre"},
    {"id": "publica_privada", "title": "Distribuição Pública x Privada", "column": "escola_publica", "legend_title": "Legenda"},
    {"id": "turnos", "title": "Distribuição de Turnos", "column": "turno", "legend_title": "Turno"},
    {"id": "atividade_remunerada", "title": "Distribuição Econômica", "column": "atividade_remunerada", "legend_title": "Legenda"},
    {"id": "participacao_economia", "title": "Distribuição de Participação na economia familiar", "column": "participacao_economia_familia", "legend_title": "Legenda"},
]

BAR_CHART_SPECS = [
    {"id": "grande_area_do_curso", "title": "Distribuição por Área de Curso", "column": "grande_area_do_curso"},
    {"id": "uf_candidato", "title": "Distribuição por UF do Candidato", "column": "uf_candidato"},
    {"id": "cidade_candidato", "title": "Distribuição por Cidade do Candidato", "column": "cidade_candidato", "limit": 20},
    {"id": "cidades_agrupadas", "title": "Distribuição por Cidade do Candidato — cidades pequenas agrupadas", "column": "cidades_agrupadas", "source_column": "cidade_candidato", "limit": 20},
]

CROSSTAB_SPECS = [
    {"id": "cor_ingresso", "title": "Cor ou Raça x Forma de Ingresso", "index": "cor_ou_raca", "columns": "Forma de Ingresso"},
    {"id": "ingresso_renda", "title": "Forma de Ingresso x Renda Mensal", "index": "Forma de Ingresso", "columns": "renda_mensal_familia"},
    {"id": "faixa_area", "title": "Faixa Etária x Área do Curso", "index": "faixa_etaria", "columns": "grande_area_do_curso"},
    {"id": "sexo_faixa", "title": "Sexo x Faixa Etária", "index": "sexo", "columns": "faixa_etaria"},
    {"id": "sexo_area", "title": "Sexo x Área do Curso", "index": "sexo", "columns": "grande_area_do_curso"},
    {"id": "uf_area", "title": "UF do Candidato x Área do Curso", "index": "uf_candidato", "columns": "grande_area_do_curso"},
    {"id": "renda_escola", "title": "Renda Mensal x Escola Pública", "index": "renda_mensal_familia", "columns": "escola_publica"},
]


class PandasStatisticsService:
    def summarize(self, df: pd.DataFrame) -> dict[str, Any]:
        normalized = df.copy()
        normalized.columns = normalized.columns.astype(str)

        numeric_df = normalized.select_dtypes(include="number")
        numeric_summary = numeric_df.describe().fillna("").to_dict() if not numeric_df.empty else {}
        categorical_columns = normalized.select_dtypes(include=["object", "category", "bool"]).columns.tolist()
        categorical_summary = {}
        for column in categorical_columns[:20]:
            categorical_summary[column] = (
                normalized[column]
                .astype(str)
                .value_counts(dropna=False)
                .head(10)
                .to_dict()
            )

        return {
            "rows": int(normalized.shape[0]),
            "columns": [str(column) for column in normalized.columns],
            "missing_values": normalized.isna().sum().astype(int).to_dict(),
            "numeric_summary": numeric_summary,
            "categorical_summary": categorical_summary,
            "notebook_charts": self._build_notebook_charts(normalized),
            "notebook_crosstabs": self._build_notebook_crosstabs(normalized),
            "available_notebook_columns": self._available_notebook_columns(normalized),
        }

    def _available_notebook_columns(self, df: pd.DataFrame) -> list[str]:
        expected = sorted({
            *[spec["column"] for spec in PIE_CHART_SPECS],
            *[spec.get("source_column", spec["column"]) for spec in BAR_CHART_SPECS],
            *[spec["index"] for spec in CROSSTAB_SPECS],
            *[spec["columns"] for spec in CROSSTAB_SPECS],
        })
        return [column for column in expected if column in df.columns]

    def _safe_series(self, df: pd.DataFrame, column: str) -> pd.Series:
        series = df[column].copy()
        return series.fillna("Não informado").astype(str)

    def _value_counts_payload(self, df: pd.DataFrame, column: str, limit: int | None = None) -> list[dict[str, Any]]:
        series = self._safe_series(df, column)
        counts = series.value_counts(dropna=False)
        total = int(counts.sum())
        if limit is not None and len(counts) > limit:
            top = counts.head(limit - 1)
            others = counts.iloc[limit - 1:].sum()
            counts = pd.concat([top, pd.Series({"Demais": others})])
        return [
            {
                "label": str(label),
                "count": int(count),
                "percentage": float((count / total) * 100) if total else 0.0,
            }
            for label, count in counts.items()
        ]

    def _build_notebook_charts(self, df: pd.DataFrame) -> list[dict[str, Any]]:
        charts: list[dict[str, Any]] = []

        for spec in PIE_CHART_SPECS:
            column = spec["column"]
            if column not in df.columns:
                continue
            charts.append({
                "id": spec["id"],
                "kind": "pie",
                "title": spec["title"],
                "column": column,
                "legend_title": spec.get("legend_title", "Legenda"),
                "values": self._value_counts_payload(df, column),
            })

        working = df.copy()
        if "cidade_candidato" in working.columns and "cidades_agrupadas" not in working.columns:
            city_share = self._safe_series(working, "cidade_candidato").value_counts(normalize=True)
            small_cities = set(city_share[city_share < 0.01].index.tolist())
            working["cidades_agrupadas"] = self._safe_series(working, "cidade_candidato").apply(
                lambda city: "Demais Cidades" if city in small_cities else city
            )

        for spec in BAR_CHART_SPECS:
            column = spec["column"]
            if column not in working.columns:
                continue
            charts.append({
                "id": spec["id"],
                "kind": "bar",
                "title": spec["title"],
                "column": column,
                "value_mode": "percentage",
                "values": self._value_counts_payload(working, column, spec.get("limit")),
            })

        return charts

    def _build_notebook_crosstabs(self, df: pd.DataFrame) -> list[dict[str, Any]]:
        crosstabs: list[dict[str, Any]] = []
        for spec in CROSSTAB_SPECS:
            index = spec["index"]
            columns = spec["columns"]
            if index not in df.columns or columns not in df.columns:
                continue

            table = pd.crosstab(
                self._safe_series(df, index),
                self._safe_series(df, columns),
                normalize=True,
            ) * 100
            table = table.round(1)
            crosstabs.append({
                "id": spec["id"],
                "title": spec["title"],
                "index": index,
                "columns_label": columns,
                "columns": [str(column) for column in table.columns.tolist()],
                "rows": [
                    {
                        "label": str(row_label),
                        "values": {str(col): float(table.loc[row_label, col]) for col in table.columns},
                    }
                    for row_label in table.index
                ],
                "unit": "%",
                "normalization": "global",
            })
        return crosstabs
