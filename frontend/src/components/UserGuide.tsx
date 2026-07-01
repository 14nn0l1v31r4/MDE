export function UserGuide() {
  const manualPath = "/docs/manual_usuario_plataforma_mineracao_dados_educacionais.pdf";

  return (
    <section className="section-block full-width-card" id="manual">
      <div className="guide-header">
        <div>
          <span className="section-kicker">Guia de Usuário</span>
          <h2>Como usar a plataforma</h2>
          <p className="hint">
            Siga este fluxo para importar uma base, executar análises e
            consultar os resultados gerados.
          </p>
        </div>

        <div className="guide-actions">
         
        

          <a
            href={manualPath}
            download
            className="button-link button-link-secondary"
          >
            Baixar manual PDF
          </a>
        </div>
      </div>

      <div className="usage-flow">
        <div className="usage-step">
          <span>1</span>
          <div>
            <h3>Prepare o arquivo CSV</h3>
            <p>
              Verifique se a primeira linha contém os nomes das colunas e se os
              dados estão organizados em linhas e colunas.
            </p>
          </div>
        </div>

        <div className="usage-step">
          <span>2</span>
          <div>
            <h3>Envie a base</h3>
            <p>
              Acesse a seção de pré-processamento, escolha o arquivo e envie a
              base para a plataforma.
            </p>
          </div>
        </div>

        <div className="usage-step">
          <span>3</span>
          <div>
            <h3>Selecione uma base pré-processada</h3>
            <p>
              Escolha a base desejada na lista de bases disponíveis para carregar
              suas informações.
            </p>
          </div>
        </div>

        <div className="usage-step">
          <span>4</span>
          <div>
            <h3>Confira a pré-visualização</h3>
            <p>
              Veja as primeiras linhas da base para confirmar se as colunas e os
              valores foram carregados corretamente.
            </p>
          </div>
        </div>

        <div className="usage-step">
          <span>5</span>
          <div>
            <h3>Selecione as colunas</h3>
            <p>
              Marque as colunas que deseja usar nas análises ou utilize a opção
              de selecionar todas.
            </p>
          </div>
        </div>

        <div className="usage-step">
          <span>6</span>
          <div>
            <h3>Execute uma análise</h3>
            <p>
              Escolha entre análise estatística, KMeans, DBSCAN, Isolation Forest
              ou regras de associação.
            </p>
          </div>
        </div>

        <div className="usage-step">
          <span>7</span>
          <div>
            <h3>Analise os resultados</h3>
            <p>
              Consulte os cards, tabelas e gráficos gerados na seção de
              resultados.
            </p>
          </div>
        </div>

        <div className="usage-step">
          <span>8</span>
          <div>
            <h3>Exporte os gráficos</h3>
            <p>
              Baixe gráficos individuais em PNG ou todos os gráficos em um
              arquivo ZIP.
            </p>
          </div>
        </div>
      </div>
    </section>
  );
}