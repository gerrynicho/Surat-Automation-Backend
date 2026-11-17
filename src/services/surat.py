import base64

from fastapi import HTTPException

from src.repository import asset_cache, gas_client
from src.schema.surat import CreateSuratRequest
from src.services.typst_renderer import render_surat

KELOLA_HINT = "Lengkapi di halaman Kelola Kepengurusan."


async def get_latest_nomor_surat(nama_kepengurusan: str) -> dict:
    return await gas_client._get("getLatestNomorSurat", {"nama_kepengurusan": nama_kepengurusan})


async def update_database(body: CreateSuratRequest) -> dict:
    return await gas_client._post("updateDatabase", body.model_dump())


async def _prepare(body: CreateSuratRequest) -> dict:
    """Predicted next nomor surat, Ketua config and image list, in one GAS call."""
    return await gas_client._get(
        "prepareSurat",
        {"nama_kepengurusan": body.nama_kepengurusan, "kode": body.metadata.kode},
    )


def _check(prep: dict) -> tuple[list[str], bool]:
    """Human-readable warnings, and whether any of them must block finalize."""
    config = prep.get("config") or {}
    assets = prep.get("assets") or {}
    blocking: list[str] = []
    if not all(config.get(k) for k in ("jabatan", "ketua_nama", "ketua_nrp")):
        blocking.append("Data Ketua (jabatan, nama, NRP) belum lengkap.")
    if not assets.get("ttd"):
        blocking.append("Tanda tangan Ketua belum diunggah.")
    if not assets.get("stempel"):
        blocking.append("Stempel belum diunggah.")

    notes: list[str] = []
    if not assets.get("header"):
        notes.append("Kop surat (header) belum diunggah, jadi surat dibuat tanpa kop.")
    return blocking + notes, bool(blocking)


def _template_data(body: CreateSuratRequest, nomor_surat: str, prep: dict, images: dict) -> dict:
    config = prep.get("config") or {}
    return {
        "tanggal": body.metadata.tanggal_pengajuan,
        "nomor_surat": nomor_surat,
        "tujuan": body.data.TUJUAN,
        "its": body.data.ITSORNO,
        "nama_kegiatan": body.data.NAMAKEGIATAN,
        "hari_tanggal": body.data.HARITANGGAL,
        "acara": body.data.ACARAYANGMINTAIZIN,
        "participants": [p.model_dump() for p in body.participants],
        "ketua": {
            "jabatan": config.get("jabatan") or "",
            "nama": config.get("ketua_nama") or "",
            "nrp": config.get("ketua_nrp") or "",
        },
        "assets": {slot: asset_cache.typst_path(path) for slot, path in images.items()},
    }


async def preview(body: CreateSuratRequest) -> dict:
    """Compile the letter with the predicted number. Nothing is saved anywhere."""
    prep = await _prepare(body)
    images = await asset_cache.resolve(prep.get("assets") or {})
    nomor_surat = prep["next_nomor_surat"]
    pdf = await render_surat(_template_data(body, nomor_surat, prep, images))
    warnings, blocked = _check(prep)
    return {
        "nomor_surat": nomor_surat,
        "pdf_base64": base64.b64encode(pdf).decode("ascii"),
        "warnings": warnings,
        "blocked": blocked,
    }


async def finalize(body: CreateSuratRequest) -> dict:
    """Register the nomor surat, compile the final PDF and store it in Berkas Keluar."""
    prep = await _prepare(body)
    warnings, blocked = _check(prep)
    if blocked:
        raise HTTPException(status_code=409, detail=" ".join(warnings) + " " + KELOLA_HINT)

    # Everything that can fail without side effects runs before the number is
    # registered, so a broken image or template never burns a nomor surat.
    images = await asset_cache.resolve(prep.get("assets") or {})
    await render_surat(_template_data(body, prep["next_nomor_surat"], prep, images))

    registered = await gas_client._post("updateDatabase", body.model_dump())
    nomor_surat = registered["nomor_surat"]
    pdf = await render_surat(_template_data(body, nomor_surat, prep, images))

    try:
        uploaded = await gas_client._post(
            "uploadPDF",
            {
                "nama_kepengurusan": body.nama_kepengurusan,
                "file_name": body.new_name,
                "pdf_base64": base64.b64encode(pdf).decode("ascii"),
            },
        )
    except Exception as exc:
        reason = exc.detail if isinstance(exc, HTTPException) else str(exc)
        raise HTTPException(
            status_code=502,
            detail=(
                f"Nomor surat {nomor_surat} sudah tercatat di spreadsheet, "
                f"tetapi PDF gagal disimpan ke Google Drive ({reason}). "
                "Hapus baris itu di spreadsheet sebelum mencoba lagi."
            ),
        )

    return {
        "success": True,
        "nomor_surat": nomor_surat,
        "file_name": uploaded["file_name"],
        "url": uploaded["url"],
    }
