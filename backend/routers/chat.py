from fastapi import APIRouter, Depends, HTTPException, Query
from fastapi_pagination import LimitOffsetPage, LimitOffsetParams
from fastapi_pagination.ext.sqlalchemy import paginate
from sqlalchemy import select, or_, desc

from controllers.user_controller import current_active_user
from db import get_async_session, Chat, User, Message
from routers.shemas import ChatRead, MessageRead

router = APIRouter(
    prefix="/chat",
    tags=["chat"],
)


@router.post('/user/id/{user}', response_model=ChatRead)
async def create_chat(user: int, message: str = Query(min_length=1, max_length=280),
                      current=Depends(current_active_user), session=Depends(get_async_session)):
    interlocutor = await session.get(User, user)

    if interlocutor is None:
        raise HTTPException(404, detail=f'interlocutor {user} do not exist')

    request = select(Chat).where(
        Chat.first.in_([current.id, interlocutor.id]),
        Chat.second.in_([current.id, interlocutor.id])
    )

    chat = (await session.execute(request)).scalars().first()

    if chat is not None:
        raise HTTPException(400, detail=f'chat already exist')

    chat = Chat(first=current.id, second=interlocutor.id)

    session.add(chat)
    await session.commit()
    await session.refresh(chat)

    message = Message(content=message, chat=chat.id)

    session.add(message)
    await session.commit()
    await session.refresh(message)

    last_message = MessageRead.from_orm(message)

    response = ChatRead(id=chat.id, interlocutor=interlocutor, last_message=last_message)

    return response


@router.post('/user/{username}', response_model=ChatRead)
async def create_chat_by_username(username: str, message: str = Query(min_length=1, max_length=280),
                                  current=Depends(current_active_user), session=Depends(get_async_session)):
    request = select(User).where(User.username == username)
    interlocutor = (await session.execute(request)).scalars().first()

    if interlocutor is None:
        raise HTTPException(404, detail=f'user {username} do not exist')

    return await create_chat(interlocutor.id, message, current, session)


@router.get('/id/{chat_id}', response_model=ChatRead)
async def get_chat_by_id(chat_id: int, current=Depends(current_active_user), session=Depends(get_async_session)):
    chat = await session.get(Chat, chat_id)

    if chat is None:
        raise HTTPException(404, f'chat {chat_id} do not exist')

    if not current.is_superuser and current.id not in (chat.first, chat.second):
        raise HTTPException(403, 'not enough permissions')

    interlocutor_id = chat.first if chat.first != current.id else chat.second

    interlocutor = await session.get(User, interlocutor_id)

    if interlocutor is None:
        raise HTTPException(404, f'interlocutor with id {interlocutor} do not exist')

    return ChatRead(id=chat.id, interlocutor=interlocutor, last_message=chat.messages[-1])


@router.get('/user/id/{user}', response_model=ChatRead)
async def get_chat(user: int, current=Depends(current_active_user), session=Depends(get_async_session)):
    request = select(Chat).where(
        Chat.first.in_([current.id, user]),
        Chat.second.in_([current.id, user])
    )

    chat = (await session.execute(request)).scalars().first()

    if chat is None:
        raise HTTPException(404, detail=f'chat with interlocutor {user} do not exist')

    return await get_chat_by_id(chat.id, current, session)


@router.get('/user/{username}', response_model=ChatRead)
async def get_chat_by_username(username: str, current=Depends(current_active_user), session=Depends(get_async_session)):
    request = select(User).where(User.username == username)

    interlocutor = (await session.execute(request)).scalars().first()

    if interlocutor is None:
        raise HTTPException(404, detail=f'user {username} do not exist')

    return await get_chat(interlocutor.id, current, session)


@router.get('/all', response_model=LimitOffsetPage)
async def get_chats(limit: int = Query(default=50, lt=101, gt=0),
                    offset: int = Query(default=0, gt=-1),
                    current=Depends(current_active_user),
                    session=Depends(get_async_session)):
    async def get_interlocutor(_interlocutor_id):
        _interlocutor = await session.get(User, _interlocutor_id)

        if _interlocutor is None:
            raise HTTPException(404, f'interlocutor with id {_interlocutor} do not exist')

        return _interlocutor

    request = select(Chat).where(
        or_(Chat.first == current.id, Chat.second == current.id)).join(
        Chat.messages
    ).order_by(desc(Message.created_at))

    data = await paginate(
        session,
        request,
        params=LimitOffsetParams(limit=limit, offset=offset),
    )

    new_items = []
    for obj in data.items:
        interlocutor_id = obj.first if obj.first != current.id else obj.second
        try:
            interlocutor = await get_interlocutor(interlocutor_id)
        except HTTPException:
            continue

        new_items += [ChatRead(id=obj.id, last_message=obj.messages[-1], interlocutor=interlocutor)]

    data.items = new_items

    return data
