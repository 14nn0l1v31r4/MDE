# Backend - Educational Analytics API

API em FastAPI organizada em camadas inspiradas em Clean Architecture, com persistência em PostgreSQL via SQLAlchemy.

## Camadas

```text
app/
├── domain              # Entidades e exceções de domínio
├── application         # Casos de uso e portas
├── infrastructure      # PostgreSQL, storage local e serviços de análise
└── interfaces          # Rotas e schemas da API
```

## Variáveis de ambiente

Veja `.env.example`:

```text
DATABASE_URL=postgresql+psycopg://analytics:analytics@localhost:5432/educational_analytics
UPLOAD_DIR=./storage/uploads
CORS_ORIGINS=["http://localhost:5173"]
```

## Rodar localmente

```bash
cd backend
python -m venv .venv
source .venv/bin/activate  # Linux/Mac
# .venv\Scripts\activate  # Windows
pip install -r requirements.txt
uvicorn app.interfaces.api.main:app --reload
```

Acesse:

- API: http://localhost:8000
- Swagger: http://localhost:8000/docs

## Banco de dados

As tabelas `datasets` e `analysis_results` são criadas automaticamente no startup da API para facilitar o desenvolvimento. Em produção, o ideal é trocar isso por migrações com Alembic.
