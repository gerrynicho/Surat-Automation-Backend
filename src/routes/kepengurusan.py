from typing import Annotated

from fastapi import APIRouter, File, Form, UploadFile

from src.services import kepengurusan as kepengurusan_service

router = APIRouter(prefix="/kepengurusan", tags=["kepengurusan"])


@router.get("")
async def get_kepengurusan_list():
    return await kepengurusan_service.get_kepengurusan_list()


@router.get("/detail")
async def get_kepengurusan_detail(nama: str):
    """Ketua settings and current images of one kepengurusan."""
    return await kepengurusan_service.get_kepengurusan_detail(nama)


@router.post("")
async def save_kepengurusan(
    nama: Annotated[str, Form()],
    jabatan: Annotated[str, Form()],
    ketua_nama: Annotated[str, Form()],
    ketua_nrp: Annotated[str, Form()],
    is_new: Annotated[bool, Form()] = False,
    ttd: Annotated[UploadFile | None, File()] = None,
    header: Annotated[UploadFile | None, File()] = None,
    footer: Annotated[UploadFile | None, File()] = None,
    stempel: Annotated[UploadFile | None, File()] = None,
):
    """Create a kepengurusan (is_new=true) or update an existing one.

    Images are optional on update: only the ones sent are replaced.
    """
    return await kepengurusan_service.save_kepengurusan(
        nama=nama,
        jabatan=jabatan,
        ketua_nama=ketua_nama,
        ketua_nrp=ketua_nrp,
        is_new=is_new,
        files={"ttd": ttd, "header": header, "footer": footer, "stempel": stempel},
    )
