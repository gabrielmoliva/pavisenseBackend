from fastapi import FastAPI, HTTPException, WebSocket, WebSocketDisconnect, Depends
from typing import List
from sqlmodel import Session, select
import joblib
import pandas as pd
import time

from app.models import Dados, PontoConforto
from app.database import init_db, get_session

app = FastAPI()

init_db()

model = joblib.load("model.joblib")

@app.websocket("/ws/sendData")
async def websocket_endpoint(ws: WebSocket, session: Session = Depends(get_session)):
    await ws.accept()
    buffer: List[Dados] = []    # Armazena os dados recebidos por um cliente

    try:
        while True:
            data = await ws.receive_json()
            dados = Dados(**data)
            buffer.append(dados)

            # talvez transformar em funcao separada async
            resultados = []
            while len(buffer) >= 100:
                dados_janela = buffer[:100]
                df = pd.DataFrame([d.model_dump() for d in dados_janela])
                janela = df.drop(['speed', 'lat', 'long']).median()
                janela = janela.join(df['speed'], how='right')
                predicao = model.predict(janela)

                lat_mediana = df['lat'].median()
                long_mediana = df['long'].median()
                # TODO: verificar se o timestamp a ser guardado deve ser o de agora ou a mediana dos timestamps das coletas
                pontoConforto = PontoConforto(lat=lat_mediana, long=long_mediana, 
                                              conforto=predicao, timestamp=time.time())
                session.add(pontoConforto)
                ws.send_json(pontoConforto)
                buffer.pop(0)   # Remove o item mais antigo do buffer
    except WebSocketDisconnect:
        buffer.clear()

# TODO: fazer busca por região próxima ao usuário a fim de melhorar desempenho
@app.get('/getPontos', response_model=List[PontoConforto])
async def get_pontos(session: Session = Depends(get_session)):
    pontos = session.exec(select(PontoConforto)).all()
    return pontos