from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
import os

# GET ENVS
user = os.getenv("USER")
password = os.getenv("PASSWORD")
host = os.getenv("HOST")
bd = os.getenv("BD")

def create_session():
    engine = create_engine(f'mysql+mysqlconnector://{user}:{password}@{host}/{bd}')
    Session = sessionmaker(bind=engine)
    session = Session()
    return session