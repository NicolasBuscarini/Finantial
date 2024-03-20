from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
import os

# GET ENVS
user = os.getenv("USER")
password = os.getenv("PASSWORD")
host = os.getenv("HOST")
bd = os.getenv("BD")

def create_session():
    # engine = create_engine(f'mysql+pymysql://{user}:{password}@{host}/{bd}')
    password_encoded = 'bob%40123'  # Encoding '@' to '%40'
    engine = create_engine(f'mysql+mysqlconnector://root:{password_encoded}@localhost/finantial')
    Session = sessionmaker(bind=engine)
    session = Session()
    return session