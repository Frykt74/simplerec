import logging
from app.db.session import engine
from app.models.base import Base
from app.core.config import settings

logger = logging.getLogger(__name__)


def init_db() -> None:
    """
    Инициализация базы данных
    Создает все таблицы если они не существуют
    """
    # Создание директории для БД
    settings.DATABASE_PATH.parent.mkdir(parents=True, exist_ok=True)
    
    # Создание всех таблиц
    logger.info(f"Creating database tables in {settings.DATABASE_PATH}")
    Base.metadata.create_all(bind=engine)
    logger.info("Database tables created successfully")


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    init_db()
    