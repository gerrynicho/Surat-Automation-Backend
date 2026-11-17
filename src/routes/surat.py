from typing import Annotated

from fastapi import APIRouter, Path

from src.schema.surat import (
    CreateSuratRequest,
    DeleteSuratResponse,
    FinalizeSuratResponse,
    PreviewSuratResponse,
    SuratDetailResponse,
    SuratListResponse,
)
from src.services import surat as surat_service

router = APIRouter(prefix="/surat", tags=["surat"])

# Running number of a letter: column NO. of the arsip sheet.
Nomor = Annotated[int, Path(ge=1)]


@router.get("", response_model=SuratListResponse)
async def list_surat(nama_kepengurusan: str):
    """Every letter in the arsip of a kepengurusan, newest first."""
    return await surat_service.list_surat(nama_kepengurusan)


# Declared before "/{nomor}" so "latest" is not read as a number.
@router.get("/latest")
async def get_latest_nomor_surat(nama_kepengurusan: str):
    return await surat_service.get_latest_nomor_surat(nama_kepengurusan)


@router.post("/preview", response_model=PreviewSuratResponse)
async def preview_surat(body: CreateSuratRequest):
    """Render the letter as a PDF for review. Does not touch the spreadsheet."""
    return await surat_service.preview(body)


@router.post("/finalize", response_model=FinalizeSuratResponse)
async def finalize_surat(body: CreateSuratRequest):
    """Register the nomor surat and save the final PDF to Berkas Keluar."""
    return await surat_service.finalize(body)


@router.post("/update-database")
async def update_database(body: CreateSuratRequest):
    return await surat_service.update_database(body)


@router.get("/{nomor}", response_model=SuratDetailResponse)
async def get_surat(nomor: Nomor, nama_kepengurusan: str):
    """One letter: its arsip row, the data it was built from and its PDF."""
    return await surat_service.get_surat(nama_kepengurusan, nomor)


@router.post("/{nomor}/preview", response_model=PreviewSuratResponse)
async def preview_surat_edit(nomor: Nomor, body: CreateSuratRequest):
    """Render an edited letter with the number it already has. Saves nothing."""
    return await surat_service.preview(body, nomor)


@router.put("/{nomor}", response_model=FinalizeSuratResponse)
async def update_surat(nomor: Nomor, body: CreateSuratRequest):
    """Replace an existing letter. The running number stays; the PDF and the arsip row change."""
    return await surat_service.update(nomor, body)


@router.delete("/{nomor}", response_model=DeleteSuratResponse)
async def delete_surat(nomor: Nomor, nama_kepengurusan: str):
    """Delete a letter. The latest one frees its number; older ones are marked as cancelled."""
    return await surat_service.delete(nama_kepengurusan, nomor)
