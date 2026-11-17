import base64

from fastapi import HTTPException, UploadFile

from src.repository import asset_cache, gas_client

MAX_IMAGE_BYTES = 4 * 1024 * 1024
IMAGE_LABELS = {
    "ttd": "Tanda tangan",
    "header": "Kop surat (header)",
    "footer": "Footer",
    "stempel": "Stempel",
}


async def get_kepengurusan_list() -> dict:
    return await gas_client._get("getKepengurusanList")


async def get_kepengurusan_detail(nama: str) -> dict:
    """Ketua settings plus a thumbnail of every image currently in use."""
    info = await gas_client._get("getKepengurusan", {"nama_kepengurusan": nama})
    assets = info.get("assets") or {}
    paths = await asset_cache.resolve(assets)

    images = {}
    for slot, path in paths.items():
        if path is None:
            images[slot] = None
            continue
        mime = assets[slot]["mime"]
        encoded = base64.b64encode(path.read_bytes()).decode("ascii")
        images[slot] = {
            # "own" = set for this kepengurusan, "default" = shared fallback
            "source": assets[slot].get("source", "own"),
            "data_url": f"data:{mime};base64,{encoded}",
        }

    return {"nama": info.get("nama", nama), "config": info.get("config"), "images": images}


def _sniff_mime(content: bytes) -> str | None:
    if content.startswith(b"\x89PNG\r\n\x1a\n"):
        return "image/png"
    if content.startswith(b"\xff\xd8\xff"):
        return "image/jpeg"
    return None


async def _read_image(slot: str, file: UploadFile | None) -> dict | None:
    if file is None:
        return None
    content = await file.read()
    if not content:
        return None
    label = IMAGE_LABELS[slot]
    if len(content) > MAX_IMAGE_BYTES:
        raise HTTPException(status_code=400, detail=f"{label}: ukuran gambar maksimal 4 MB.")
    # Checked from the file content itself, not the file name or browser header.
    mime = _sniff_mime(content)
    if mime is None:
        raise HTTPException(status_code=400, detail=f"{label}: gambar harus berformat PNG atau JPG.")
    return {"mime": mime, "data_base64": base64.b64encode(content).decode("ascii")}


async def save_kepengurusan(
    *,
    nama: str,
    jabatan: str,
    ketua_nama: str,
    ketua_nrp: str,
    is_new: bool,
    files: dict[str, UploadFile | None],
) -> dict:
    fields = {
        "Nama kepengurusan": nama.strip(),
        "Jabatan": jabatan.strip(),
        "Nama Ketua": ketua_nama.strip(),
        "NRP Ketua": ketua_nrp.strip(),
    }
    for label, value in fields.items():
        if not value:
            raise HTTPException(status_code=400, detail=f"{label} wajib diisi.")

    images = {}
    for slot in IMAGE_LABELS:
        image = await _read_image(slot, files.get(slot))
        if image is not None:
            images[slot] = image

    if is_new and "ttd" not in images:
        raise HTTPException(status_code=400, detail="Tanda tangan Ketua wajib diunggah untuk kepengurusan baru.")

    return await gas_client._post(
        "saveKepengurusan",
        {
            "nama": fields["Nama kepengurusan"],
            "jabatan": fields["Jabatan"],
            "ketua_nama": fields["Nama Ketua"],
            "ketua_nrp": fields["NRP Ketua"],
            "is_new": is_new,
            "images": images,
        },
    )
