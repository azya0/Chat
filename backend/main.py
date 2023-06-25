import uvicorn
from fastapi import FastAPI
from fastapi_pagination import add_pagination
from fastapi.middleware.cors import CORSMiddleware

from config import get_settings
from controllers.user_controller import fastapi_users, auth_backend
from routers.shemas import UserRead, UserCreate, UserUpdate
from routers.__all__ import __all__ as routers


def get_application(_settings):
    application = FastAPI(
        title=_settings.PROJECT_NAME,
        version=_settings.VERSION,
        debug=_settings.DEBUG,
    )

    origins = ['*']

    application.add_middleware(
        CORSMiddleware,
        allow_origins=origins,
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    application.include_router(
        fastapi_users.get_register_router(UserRead, UserCreate),
        prefix="/auth",
        tags=["auth"],
    )

    application.include_router(
        fastapi_users.get_auth_router(auth_backend),
        prefix="/auth/jwt",
        tags=["auth"],
    )

    application.include_router(
        fastapi_users.get_users_router(UserRead, UserUpdate),
        prefix="/users",
        tags=["users"],
    )

    for router in routers:
        application.include_router(router)

    add_pagination(application)

    return application


app = get_application(get_settings())
