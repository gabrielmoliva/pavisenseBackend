from pydantic import BaseModel
from typing import List

class Dados(BaseModel):
    timestamp: int
    lat: float
    long: float
    accValues: List[float]
    gyroValues: List[float]
    speed: float

class PontoConforto(BaseModel):
    lat: float
    long: float
    conforto: str