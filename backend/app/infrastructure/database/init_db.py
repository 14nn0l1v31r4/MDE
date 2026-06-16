from app.infrastructure.database.models import Base
from app.infrastructure.database.session import engine


def init_db() -> None:
    Base.metadata.create_all(bind=engine)
