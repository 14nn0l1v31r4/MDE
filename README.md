# Educational Analytics Clean Architecture

Sistema web em **FastAPI + React + PostgreSQL** para transformar notebooks de análise/mineração de dados educacionais em uma aplicação organizada por camadas.

## O que já está implementado

- Upload de CSV
- Persistência de datasets e resultados no PostgreSQL
- Prévia da base
- Estatísticas descritivas
- Clusterização com KMeans
- Clusterização com DBSCAN
- Detecção de anomalias com Isolation Forest
- Regras de associação com Apriori + Association Rules
- Backend separado em Domain, Application, Infrastructure e Interfaces
- Frontend React com Vite e TypeScript
- Tema visual inspirado no layout enviado: verde `#006633`, vermelho `#CC0000`, cards claros, botões arredondados e grid responsivo

## Arquitetura

```text
backend/app
├── domain
│   ├── entities
│   └── exceptions
├── application
│   ├── ports
│   └── use_cases
├── infrastructure
│   ├── database
│   │   ├── models.py
│   │   ├── session.py
│   │   └── init_db.py
│   ├── repositories
│   │   └── postgres_repositories.py
│   ├── services
│   └── storage
└── interfaces
    └── api
        ├── routes
        └── schemas
```

## Rodar com Docker Compose

```bash
docker compose up --build
```

Serviços:

- Frontend: http://localhost:5173
- Backend: http://localhost:8000
- Swagger: http://localhost:8000/docs
- PostgreSQL: localhost:5432

Credenciais locais do banco:

```text
POSTGRES_USER=analytics
POSTGRES_PASSWORD=analytics
POSTGRES_DB=educational_analytics
```

## Rodar backend localmente

Suba apenas o PostgreSQL:

```bash
docker compose up postgres
```

Depois rode a API:

```bash
cd backend
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
cp .env.example .env
uvicorn app.interfaces.api.main:app --reload
```

No Windows PowerShell:

```powershell
cd backend
python -m venv .venv
.venv\Scripts\activate
pip install -r requirements.txt
copy .env.example .env
uvicorn app.interfaces.api.main:app --reload
```

## Rodar frontend localmente

```bash
cd frontend
npm install
npm run dev
```

## Observação sobre Clean Architecture

Os casos de uso continuam dependendo apenas de portas/interfaces da camada `application`. O PostgreSQL foi adicionado apenas na camada `infrastructure`, por meio dos repositórios `PostgresDatasetRepository` e `PostgresAnalysisResultRepository`.

## Frontend visual

O frontend React usa uma identidade própria, apenas inspirada nas cores do material original: verde institucional como cor primária, vermelho como destaque/ação crítica, fundo claro, cards arredondados e layout responsivo.

## Visualizações no frontend

A camada React agora renderiza gráficos a partir do JSON retornado pela API, sem acoplar o backend a bibliotecas de visualização. Foram adicionados:

- cards de métricas para estatística, clusters, anomalias e regras;
- gráfico de valores ausentes por coluna;
- gráfico de médias das colunas numéricas;
- gráficos de distribuição de categorias;
- distribuição de registros por cluster;
- distribuição de registros normais versus anômalos;
- gráfico de lift das principais regras de associação;
- tabelas de prévia dos registros classificados e regras mineradas.

Os gráficos foram implementados em React/CSS puro para evitar dependências extras no frontend.

## Visualizações recriadas a partir dos notebooks

A versão atual inclui visualizações específicas inspiradas nos notebooks de análise estatística e modelagem de clusterização:

- gráficos de pizza para `cor_ou_raca`, `Forma de Ingresso`, `renda_mensal_familia`, `periodo_fundamental`, `escola_publica`, `sexo`, `faixa_etaria`, `semestre`, `turno`, `atividade_remunerada` e `participacao_economia_familia`;
- gráficos de barras para `grande_area_do_curso`, `uf_candidato`, `cidade_candidato` e `cidades_agrupadas`;
- tabelas cruzadas percentuais equivalentes às `pd.crosstab(..., normalize=True)` usadas nos notebooks;
- gráfico de cotovelo do KMeans com distorção por quantidade de clusters;
- distribuição dos clusters em barras e pizza;
- tabelas de perfil dos clusters por coluna, com percentuais para variáveis categóricas e médias para variáveis numéricas.

O backend continua sem gerar imagens: ele entrega os dados estruturados e o React renderiza os gráficos.
