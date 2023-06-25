from fastapi import APIRouter

router = APIRouter(
    prefix="/message",
    tags=["message"],
)