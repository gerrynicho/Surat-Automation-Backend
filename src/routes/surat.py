from fastapi import APIRouter

from src.schema.surat import CreateSuratRequest, FinalizeSuratResponse, PreviewSuratResponse
from src.services import surat as surat_service

router = APIRouter(prefix="/surat", tags=["surat"])


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
