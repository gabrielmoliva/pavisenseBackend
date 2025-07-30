# Arquivo de conexão ao banco de dados

from sqlmodel import SQLModel, create_engine, Session

SQLALCHEMY_DATABASE_URL = "sqlite:///./pavisense.db"
engine = create_engine(SQLALCHEMY_DATABASE_URL, connect_args={"check_same_thread": False})

def get_session():
    with Session(engine) as session:
        yield session

def init_db():
    SQLModel.metadata.create_all(engine)
