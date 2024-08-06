from pydantic import BaseModel

class UserCreate(BaseModel):
    name: str
    username: str
    password: str

class User(BaseModel):
    id: int
    name: str
    username: str

    class Config:
        orm_mode = True

class Token(BaseModel):
    access_token: str
    token_type: str
