# Models da aplicação

from sqlmodel import SQLModel, Field
from typing import Optional, List
from enum import Enum

class NivelConforto (int, Enum):
    GOOD_ROAD = 0
    BAD_ROAD  = 1

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
    acc_x_std: float
    acc_y_std: float
    acc_z_std: float
    gyro_x_std: float
    gyro_y_std: float
    gyro_z_std: float
    speed: float

class Usuario(SQLModel, table=True):
    id: Optional[int] = Field(primary_key=True, default=None)
    login: str = Field(unique=True, nullable=False, index=True, max_length=50) 
    email: Optional[str] = Field(default=None, nullable=True, max_length=50)
    senha: str = Field(nullable=False, max_length=50)