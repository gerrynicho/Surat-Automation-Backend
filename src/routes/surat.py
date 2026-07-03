from fastapi import APIRouter

from src.schema.surat import CreateSuratRequest, FileActionRequest
from src.services import surat as surat_service

router = APIRouter(prefix="/surat", tags=["surat"])


@router.get("/latest")
async def get_latest_nomor_surat(nama_kepengurusan: str):
    return await surat_service.get_latest_nomor_surat(nama_kepengurusan)


@router.post("/create")
async def create_surat(body: CreateSuratRequest):
    return await surat_service.create_surat(body)


@router.post("/update-database")
async def update_database(body: CreateSuratRequest):
    return await surat_service.update_database(body)


@router.post("/export-pdf")
async def export_pdf(body: FileActionRequest):
    return await surat_service.export_pdf(body)
