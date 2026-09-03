import logging

from fastapi import FastAPI, HTTPException
from sqlalchemy import text
from sqlalchemy.exc import SQLAlchemyError

from app.logging import configure_logging
from app.db.neon import SessionLocal

logger = logging.getLogger(__name__)

configure_logging()
app = FastAPI()

@app.get("/")
def root():
    return {"message": "welcome to the FastAPI application!"}

@app.get("/health")
def health_check():
    return {"status": "healthy"}


@app.get("/health/db")
def database_health_check():
    try:
        with SessionLocal() as db:
            db.execute(text("SELECT 1"))
    except SQLAlchemyError as error:
        logger.exception("Database health check failed")
        raise HTTPException(status_code=503, detail="Database unavailable") from error

    logger.info("Database health check succeeded")
    return {"status": "healthy", "database": "connected"}