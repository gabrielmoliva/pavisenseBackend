from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from typing import List
import joblib

app = FastAPI()

# Dados recebidos da aplicacao
class Dados(BaseModel):
    timestamp: int
    lat: float
    long: float
    accValues: List[float]
    gyroValues: List[float]
    speed: float

# Dados para processamento do modelo
class DataframeRow(BaseModel):
    acc_x: float
    acc_y: float
    acc_z: float
    gyro_x: float
    gyro_y: float
    gyro_z: float
    speed: float

# Ponto de conforto decorrente da avaliacao do modelo
class PontoConforto(BaseModel):
    lat: float
    long: float
    conforto: str

@app.post('/sendData', response_model=Dados)
def send_data(dados: Dados):
    print(f'Timestamp: {dados.timestamp}, Latitude: {dados.lat}, Longitude: {dados.long}')
    print(f'Acelerometro: {dados.accValues}, Giroscopio: {dados.gyroValues}, Velocidade: {dados.speed}')
    return dados

