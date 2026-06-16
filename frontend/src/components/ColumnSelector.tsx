import type { Dataset } from "../types";

type Props = {
  dataset: Dataset | null;
  selectedColumns: string[];
  onChange: (columns: string[]) => void;
};

export function ColumnSelector({ dataset, selectedColumns, onChange }: Props) {
  if (!dataset) return null;

  const allColumns = dataset.columns;

  const allSelected =
    allColumns.length > 0 &&
    allColumns.every((column) => selectedColumns.includes(column));

  function toggle(column: string) {
    if (selectedColumns.includes(column)) {
      onChange(selectedColumns.filter((item) => item !== column));
    } else {
      onChange([...selectedColumns, column]);
    }
  }

  function selectAllColumns() {
    onChange(allColumns);
  }

  function clearSelectedColumns() {
    onChange([]);
  }

  return (
    <div className="filter-group">
      <div className="column-selector-header">
        <div>
          <h3>Colunas para análise</h3>
          <span className="selected-columns-count">
            {selectedColumns.length} de {allColumns.length} colunas selecionadas
          </span>
        </div>

        <div className="column-selector-actions">
          <button
            type="button"
            className="btn-outline"
            onClick={selectAllColumns}
            disabled={allSelected}
          >
            Selecionar todas
          </button>

          <button
            type="button"
            className="btn-outline btn-outline-danger"
            onClick={clearSelectedColumns}
            disabled={selectedColumns.length === 0}
          >
            Limpar
          </button>
        </div>
      </div>

      <div className="columns-grid">
        {allColumns.map((column) => (
          <label key={column}>
            <input
              type="checkbox"
              checked={selectedColumns.includes(column)}
              onChange={() => toggle(column)}
            />
            {column}
          </label>
        ))}
      </div>
    </div>
  );
}