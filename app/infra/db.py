from dotenv import load_dotenv
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
import os

# Carrega variáveis de ambiente baseado no ambiente selecionado (dev ou prod)
env = os.getenv("ENV", "dev")
dotenv_path = "prod.env" if env == "prod" else "dev.env"
load_dotenv(dotenv_path)

# Obter variáveis de ambiente
user = os.getenv("USER")
password = os.getenv("PASSWORD")
host = os.getenv("HOST")
bd = os.getenv("BD")

# Definir engine global com base nas variáveis de ambiente
engine = create_engine(
    f"mysql+mysqlconnector://{user}:{password}@{host}/{bd}"
)

def create_session():
    """
    Create a database session.
    """
    Session = sessionmaker(bind=engine)
    session = Session()
    return session
