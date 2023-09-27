from fastapi import APIRouter, Depends, HTTPException, Query
from fastapi_pagination import LimitOffsetPage, LimitOffsetParams
from fastapi_pagination.ext.sqlalchemy import paginate
from sqlalchemy import select, desc
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from controllers.user_controller import current_active_user
from db import get_async_session, Chat, User, Message, UserToChat
from routers.shemas import ChatRead, MessageRead, UserReadShort

router = APIRouter(
    prefix="/chat",
    tags=["chat"],
)


async def create_chat_with_interlocutor(interlocutor: User, message: str, current: User, session: AsyncSession):
    request = select(Chat).join(Chat.users).where(Chat.users.contains(interlocutor), Chat.users.contains(current))

    chat = (await session.execute(request)).scalars().first()

    if chat is not None:
        raise HTTPException(400, detail='chat already exist')

    message = message.strip()

    if not message:
        raise HTTPException(400, detail='empty message')

    chat = Chat()

    session.add(chat)
    await session.commit()
    await session.refresh(chat)

    for user in (current, interlocutor):
        connection = UserToChat(user=user.id, chat=chat.id)
        session.add(connection)

    await session.commit()

    message = Message(content=message, chat_id=chat.id, author_id=current.id)

    session.add(message)
    await session.commit()
    await session.refresh(message)

    return chat, message


@router.post('/user/id/{user}', response_model=ChatRead)
async def create_chat(user: int, message: str = Query(min_length=1, max_length=280),
                      current=Depends(current_active_user), session=Depends(get_async_session)):
    interlocutor = await session.get(User, user)

    if interlocutor is None:
        raise HTTPException(404, detail=f'interlocutor {user} do not exist')

    chat, message = await create_chat_with_interlocutor(interlocutor, message, current, session)

    last_message = MessageRead.from_orm(message)

    return ChatRead(id=chat.id, interlocutor=interlocutor, last_message=last_message)


@router.post('/user/{username}', response_model=ChatRead)
async def create_chat_by_username(username: str, message: str = Query(min_length=1, max_length=280),
                                  current=Depends(current_active_user), session=Depends(get_async_session)):
    request = select(User).where(User.username == username)
    interlocutor = (await session.execute(request)).scalars().first()

    if interlocutor is None:
        raise HTTPException(404, detail=f'user {username} do not exist')

    chat, message = await create_chat_with_interlocutor(interlocutor, message, current, session)

    last_message = MessageRead.from_orm(message)

    return ChatRead(id=chat.id, interlocutor=interlocutor, last_message=last_message)


async def get_chat_by_chat_model(chat: Chat, current: User, interlocutor=None):
    if not (current.is_superuser or current in chat.users):
        raise HTTPException(403, 'not enough permissions')
    
    if interlocutor is None:
        interlocutor = chat.users[0] if chat.users[0] != current else chat.users[1]
    
        if interlocutor is None:
            raise HTTPException(404, f'interlocutor do not exist')

    return ChatRead(id=chat.id, interlocutor=interlocutor, last_message=chat.messages[-1])


@router.get('/id/{chat_id}', response_model=ChatRead)
async def get_chat_by_id(chat_id: int, current=Depends(current_active_user), session=Depends(get_async_session)):
    chat = await session.get(Chat, chat_id, options=(selectinload(Chat.users), ))

    if chat is None:
        raise HTTPException(404, f'chat {chat_id} do not exist')

    return await get_chat_by_chat_model(chat, current)


async def get_chat_by_interlocutor(interlocutor: User, current: User, session: AsyncSession):
    request = select(Chat).join(Chat.users).where(Chat.users.contains(interlocutor), Chat.users.contains(current))

    chat = (await session.execute(request)).scalars().first()

    if chat is None:
        raise HTTPException(404, detail=f'chat with interlocutor {interlocutor.id} do not exist')

    return await get_chat_by_chat_model(chat, current, interlocutor=interlocutor)


@router.get('/user/id/{user}', response_model=ChatRead)
async def get_chat(user: int, current=Depends(current_active_user), session=Depends(get_async_session)):
    interlocutor = await session.get(User, user)

    if interlocutor is None:
        raise HTTPException(404, detail=f'interlocutor with id {user} do not exist')

    return await get_chat_by_interlocutor(interlocutor, current, session)


@router.get('/user/{username}', response_model=ChatRead)
async def get_chat_by_username(username: str, current=Depends(current_active_user), session=Depends(get_async_session)):
    request = select(User).where(User.username == username)

    interlocutor = (await session.execute(request)).scalars().first()

    if interlocutor is None:
        raise HTTPException(404, detail=f'user {username} do not exist')

    return await get_chat_by_interlocutor(interlocutor, current, session)


@router.get('/all', response_model=LimitOffsetPage)
async def get_chats(limit: int = Query(default=50, lt=101, gt=0),
                    offset: int = Query(default=0, gt=-1),
                    current=Depends(current_active_user),
                    session=Depends(get_async_session)):
    request = select(Chat).where(Chat.users.contains(current)).order_by(desc(Chat.updated_at)).options(
        selectinload(Chat.users), selectinload(Chat.messages, Message.author))

    data: LimitOffsetPage = await paginate(
        session,
        request,
        params=LimitOffsetParams(limit=limit, offset=offset),
    )

    new_items = []
    for chat_model in data.items:
        interlocutor = chat_model.users[0] if chat_model.users[0] != current else chat_model.users[1]
        new_items.append(ChatRead(id=chat_model.id, interlocutor=interlocutor, last_message=chat_model.messages[-1]))

    data.items = new_items

    return data


@router.get('/to_create_with/{username}', response_model=LimitOffsetPage[UserReadShort])
async def get_chats(username: str,
                    limit: int = Query(default=50, lt=101, gt=0),
                    offset: int = Query(default=0, gt=-1),
                    current: User = Depends(current_active_user),
                    session: AsyncSession = Depends(get_async_session)):
    request = select(User).where(
        User.id != current.id, User.username.regexp_match(f'(\\S*){username}(\\S*)', flags='i'),
        ~User.chats.any(Chat.users.any(id=current.id))
    )

    data = await paginate(
        session,
        request,
        params=LimitOffsetParams(limit=limit, offset=offset),
    )

    return data
