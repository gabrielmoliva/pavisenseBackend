# Models da aplicação

from sqlmodel import SQLModel, Field
from typing import Optional, List
from enum import Enum

class NivelConforto(int, Enum):
    GOOD_ROAD = 1
    BAD_ROAD  = 2

# Coordenada com um nível de conforto específico
class PontoConforto(SQLModel, table=True):
    id: Optional[int] = Field(primary_key=True, index=True)
    lat: float
    long: float
    conforto: NivelConforto
    timestamp: float

# Dados recebidos do front
class Dados(SQLModel, table=False):
    timestamp: float
    lat: float
    long: float
    accValues: List[float]
    gyroValues: List[float]
    speed: float
