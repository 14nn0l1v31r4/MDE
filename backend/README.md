# Backend - Educational Analytics API

API FastAPI organizada em camadas, com persistência PostgreSQL via SQLAlchemy.

## Variáveis de ambiente

Copie `.env.example` para `.env` e configure valores reais:

```text
DATABASE_URL=postgresql+psycopg://analytics:change-me@localhost:5434/mining_bd
JWT_SECRET_KEY=replace-with-a-random-value-of-at-least-32-characters
JWT_ALGORITHM=HS256
JWT_ACCESS_TOKEN_EXPIRE_MINUTES=30
UPLOAD_DIR=./storage/uploads
CORS_ORIGINS=["http://localhost:5173"]
MAX_UPLOAD_SIZE_BYTES=52428800
```

## Rodar localmente

```bash
cd backend
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
alembic upgrade head
uvicorn app.interfaces.api.main:app --reload
```

No Windows PowerShell, use `.venv\\Scripts\\activate`.

## Banco de dados

Alembic é fonte única de verdade do schema. A API não cria nem altera tabelas no startup.

Aplicar migrations:

```bash
alembic upgrade head
```

Verificar revisão aplicada:

```bash
alembic current
```

Reverter uma revisão somente em ambiente controlado:

```bash
alembic downgrade -1
```

## Docker Compose

O serviço `migrate` executa `alembic upgrade head` antes do backend. Configure `DATABASE_URL`, `JWT_SECRET_KEY` e `CORS_ORIGINS` no arquivo usado pelo Compose:

```bash
docker compose --env-file backend/.env up --build
```
