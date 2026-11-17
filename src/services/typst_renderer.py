"""Compiles backend/typst/surat.typ into a PDF."""

import json

import typst
from fastapi import HTTPException
from starlette.concurrency import run_in_threadpool

from src.repository.asset_cache import TYPST_ROOT

TEMPLATE = TYPST_ROOT / "surat.typ"
FONT_DIR = TYPST_ROOT / "fonts"


def _compile(data: dict) -> bytes:
    # All letter data travels as one JSON string and is read with json() in the
    # template, so user text is never interpreted as Typst markup.
    return typst.compile(
        str(TEMPLATE),
        root=str(TYPST_ROOT),
        font_paths=[str(FONT_DIR)],
        sys_inputs={"data": json.dumps(data, ensure_ascii=False)},
    )


async def render_surat(data: dict) -> bytes:
    try:
        return await run_in_threadpool(_compile, data)
    except Exception as exc:  # typst raises its own error types with the diagnostics as text
        print(f"typst compile failed: {exc}")
        raise HTTPException(status_code=500, detail="Gagal menyusun PDF surat. Hubungi pengelola aplikasi.")
