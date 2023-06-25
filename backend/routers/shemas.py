import datetime
import uuid
from string import ascii_letters, digits

from fastapi_users import schemas
from fastapi_users.schemas import CreateUpdateDictModel
from pydantic import EmailStr, validator, BaseModel


class UserRead(schemas.BaseUser[uuid.UUID]):
    username: str


class UserCreate(CreateUpdateDictModel):
    email: EmailStr
    username: str
    password: str

    @validator('username')
    def username_validator(cls, v):
        if len(v) < 3:
            raise ValueError(f'username length less then 3')

        banned_chars = set(filter(lambda char: char not in ascii_letters + digits + '_', v))

        if any(banned_chars):
            raise ValueError(f'username can\'t include chars like: {", ".join(banned_chars)}')
        return v

    @validator('password')
    def password_validator(cls, v):
        if len(v) < 5:
            raise ValueError(f'password length less then 5')
        return v


class UserUpdate(schemas.BaseUserUpdate):
    username: str


class MessageRead(BaseModel):
    id: int
    content: str

    created_at: datetime.datetime
    updated_at: datetime.datetime

    class Config:
        orm_mode = True


class ChatRead(BaseModel):
    id: int
    interlocutor: UserRead

    last_message: MessageRead

    class Config:
        orm_mode = True
