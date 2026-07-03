from src.repository import gas_client
from src.schema.surat import CreateSuratRequest, FileActionRequest


async def get_latest_nomor_surat(nama_kepengurusan: str) -> dict:
    return await gas_client._get("getLatestNomorSurat", {"nama_kepengurusan": nama_kepengurusan})


async def create_surat(body: CreateSuratRequest) -> dict:
    return await gas_client._post("createSurat", body.model_dump())


async def update_database(body: CreateSuratRequest) -> dict:
    return await gas_client._post("updateDatabase", body.model_dump())


async def export_pdf(body: FileActionRequest) -> dict:
    return await gas_client._post("exportPDF", body.model_dump())
