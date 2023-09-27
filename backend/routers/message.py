from fastapi import APIRouter, Query, Depends, HTTPException, Cookie
from fastapi_pagination import LimitOffsetPage, LimitOffsetParams
from fastapi_pagination.ext.sqlalchemy import paginate
from fastapi_users import jwt
from jwt import exceptions as jwt_exceptions
from sqlalchemy import select, desc
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload
from starlette.websockets import WebSocket, WebSocketDisconnect

from config import get_settings
from controllers.user_controller import current_active_user
from db import get_async_session, Chat, Message, User
from routers.chat import create_chat_with_interlocutor
from routers.shemas import MessageReadShort, MessageReadUserShort, MessageReadShortChat
import logging


class ConnectionManager:
    def __init__(self):
        self.active_connections: dict[int, WebSocket] = {}

    async def connect(self, user_id: int, websocket: WebSocket):
        await websocket.accept()

        self.active_connections[user_id] = websocket

    def disconnect(self, user_id: int):
        if user_id in self.active_connections:
            del self.active_connections[user_id]

    async def send(self, user_id: int, message_data: Message):
        connection = self.active_connections.get(user_id)

        if connection is not None:
            await connection.send_text(MessageReadShortChat.from_orm(message_data).json())

    def include(self, user_id: int):
        return user_id in self.active_connections


router = APIRouter(
    prefix="/message",
    tags=["message"],
)

connections = ConnectionManager()


async def send_message_to_chat(chat: Chat, interlocutor: User, message_content: str, current: User,
                               session: AsyncSession) -> Message:
    message_content = message_content.strip()

    if not message_content:
        raise HTTPException(400, detail='empty message')

    if not (current.is_superuser or current in chat.users):
        raise HTTPException(403, detail='not enough permissions')

    message = Message(content=message_content, chat_id=chat.id, author_id=current.id)

    session.add(message)
    await session.commit()
    await session.refresh(message)

    chat.updated_at = message.created_at
    await session.commit()

    await connections.send(interlocutor.id, message)

    return message


@router.post('/user/{user_id}', response_model=MessageReadShort)
async def post_message_to_user(user_id: int, message: str = Query(min_length=1, max_length=280),
                               current=Depends(current_active_user), session=Depends(get_async_session)):
    interlocutor = await session.get(User, user_id)

    if interlocutor is None:
        raise HTTPException(404, detail=f'no user with id {user_id}')

    request = select(Chat).join(Chat.users).where(Chat.users.contains(interlocutor), Chat.users.contains(current))

    chat = (await session.execute(request)).scalars().first()

    message = (await create_chat_with_interlocutor(interlocutor, message, current, session))[1] \
        if chat is None else (await send_message_to_chat(chat, interlocutor, message, current, session))

    return MessageReadShort.from_orm(message)


@router.post('/chat/{chat_id}', response_model=MessageReadShort)
async def post_message_to_chat(chat_id: int, message: str = Query(min_length=1, max_length=280),
                               current=Depends(current_active_user), session=Depends(get_async_session)):
    chat = await session.get(Chat, chat_id, options=(selectinload(Chat.users),))

    if chat is None:
        raise HTTPException(404, detail=f'no chat with id {chat_id}')

    interlocutor = next(filter(lambda user: user != current, chat.users))

    return MessageReadShort.from_orm(await send_message_to_chat(chat, interlocutor, message, current, session))


@router.get('/chat/{chat_id}', response_model=LimitOffsetPage[MessageReadUserShort])
async def get_message_from_chat(chat_id: int,
                                limit: int = Query(default=50, lt=101, gt=0),
                                offset: int = Query(default=0, gt=-1),
                                current=Depends(current_active_user),
                                session=Depends(get_async_session)):
    chat = await session.get(Chat, chat_id, options=(selectinload(Chat.users),))

    if chat is None:
        raise HTTPException(404, detail=f'no chat with id {chat_id}')

    if not (current.is_superuser or current in chat.users):
        raise HTTPException(403, detail='not enough permissions')

    request = select(Message).where(Message.chat_id == chat_id).order_by(desc(Message.created_at))

    return await paginate(
        session,
        request,
        params=LimitOffsetParams(limit=limit, offset=offset),
    )


@router.websocket("/connect")
async def websocket_endpoint(websocket: WebSocket, access_token=Cookie(...),
                             session: AsyncSession = Depends(get_async_session)):
    async def get_current_user() -> User | None:
        try:
            data = jwt.decode_jwt(access_token, get_settings().SECRET, audience='fastapi-users:auth')
        except jwt_exceptions.DecodeError:
            return None

        return await session.get(User, int(data['sub']))

    current_user: User | None = await get_current_user()

    if current_user is None:
        return

    await connections.connect(current_user.id, websocket)

    try:
        while True:
            await websocket.receive_text()
    except WebSocketDisconnect:
        connections.disconnect(current_user.id)
