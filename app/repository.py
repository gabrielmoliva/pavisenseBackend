from sqlalchemy.orm import Session
from . import models, schemas

def criar_ponto(db: Session, ponto: schemas.PontoConforto):
    db_ponto = models.PontoConfortoDB(**ponto.model_dump())
    db.add(db_ponto)
    db.commit()
    db.refresh(db_ponto)
    return db_ponto

def listar_pontos(db: Session):
    return db.query(models.PontoConfortoDB).all()