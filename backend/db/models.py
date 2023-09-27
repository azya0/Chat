import datetime

from fastapi import Depends
from fastapi_users.db import SQLAlchemyBaseUserTable
from fastapi_users_db_sqlalchemy import SQLAlchemyUserDatabase
from sqlalchemy import Column, String, DateTime, func, Integer, ForeignKey
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import as_declarative, relationship
from sqlalchemy.orm import declarative_mixin

from db.engine import get_async_session


@as_declarative()
class Base:
    __table_args__ = {'extend_existing': True}

    id = Column(Integer, primary_key=True, index=True)


@declarative_mixin
class TimestampMixin:
    created_at = Column(DateTime, server_default=func.now())
    updated_at = Column(
        DateTime,
        server_default=func.now(),
        server_onupdate=func.now(),
        onupdate=datetime.datetime.now
    )


class User(TimestampMixin, SQLAlchemyBaseUserTable, Base):
    __tablename__ = 'user'

    username = Column(String(30), index=True, unique=True, nullable=False)

    chats = relationship('Chat', secondary='user_xref_chat', back_populates='users')
    messages = relationship('Message', back_populates='author')


class Message(TimestampMixin, Base):
    __tablename__ = 'message'

    content = Column(String(280), nullable=False)
    chat_id = Column(Integer, ForeignKey('chat.id'), nullable=False)
    author_id = Column(Integer, ForeignKey('user.id'), nullable=False)

    chat = relationship("Chat", back_populates='messages', uselist=False)
    author = relationship("User", back_populates='messages', uselist=False)


class UserToChat(Base):
    __tablename__ = 'user_xref_chat'

    user = Column(Integer, ForeignKey('user.id'), index=True, nullable=False)
    chat = Column(Integer, ForeignKey('chat.id'), nullable=False)


class Chat(TimestampMixin, Base):
    __tablename__ = 'chat'

    messages = relationship('Message', lazy='selectin', uselist=True, order_by='Message.created_at')
    users = relationship('User', secondary='user_xref_chat', back_populates='chats', uselist=True)


async def get_user_db(session: AsyncSession = Depends(get_async_session)):
    yield SQLAlchemyUserDatabase(session, User)
