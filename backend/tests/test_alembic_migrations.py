import asyncio
import logging
from pathlib import Path
from unittest.mock import patch

from alembic import command
from alembic.config import Config

from app.infrastructure.database.models import Base
from app.interfaces.api.main import app, lifespan


BACKEND_DIR = Path(__file__).resolve().parents[1]


def test_alembic_head_creates_authentication_ownership_schema(capsys):
    config = Config(str(BACKEND_DIR / "alembic.ini"))

    command.upgrade(config, "head", sql=True)

    sql = capsys.readouterr().out

    assert "CREATE TABLE users" in sql
    assert "CREATE TABLE datasets" in sql
    assert "CREATE TABLE analysis_results" in sql
    assert "user_id" in sql
    assert "FOREIGN KEY(user_id)" in sql


def test_api_lifespan_does_not_mutate_database_schema():
    async def run_lifespan():
        async with lifespan(app):
            pass

    with patch.object(Base.metadata, "create_all") as create_all:
        asyncio.run(run_lifespan())

    create_all.assert_not_called()


def test_alembic_configuration_does_not_disable_application_loggers(capsys):
    config = Config(str(BACKEND_DIR / "alembic.ini"))

    command.upgrade(config, "head", sql=True)
    capsys.readouterr()

    assert logging.getLogger("mde.audit").disabled is False
