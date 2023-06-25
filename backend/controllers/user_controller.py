from fastapi import Depends, exceptions
from fastapi_users import BaseUserManager, FastAPIUsers, IntegerIDMixin, schemas, models
from fastapi_users.authentication import (
    AuthenticationBackend,
    JWTStrategy, BearerTransport,
)

from fastapi_users.db import SQLAlchemyUserDatabase
from flask import Request
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from config import get_settings
from db import get_async_session
from db.models import User, get_user_db


class UserManager(IntegerIDMixin, BaseUserManager[User, int]):
    async def create(
            self,
            user_create: schemas.UC,
            safe: bool = False,
            request: Request | None = None,
            session: AsyncSession = Depends(get_async_session)
    ) -> models.UP:
        statement = select(User).where(User.username == user_create.username)

        if (await self.user_db.session.execute(statement)).first() is not None:
            raise exceptions.HTTPException(400, detail='REGISTER_USER_ALREADY_EXISTS')
        return await super().create(user_create, safe, request)


async def get_user_manager(user_db: SQLAlchemyUserDatabase = Depends(get_user_db)):
    yield UserManager(user_db)


cookie_transport = BearerTransport(tokenUrl="auth/jwt/login")


def get_jwt_strategy() -> JWTStrategy:
    return JWTStrategy(secret=get_settings().SECRET, lifetime_seconds=3600)


auth_backend = AuthenticationBackend(
    name="cookie",
    transport=cookie_transport,
    get_strategy=get_jwt_strategy,
)

fastapi_users = FastAPIUsers[User, int](get_user_manager, [auth_backend])

current_active_user = fastapi_users.current_user(active=True)
