import os
from dotenv import load_dotenv
from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker
from sqlalchemy.exc import SQLAlchemyError
from app.infra.entities import Base
from app.config.logging_config import setup_logging
from fastapi import HTTPException 

# Setting up the environment variables for the application.
env = os.getenv("ENV", "dev")
dotenv_path = ".prod.env" if env == "prod" else ".dev.env"
load_dotenv(dotenv_path)

# Retrieving environment variables from the system
user = os.getenv("USER")
password = os.getenv("PASSWORD")
host = os.getenv("HOST")
bd = os.getenv("BD")

# Connection to a MySQL database using the mysqlconnector driver.
engine = create_engine(
    f"mysql+mysqlconnector://{user}:{password}@{host}/{bd}"
)

def get_db():
    """
    The function `get_db` creates a database session and yields it, ensuring the session is closed after
    its use.
    """
    db = create_session()
    try:
        yield db
    finally:
        db.close()

def create_session():
    """
    Create a database session.
    """
    Session = sessionmaker(bind=engine)
    session = Session()
    return session


def setup_database():
    """
    Function to test database connection and create tables using SQLAlchemy models.
    """
    logger = setup_logging()
    try:
        logger.info("Connecting to the database...")
        # Simple SQL query to test the connection
        with create_session() as db:
            db.execute(text("SELECT 1"))
        logger.info("Database connection successful.")

        # Create all database tables defined in SQLAlchemy models using the
        # `engine` database engine.
        Base.metadata.create_all(bind=engine)
    except SQLAlchemyError as e:
        logger.error(f"Error connecting to the database: {e}")
        raise HTTPException(
            status_code=500, detail="Error connecting to the database."
        ) from e  # Use `from e` to provide context about the original exception
