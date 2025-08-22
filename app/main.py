from fastapi import FastAPI, HTTPException, WebSocket, WebSocketDisconnect, Depends
from typing import List
from sqlmodel import Session, select
import joblib
import pandas as pd
import time
import app.auth as auth
from starlette import status
from typing import Annotated

from app.models import Dados, PontoConforto, NivelConforto, Usuario
from app.database import init_db, get_session
from app.auth import get_current_user

app = FastAPI()
app.include_router(auth.router)

init_db()

db_dependency = Annotated[Session, Depends(get_session)]
user_dependency = Annotated[dict, Depends(get_current_user)]

# Constantes da aplicação
MIN_SPEED_VALUE = 5.55  # m/s
WINDOW_SIZE = 101  # tamanho da janela

def median(pontos: List[Dados]):
    tam = len(pontos)
    return pontos[tam // 2]

@app.websocket("/ws/sendData/{user_id}/{model_info}")
async def websocket_endpoint(ws: WebSocket, db: db_dependency, user_id: int, model_info: int = 0):
    usuario = db.exec(select(Usuario).where(Usuario.id == int(user_id))).first()
    if (not usuario):
        raise Exception("Id de usuário inválido")
    
    if (model_info==0):
        model = joblib.load("model.joblib")
    else:
        model = joblib.load("mlp.joblib")
    
    await ws.accept()
    buffer: List[Dados] = []  # Armazena os dados recebidos por um cliente

    try:
        while True:
            data = await ws.receive_json()
            dados = Dados(**data)
            # print(dados)
            if dados.speed < MIN_SPEED_VALUE:
                continue

            buffer.append(dados)

            # talvez transformar em funcao separada async
            while len(buffer) >= WINDOW_SIZE:
                ponto_mediano = median(buffer)
                colunas_df = [
                    "acc_x_std",
                    "acc_y_std",
                    "acc_z_std",
                    "gyro_x_std",
                    "gyro_y_std",
                    "gyro_z_std",
                    "speed",
                ]
                df = pd.DataFrame([ponto_mediano.model_dump()])[colunas_df]
                predicao = model.predict(df)

                lat = ponto_mediano.lat
                long = ponto_mediano.long
                timestamp = ponto_mediano.timestamp
                # TODO: verificar se o timestamp a ser guardado deve ser o de agora ou a mediana dos timestamps das coletas
                pontoConforto = PontoConforto(
                    id_usuario=user_id,
                    lat=float(lat),
                    long=float(long),
                    conforto=NivelConforto(int(predicao)),
                    timestamp=time.time(),
                )
                db.add(pontoConforto)
                db.commit()
                db.refresh(pontoConforto)
                await ws.send_json(pontoConforto.model_dump())
                buffer.pop(0)  # Remove o item mais antigo do buffer

                print(f"PontoConforto calculado: {pontoConforto}")
    except WebSocketDisconnect:
        buffer.clear()


# TODO: fazer busca por região próxima ao usuário a fim de melhorar desempenho
@app.get("/getPontos", response_model=List[PontoConforto])
async def get_pontos(db: db_dependency):
    pontos = db.exec(select(PontoConforto)).all()
    return pontos


@app.get("/", status_code=status.HTTP_200_OK)
async def usuario(usuario: user_dependency, db: db_dependency):
    if usuario is None:
        raise HTTPException(status_code=401, detail="Falha na autenticação")
    return {"Usuario": usuario}
