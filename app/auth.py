from datetime import timedelta, datetime, timezone
from typing import Annotated
from fastapi import APIRouter, Depends, HTTPException
from passlib.context import CryptContext
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from sqlmodel import SQLModel, Session
from app.database import get_session
from starlette import status
from app.models import Usuario
from dotenv import load_dotenv
import os
from jose import jwt, JWTError

load_dotenv()

SECRET_KEY = os.getenv('SECRET_KEY')
ALGORITHM = os.getenv('ALGORITHM')

router = APIRouter(
    prefix="/auth",
    tags=["auth"],
)

bcrypt_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
oauth2_bearer = OAuth2PasswordBearer(tokenUrl="auth/token")


class CreateUserRequest(SQLModel, table=False):
    username: str
    password: str


class Token(SQLModel, table=False):
    access_token: str
    token_type: str


db_dependency = Annotated[Session, Depends(get_session)]


@router.post("/", status_code=status.HTTP_201_CREATED)
async def create_user(db: db_dependency, create_user_request: CreateUserRequest):
    create_user_model = Usuario(
        login=create_user_request.username,
        senha=bcrypt_context.hash(create_user_request.password),
    )

    db.add(create_user_model)
    db.commit()


@router.post("/token", response_model=Token)
async def login_for_access_token(form_data: Annotated[OAuth2PasswordRequestForm, Depends()], db: db_dependency):
    user = authenticate_user(form_data.username, form_data.password, db)
    if not user:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED,
                            detail='Não foi possível validar o usuário')
    token = create_access_token(user.id, user.login, timedelta(days=5.0))

    return {'access_token': token, 'token_type': 'bearer'}

def authenticate_user(login: str, password: str, db):
    user = db.query(Usuario).filter(Usuario.login == login).first()
    if not user:
        return False
    if not bcrypt_context.verify(password, user.senha):
        return False
    return user

def create_access_token(username: str, user_id: int, expires_delta: timedelta):
    encode = {'sub': username, 'id': user_id}
    expires = datetime.now(timezone.utc) + expires_delta
    encode.update({'exp': expires})
    return jwt.encode(encode, SECRET_KEY, algorithm=ALGORITHM)

async def get_current_user(token: Annotated[str, Depends(oauth2_bearer)]):
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=ALGORITHM)
        login: str = payload.get('sub')
        user_id: int = payload.get('id')
        if login is None or user_id is None:
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED,
                                detail='Não foi possível validar o usuário')
        return {'login': login, 'id': user_id}
    except JWTError:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED,
                            detail='Não foi possível validar o usuário')
