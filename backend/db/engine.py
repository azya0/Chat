import logging

from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker, Session
from typing_extensions import AsyncGenerator

from config import get_settings
import sqlalchemy as sql

logger = logging.getLogger(__name__)


class SessionManager:

    def __init__(self):
        settings = get_settings()
        self.async_engine = create_async_engine(url=settings.SQLALCHEMY_URL)
        self.async_session = sessionmaker(
            self.async_engine,
            expire_on_commit=False,
            class_=AsyncSession
        )

    def __new__(cls):
        if not hasattr(cls, 'instance'):
            cls.instance = super().__new__(cls)
        return cls.instance

    def get_session(self) -> Session | AsyncSession:
        return self.async_session()

    async def get_all_table_names(self):
        async with self.async_engine.connect() as conn:
            tables = await conn.run_sync(
                lambda sync_conn: sql.inspect(sync_conn).get_table_names()
            )

            return tables


async def get_async_session() -> AsyncGenerator[AsyncSession, None]:
    async_session = SessionManager().get_session()

    async with async_session:
        try:
            yield async_session
            await async_session.commit()
        except SQLAlchemyError as exc:
            await async_session.rollback()
            logger.error('Sqlalchemy error')
            raise exc
        finally:
            await async_session.close()
