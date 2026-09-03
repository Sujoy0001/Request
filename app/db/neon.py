from collections.abc import Generator
import logging

from sqlalchemy import create_engine
from sqlalchemy.orm import Session, sessionmaker

from ..config import get_settings

logger = logging.getLogger(__name__)


def _database_url() -> str:
	url = get_settings().neon_db
	if url.startswith("postgresql://"):
		return url.replace("postgresql://", "postgresql+psycopg://", 1)
	return url


engine = create_engine(_database_url(), pool_pre_ping=True)
SessionLocal = sessionmaker(bind=engine, autoflush=False, autocommit=False)
logger.info("Neon database engine configured")


def get_db() -> Generator[Session, None, None]:
	db = SessionLocal()
	logger.debug("Database session opened")
	try:
		yield db
	finally:
		db.close()
		logger.debug("Database session closed")
