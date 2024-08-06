from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from fastapi.responses import JSONResponse

from sqlalchemy.orm import Session
from pydantic import BaseModel
from ..schemas import user as schemas
from ..models import user as models
from ..database import database
from ..core.auth import authenticate_user, get_current_user
from ..core.security import get_password_hash, create_access_token, ACCESS_TOKEN_EXPIRE_MINUTES
from datetime import timedelta

router = APIRouter()

@router.post("/register", response_model=schemas.Token, status_code=status.HTTP_201_CREATED)
async def register_user(user: schemas.UserCreate):
    """
    Реєстрація нового юзера.

    Цей ендпоінт дозволяє створити нового юзера. Якщо юзернейм юзера вже зайняте, буде повернено помилку.

    - **name**: Повне ім'я юзера.
    - **username**: Унікальний юзернейм юзера.
    - **password**: Пароль для облікового запису користувача.
    """
    query = models.users.select().where(models.users.c.username == user.username)
    existing_user = await database.fetch_one(query)
    if existing_user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Username already taken",
        )
    hashed_password = get_password_hash(user.password)
    query = models.users.insert().values(
        name=user.name, 
        username=user.username, 
        hashed_password=hashed_password
    )
    last_record_id = await database.execute(query)
    access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        data={"sub": user.username}, expires_delta=access_token_expires
    )
    return JSONResponse(status_code=status.HTTP_201_CREATED, content={"access_token": access_token, "token_type": "bearer"})

@router.post("/login", response_model=schemas.Token)
async def login_for_access_token(login_request: OAuth2PasswordRequestForm = Depends()):
    """
    Авторизація юзера.

    Цей ендпоінт дозволяє юзера увійти в систему, надавши свой юзернейм та пароль. Якщо дані правильні, буде повернено JWT токен.

    - **username**: Юзернейм юзера.
    - **password**: Пароль юзера.
    """
    user = await authenticate_user(login_request.username, login_request.password)
    
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        data={"sub": user.username}, expires_delta=access_token_expires
    )
    
    return {"access_token": access_token, "token_type": "bearer"}