from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.sql import text
from fastapi import HTTPException
from app.api.models.entities import Base
from app.infra.db import create_session, engine
from app.config.logging_config import setup_logging

logger = setup_logging()


def setup_database():
    """
    Function to test database connection and create tables using SQLAlchemy models.
    """
    try:
        logger.info("Connecting to the database...")
        # Simple SQL query to test the connection
        with create_session() as db:
            db.execute(text("SELECT 1"))
        logger.info("Database connection successful.")

        # Create all database tables defined in SQLAlchemy models using the `engine` database engine.
        Base.metadata.create_all(bind=engine)
    except SQLAlchemyError as e:
        logger.error(f"Error connecting to the database: {e}")
        raise HTTPException(
            status_code=500, detail="Error connecting to the database."
        )
