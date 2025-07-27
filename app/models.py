from sqlalchemy import Column, Integer, Float, String
from .database import Base

class PontoConfortoDB(Base):
    __tablename__ = "pontos"
    id = Column(Integer, primary_key=True, index=True)
    lat = Column(Float, nullable=False)
    long = Column(Float, nullable=False)
    conforto = Column(String, nullable=False)