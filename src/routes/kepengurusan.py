from fastapi import APIRouter

from src.services import kepengurusan as kepengurusan_service

router = APIRouter(prefix="/kepengurusan", tags=["kepengurusan"])


@router.get("")
async def get_kepengurusan_list():
    return await kepengurusan_service.get_kepengurusan_list()
