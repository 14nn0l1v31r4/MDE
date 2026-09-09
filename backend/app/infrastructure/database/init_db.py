from app.infrastructure.database.models import Base
from app.infrastructure.database.session import engine


import logging

logger = logging.getLogger(__name__)


def init_db() -> None:
    Base.metadata.create_all(bind=engine)
    try:
        Base.metadata.create_all(bind=engine)
    except Exception as exc:
        logger.warning(f"Não foi possível inicializar tabelas no banco de dados: {exc}")
