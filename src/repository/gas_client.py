import httpx
from fastapi import HTTPException

from config import settings

TIMEOUT = 60.0


async def _get(route: str, params: dict = {}) -> dict:
    async with httpx.AsyncClient(timeout=TIMEOUT, follow_redirects=True) as client:
        r = await client.get(
            settings.gas_url,
            params={"route": route, "api_key": settings.gas_api_key, **params},
        )
        r.raise_for_status()
    return _unwrap(r.json())


async def _post(route: str, payload: dict) -> dict:
    async with httpx.AsyncClient(timeout=TIMEOUT, follow_redirects=True) as client:
        r = await client.post(
            settings.gas_url,
            params={"route": route, "api_key": settings.gas_api_key},
            json=payload,
        )
        r.raise_for_status()
    return _unwrap(r.json())


def _unwrap(body: dict) -> dict:
    """Translate GAS envelope { code, response } into a plain dict or raise HTTPException."""
    code: int = body.get("code", 200)
    response = body.get("response", {})
    if code != 200:
        detail = response.get("error", "GAS server error") if isinstance(response, dict) else str(response)
        raise HTTPException(status_code=code, detail=detail)
    return response
