"""Local cache of the images kept in the Drive Assets folder.

Typst can only read files under its root, so images are downloaded once through
GAS and stored in backend/typst/.cache. The cache key includes the Drive file id
and its last-updated time, so replacing an image in Drive is picked up on the
next letter without restarting the backend.
"""

import asyncio
import base64
import os
import re
from pathlib import Path

from fastapi import HTTPException

from src.repository import gas_client

TYPST_ROOT = Path(__file__).resolve().parents[2] / "typst"
CACHE_DIR = TYPST_ROOT / ".cache"

SLOTS = ("header", "footer", "stempel", "ttd")
_EXT_BY_MIME = {"image/png": ".png", "image/jpeg": ".jpg"}
_SAFE_ID = re.compile(r"^[A-Za-z0-9_-]+$")


def _cache_path(asset: dict) -> Path:
    file_id = str(asset.get("id", ""))
    ext = _EXT_BY_MIME.get(str(asset.get("mime", "")))
    if not _SAFE_ID.match(file_id) or ext is None:
        raise HTTPException(status_code=502, detail="GAS mengembalikan data gambar yang tidak valid")
    updated = re.sub(r"\D", "", str(asset.get("updated", ""))) or "0"
    return CACHE_DIR / f"{file_id}-{updated}{ext}"


async def ensure_local(asset: dict) -> Path:
    """Return the local path of a Drive image, downloading it if needed."""
    path = _cache_path(asset)
    if path.exists():
        return path

    result = await gas_client._get("getAssetFile", {"file_id": asset["id"]})
    try:
        content = base64.b64decode(result["data_base64"], validate=True)
    except (KeyError, ValueError):
        raise HTTPException(status_code=502, detail="Gambar dari Drive tidak bisa dibaca")

    CACHE_DIR.mkdir(parents=True, exist_ok=True)
    tmp = path.with_name(path.name + f".{os.getpid()}.tmp")
    tmp.write_bytes(content)
    tmp.replace(path)  # atomic: a concurrent compile never sees a half-written file
    return path


async def resolve(assets: dict) -> dict[str, Path | None]:
    """Download every image listed by GAS. Slots that are not set map to None."""
    present = [slot for slot in SLOTS if assets.get(slot)]
    paths = await asyncio.gather(*(ensure_local(assets[slot]) for slot in present))
    resolved: dict[str, Path | None] = {slot: None for slot in SLOTS}
    resolved.update(zip(present, paths))
    return resolved


def typst_path(path: Path | None) -> str | None:
    """Path as the Typst template expects it: relative to backend/typst."""
    return None if path is None else path.relative_to(TYPST_ROOT).as_posix()
