import logging

from fastapi import FastAPI, HTTPException
from sqlalchemy import text
from sqlalchemy.exc import SQLAlchemyError

from app.db.neon import SessionLocal
from app.logging import configure_logging
from app.routes.Students import router as students_router

logger = logging.getLogger(__name__)

configure_logging()
app = FastAPI()
app.include_router(students_router)

@app.get("/")
def root():
    logger.info("Root endpoint accessed")
    return {"message": "welcome to the FastAPI application!"}

@app.get("/health")
def health_check():
    logger.info("Health check endpoint accessed")
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